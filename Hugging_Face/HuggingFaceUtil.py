import time
import torch

from pyannote.audio import Pipeline
from torch.cuda import device

from env_config import *

class HuggingFaceUtil:
    api_model = "pyannote/speaker-diarization-3.1"
    api_env = "hugging_face"
    api_token_env = "token"

    def __init__(self):

        pass

    def counting(self, file):
        start_time = time.time()
        pipeline = Pipeline.from_pretrained(self.api_model, use_auth_token=get_env_setting(self.api_env, self.api_token_env))  # HuggingFace 토큰 필요

        # 내부적으로 어떤 모델이 로드되는지 체크
        print("torch.cuda.is_available():", torch.cuda.is_available())
        print("CUDA device name:", torch.cuda.get_device_name(0))

        # 5분짜리 한국어 음성파일
        diarization = pipeline(file)
        speakers = set([s for _, _, s in diarization.itertracks(yield_label=True)])

        elapsed = time.time() - start_time
        print(f"걸린 시간 : {elapsed:.2f}")
        print("화자 수:", len(speakers))
        return len(speakers)