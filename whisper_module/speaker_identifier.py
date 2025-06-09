# speaker_identifier.py
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import torch
import os
import shutil
from typing import List, Tuple


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    두 벡터 a, b에 대해 코사인 유사도를 계산합니다.
    (둘 다 L2 정규화된 상태라면 dot(a,b)만 해도 무방합니다.)
    """
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b)
    return float(np.dot(a_norm, b_norm))

class SpeakerIdentifier:
    SPEAKER_DB = "speaker_db"
    def __init__(self):
        self.threshold: float = 0.75
        self.speaker_db = {}

    def execute(
            self,
            embed: np.ndarray,
    ) -> str:
        """
        주어진 임베딩을 speaker_db 내 임베딩들과 비교해
        - 최대 코사인 유사도가 threshold 미만이면 "Unknown",
        - 그 이상이면 가장 유사도가 높은 화자 이름 반환
        """
        # 1) 입력 임베딩도 L2 정규화
        if np.linalg.norm(embed) > 0:
            embed_norm = embed / np.linalg.norm(embed)
        else:
            return "Unknown"

        best_name = None
        best_score = -1.0

        for name, ref_embed in self.speaker_db.items():
            # ref_embed는 이미 정규화되어 있다고 가정
            # (만약 안 되어 있다면 ref_embed /‖ref_embed‖ 처리를 해 주세요)
            score = cosine_similarity(embed_norm, ref_embed)
            if score > best_score:
                best_score = score
                best_name = name

        # 임계값 아래라면 Unknown 반환
        if best_score < self.threshold:
            return "Unknown"
        return best_name

    def init_speaker_db(self, encoder: VoiceEncoder) -> dict:
        """
        speaker_db 디렉토리에 있는 모든 화자 샘플을 임베딩하여 딕셔너리 반환.
        Returns:
            dict[str, np.ndarray]: 화자명 -> 임베딩 벡터
        """
        self.speaker_db = {}
        for file_path in Path(self.SPEAKER_DB).glob("*.*"):
            wav = preprocess_wav(str(file_path))
            embed = encoder.embed_utterance(wav)
            self.speaker_db[file_path.stem] = embed

    def cleanup_speakers(self):
        if os.path.exists(self.SPEAKER_DB):
            shutil.rmtree(self.SPEAKER_DB)
    @staticmethod
    def get_speaker_name_and_path() -> List[Tuple[str, str]]:
        """
        speaker_db 디렉토리에서 (전체 경로, 파일 이름) 튜플 리스트 반환
        """
        result = []
        for file_path in Path(SpeakerIdentifier.SPEAKER_DB).glob("*.*"):
            full_path = str(file_path.resolve())
            file_name = file_path.stem
            result.append((full_path, file_name))
        return result
pass

# def remove_last_row(self):
#     if self.speaker_rows:
#         name_var, path_var = self.speaker_rows.pop()
#         filename = name_var.get().strip()
#         if filename:
#             for ext in [".wav", ".mp3", ".m4a", ".ogg"]:
#                 try:
#                     os.remove(os.path.join(SPEAKER_DB, f"{filename}{ext}"))
#                 except FileNotFoundError:
#                     continue
#         row = self.list_frame.winfo_children()[-1]
#         row.destroy()