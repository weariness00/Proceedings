from tkinter import messagebox
from exceptiongroup import catch
from resemblyzer import VoiceEncoder
from sklearn.cluster import KMeans
from whisper_module.speaker_identifier import get_speaker_db, identify_by_embedding
from typing import List, Dict, Any
import os
import math
import torch
import torchaudio
from pydub import AudioSegment
from faster_whisper import WhisperModel

SPEAKER_DB = "speaker_db"

class Transcribe:
    def __init__(self):
        self.model_name = "base"
        self.speaker_count = 2
        self.model = None
        pass

    def execute(self,
               audio_path: str,
               chunk_length_s: int = 300
               ) -> List[Dict[str, Any]]:
        """
           긴 오디오(audio_path)를 chunk_length_s(초) 단위로 나눈 뒤,
           각 chunk마다 전사→임베딩→KMeans→화자 식별을 수행하고,
           전체 결과를 합쳐 리턴합니다.
           """

        # 1) GPU 메모리 캐시 비우기
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # 2) WhisperModel 로드 (GPU → CPU 자동 fallback)
        self.model, device = load_whisper_model(self.model_name)
        model = self.model

        # 3) 오디오를 chunk 단위로 분리한 파일 경로 리스트 얻기
        chunk_paths = split_audio_to_chunks(audio_path, chunk_length_s)
        if not chunk_paths:
            raise ValueError("Audio splitting resulted in no chunks.")

        print(f"🔀 총 {len(chunk_paths)}개 조각으로 분할: {chunk_paths}")

        # 4) Resemblyzer용 음성 DB와 encoder 준비
        encoder = VoiceEncoder(device="cpu")
        speaker_db = get_speaker_db(encoder)

        # 5) 모든 chunk를 처리하며 최종 결과 누적
        final_results: List[Dict[str, Any]] = []
        offset_s = 0.0  # 이전 chunk까지 누적된 시간(초)

        for idx, chunk_path in enumerate(chunk_paths, start=1):
            print(f"--- Chunk {idx}/{len(chunk_paths)} 전사 시작: {chunk_path} (오프셋 {offset_s}s)")

            # 전사 전 GPU 캐시 비우기
            import gc
            gc.collect()
            if device == "cuda":
                torch.cuda.empty_cache()

            # 5.1) chunk 전사 (로컬 시간)
            segments, _ = model.transcribe(chunk_path)
            segments = list(segments)
            if not segments:
                print(f"--- Chunk {idx}: 전사된 세그먼트 없음, offset만 증가")
                chunk_audio = AudioSegment.from_file(chunk_path)
                offset_s += len(chunk_audio) / 1000.0
                continue

            # 5.2) chunk 파일 로드하여 임베딩 추출 준비
            waveform, sr = torchaudio.load(chunk_path)
            waveform = waveform.mean(dim=0).numpy()

            chunk_embeddings = []
            chunk_segdata = []

            for seg in segments:
                st, ed, txt = seg.start, seg.end, seg.text
                start_frame = int(st * sr)
                end_frame = int(ed * sr)
                segment_wav = waveform[start_frame:end_frame]
                if len(segment_wav) < sr * 0.3:
                    continue
                emb = encoder.embed_utterance(segment_wav)
                chunk_embeddings.append(emb)
                # offset을 더해 전체 기준 시간으로 변환
                chunk_segdata.append({
                    "start": st + offset_s,
                    "end": ed + offset_s,
                    "text": txt
                })

            if not chunk_embeddings:
                print(f"--- Chunk {idx}: 임베딩 추출된 세그먼트 없음, offset만 증가")
                chunk_audio = AudioSegment.from_file(chunk_path)
                offset_s += len(chunk_audio) / 1000.0
                continue

            # 5.3) 이 chunk 내에서만 KMeans 클러스터링
            print(f"--- Chunk {idx}: 🔀 {len(chunk_embeddings)}개 임베딩으로 KMeans({self.speaker_count}) 실행")
            kmeans = KMeans(n_clusters=self.speaker_count, random_state=0).fit(chunk_embeddings)
            labels = kmeans.labels_

            # 5.4) 클러스터 중심별 화자 이름 매핑
            cluster_to_name: Dict[int, str] = {}
            for cidx, center in enumerate(kmeans.cluster_centers_):
                name = identify_by_embedding(center, speaker_db, threshold=0.5)
                cluster_to_name[cidx] = name

            # 5.5) chunk_segdata와 labels를 결합해 최종 결과에 추가
            for seg_info, cidx in zip(chunk_segdata, labels):
                final_results.append({
                    "speaker": cluster_to_name.get(cidx, "Unknown"),
                    "start": seg_info["start"],
                    "end": seg_info["end"],
                    "text": seg_info["text"]
                })

            # 5.6) 이 chunk의 길이만큼 offset 증가
            chunk_audio = AudioSegment.from_file(chunk_path)
            offset_s += len(chunk_audio) / 1000.0

            print(f"--- Chunk {idx} 완료, 누적 세그먼트 수: {len(final_results)}, offset → {offset_s}s")
        print(f"--- Done Transcriber")

        # 6) 임시 chunk 파일 삭제
        print("▶ Cleanup 시작: tmp_chunks 삭제 전")  # (A)
        for p in chunk_paths:
            try:
                os.remove(p)
            except Exception as e:
                print(e)
                pass
        try:
            os.rmdir("tmp_chunks")
        except Exception as e:
            print(e)
            pass
        print("▶ Cleanup: tmp_chunks 삭제 완료")  # (B)

        # 7) GPU 메모리 잡고 있는 객체들을 명시적으로 비우기
        print("▶ Cleanup: GPU 캐시 비우기 전")  # (C)
        try:
            import gc
            gc.collect()
            print("GC Clean")
            torch.cuda.empty_cache()
            print("▶ Cleanup: torch.cuda.empty_cache() 호출 완료")  # (D)
        except Exception as e:
            print(f"Cleanup 중 예외 발생: {e}")
            pass

        print(f"--- GPU Clear")
        print(f"▶ 최종 세그먼트 개수: {len(final_results)}")
        return final_results

def split_audio_to_chunks(input_path: str, chunk_length_s: int = 300) -> list[str]:
    """
    input_path(mp3/wav)을 chunk_length_s(초) 단위로 자르고,
    임시 WAV 파일로 저장한 뒤 파일 경로 리스트를 리턴합니다.
    """
    chunk_paths = []
    try:
        audio = AudioSegment.from_file(input_path)
        total_ms = len(audio)
        chunk_ms = chunk_length_s * 1000

        os.makedirs("tmp_chunks", exist_ok=True)
        for start_ms in range(0, total_ms, chunk_ms):
            end_ms = min(start_ms + chunk_ms, total_ms)
            chunk = audio[start_ms:end_ms]
            if len(chunk) <= 0:
                continue
            start_s = start_ms // 1000
            end_s = math.ceil(end_ms / 1000)
            chunk_name = f"tmp_chunks/chunk_{start_s}_{end_s}.wav"
            chunk.export(chunk_name, format="wav")
            chunk_paths.append(chunk_name)
    except Exception as e:
        print("split_audio_to_chunks 오류:", e)

    # 만약 한 개도 chunk가 생성되지 않았다면, 원본 전체를 하나의 chunk로 간주
    if not chunk_paths:
        try:
            os.makedirs("tmp_chunks", exist_ok=True)
            fallback_name = "tmp_chunks/chunk_0_0.wav"
            audio.export(fallback_name, format="wav")
            chunk_paths.append(fallback_name)
        except Exception as ex:
            print("fallback chunk 생성 실패:", ex)

    return chunk_paths


def load_whisper_model(model_size: str):
    """
    GPU 사용 가능 시 GPU로 WhisperModel을 시도해서 로드하고,
    실패하거나 GPU가 없으면 CPU로 로드하여 반환합니다.
    """
    use_cuda = torch.cuda.is_available()
    if use_cuda:
        for compute in ("float16", "int8"):
            try:
                model = WhisperModel(model_size, device="cuda", compute_type=compute)
                print(f"▶ WhisperModel('{model_size}') loaded on GPU (compute_type={compute})")
                return model, "cuda"
            except Exception as e:
                print(f"⚠ GPU 로드 실패 (compute_type={compute}): {e}")
        print("▶ GPU로 모두 실패, CPU로 전환합니다.")

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print(f"▶ WhisperModel('{model_size}') loaded on CPU")
    return model, "cpu"


if __name__ == "__main__":
    path = "meeting.wav"
    results = transcribe_and_identify(path, model_size="base", num_speakers=2, chunk_length_s=300)
    with open("transcript.txt", "w", encoding="utf-8") as f:
        for seg in results:
            f.write(f"[{seg['speaker']}] {seg['text']}\n")
    print("✅ Written to transcript.txt")
