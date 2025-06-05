import numpy as np
import torchaudio
import torch
from pathlib import Path
from resemblyzer import VoiceEncoder
from sklearn.cluster import KMeans
from faster_whisper import WhisperModel
from whisper_module.speaker_identifier import get_speaker_db, identify_by_embedding
from typing import List, Dict, Any

SPEAKER_DB = "speaker_db"

def transcribe_and_identify(audio_path: str, model_size="base", num_speakers=2) -> List[Dict[str, Any]]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"🧠 model_size: {model_size}")
    print(f"🧠 Using device: {device}")
    print(f"🧠 Using compute_type: {compute_type}")
    # GPU 메모리 사용량 출력 (optional)
    print("CUDA available?:", torch.cuda.is_available())
    if device == "cuda":
        import subprocess, sys
        subprocess.call(["nvidia-smi"], shell=True)
    # 1. faster-whisper로 전사
    print("📄 Transcribing with Faster-Whisper...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _ = model.transcribe(audio_path)
    # 3) 모델 로드 직후 GPU 상태 확인
    if device == "cuda":
        subprocess.call("nvidia-smi", shell=True)

    segments = list(segments)  # generator -> list
    if not segments:
        raise ValueError("No segments found in audio.")

    # 2. 오디오 로드 및 Resemblyzer 임베딩 추출
    print("🔊 Extracting embeddings...")
    waveform, sr = torchaudio.load(audio_path)
    waveform = waveform.mean(dim=0).numpy()

    encoder = VoiceEncoder(device=device)
    embeddings = []
    segment_data = []

    for seg in segments:
        start, end, text = seg.start, seg.end, seg.text
        start_frame, end_frame = int(start * sr), int(end * sr)
        segment_wav = waveform[start_frame:end_frame]
        if len(segment_wav) < sr * 0.3:
            continue  # 너무 짧은 구간 무시
        embed = encoder.embed_utterance(segment_wav)
        embeddings.append(embed)
        segment_data.append({"start": start, "end": end, "text": text})

    # 3. 화자 분리 (KMeans)
    print("🔀 Clustering speakers...")
    kmeans = KMeans(n_clusters=num_speakers, random_state=0).fit(embeddings)
    speaker_ids = kmeans.labels_

    # 4. 화자 실명 식별 (speaker_db와 centroid 비교)
    print("🧠 Identifying speakers...")
    speaker_db = get_speaker_db(encoder)
    cluster_to_name = {
        i: identify_by_embedding(center, speaker_db)
        for i, center in enumerate(kmeans.cluster_centers_)
    }

    # 5. 결과 구성
    results = []
    for seg, spk_id in zip(segment_data, speaker_ids):
        results.append({
            "speaker": cluster_to_name[spk_id],
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })

    return results

if __name__ == "__main__":
    path = "meeting.wav"
    results = transcribe_and_identify(path, model_size="base", num_speakers=2)
    with open("transcript.txt", "w", encoding="utf-8") as f:
        for seg in results:
            f.write(f"[{seg['speaker']}] {seg['text']}\n")
    print("✅ Written to transcript.txt")