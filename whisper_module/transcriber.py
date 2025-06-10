# transcriber.py
from resemblyzer import VoiceEncoder, preprocess_wav
from whisper_module.speaker_identifier import SpeakerIdentifier
from faster_whisper import WhisperModel
from typing import List, Dict, Any
from pydub import AudioSegment
import torch, os, time
from Hugging_Face.HuggingFaceUtil import HuggingFaceUtil
from Utils.ffmpeg_util import ffmpeg_ensure_wav, split_audio_to_chunks

class Transcribe:
    def __init__(self):
        self.model_name = "base"
        self.model = None
        self.speaker_identifier = SpeakerIdentifier()

    def execute(
        self,
        audio_path: str,
        chunk_length_s: int = 300
    ) -> List[Dict[str, Any]]:
        # 1) GPU 캐시 비우기
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # 2) WhisperModel 로드
        self.model, device = self._load_whisper(self.model_name)

        # 3) WAV 보장 후 샘플레이트와 채널 보정
        audio_path = ffmpeg_ensure_wav(audio_path)
        # 모든 오디오를 16kHz mono WAV로 변환
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(audio_path, format="wav")

        # 4) 청크 분할
        chunk_paths = split_audio_to_chunks(audio_path, chunk_length_s)
        if not chunk_paths:
            raise ValueError("Audio splitting resulted in no chunks.")

        # 5) Resemblyzer DB 초기화
        encoder = VoiceEncoder(device="cpu")
        self.speaker_identifier.init_speaker_db(encoder)

        final_results: List[Dict[str, Any]] = []
        offset_s = 0.0

        for idx, chunk in enumerate(chunk_paths, start=1):
            # GPU 캐시 클리어
            if device == "cuda":
                torch.cuda.empty_cache()
            start_time = time.time()

            segments, _ = self.model.transcribe(chunk)
            segments = list(segments)
            if not segments:
                offset_s += AudioSegment.from_file(chunk).duration_seconds
                continue

            for seg in segments:
                st, ed, txt = seg.start, seg.end, seg.text
                # 전체 청크 오디오도 16kHz mono로 보장 후 슬라이싱
                wav = preprocess_wav(chunk)
                sr = 16000
                start_sample = int(st * sr)
                end_sample   = int(ed * sr)
                segment_wav  = wav[start_sample:end_sample]
                if len(segment_wav) < 0.3 * sr:
                    continue
                emb  = encoder.embed_utterance(segment_wav)
                name = self.speaker_identifier.execute(emb)
                final_results.append({
                    "speaker": name,
                    "start":   st + offset_s,
                    "end":     ed + offset_s,
                    "text":    txt.strip()
                })

            # offset 증가 및 처리 시간 로깅
            offset_s += AudioSegment.from_file(chunk).duration_seconds
            elapsed = time.time() - start_time
            print(f"Chunk {idx} 처리 완료, 시간: {elapsed:.2f}s")

        # 6) 임시 파일 정리
        os.remove(audio_path)
        for p in chunk_paths:
            try: os.remove(p)
            except: pass
        try: os.rmdir("tmp_chunks")
        except: pass

        return final_results

    def _load_whisper(self, size: str):
        # GPU 우선 로드
        if torch.cuda.is_available():
            for comp in ("float16", "int8"):
                try:
                    return WhisperModel(size, device="cuda", compute_type=comp), "cuda"
                except:
                    continue
        # CPU fallback
        return WhisperModel(size, device="cpu", compute_type="int8"), "cpu"

if __name__ == "__main__":
    trans = Transcribe()
    out = trans.execute("meeting.wav", chunk_length_s=300)
    with open("transcript.txt", "w", encoding="utf-8") as f:
        for s in out:
            f.write(f"[{s['speaker']}] {s['text']}\n")
    print("✅ transcript.txt 작성 완료")
