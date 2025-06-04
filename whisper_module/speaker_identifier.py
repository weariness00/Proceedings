# speaker_identifier.py
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import torch
import os
import shutil
from typing import List, Tuple

SPEAKER_DB = "speaker_db"

def get_speaker_db(encoder: VoiceEncoder) -> dict:
    """
    speaker_db 디렉토리에 있는 모든 화자 샘플을 임베딩하여 딕셔너리 반환.
    Returns:
        dict[str, np.ndarray]: 화자명 -> 임베딩 벡터
    """
    speaker_db = {}
    for file_path in Path(SPEAKER_DB).glob("*.*"):
        wav = preprocess_wav(str(file_path))
        embed = encoder.embed_utterance(wav)
        speaker_db[file_path.stem] = embed
    return speaker_db

def identify_by_embedding(embed: np.ndarray, speaker_db: dict) -> str:
    """
    주어진 임베딩을 speaker_db 내 임베딩들과 비교해 가장 유사한 화자 식별
    """
    best_match = None
    best_score = -1
    for name, ref_embed in speaker_db.items():
        similarity = np.dot(embed, ref_embed)
        if similarity > best_score:
            best_score = similarity
            best_match = name
    return best_match or "Unknown"

def get_speaker_name_and_path() -> List[Tuple[str, str]]:
    """
    speaker_db 디렉토리에서 (전체 경로, 파일 이름) 튜플 리스트 반환
    """
    result = []
    for file_path in Path(SPEAKER_DB).glob("*.*"):
        full_path = str(file_path.resolve())
        file_name = file_path.stem
        result.append((full_path, file_name))
    return result

def cleanup_speakers():
    if os.path.exists(SPEAKER_DB):
        shutil.rmtree(SPEAKER_DB)

def remove_last_row(self):
    if self.speaker_rows:
        name_var, path_var = self.speaker_rows.pop()
        filename = name_var.get().strip()
        if filename:
            for ext in [".wav", ".mp3", ".m4a", ".ogg"]:
                try:
                    os.remove(os.path.join(SPEAKER_DB, f"{filename}{ext}"))
                except FileNotFoundError:
                    continue
        row = self.list_frame.winfo_children()[-1]
        row.destroy()