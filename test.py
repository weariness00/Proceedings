# test_pydub_ffmpeg.py

import os
from pydub import AudioSegment
import subprocess

# ➊ 우선 AudioSegment.converter/ffprobe에 절대경로 지정
AudioSegment.converter = r"C:\Program Files\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
AudioSegment.ffprobe   = r"C:\Program Files\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin\ffprobe.exe"

# ➋ 실제로 지정된 경로가 올바르게 반영되었는지 확인
print("▶ AudioSegment.converter →", AudioSegment.converter)
print("▶ AudioSegment.ffprobe   →", AudioSegment.ffprobe)
print("▶ ffmpeg.exe exists?     →", os.path.exists(AudioSegment.converter))
print("▶ ffprobe.exe exists?    →", os.path.exists(AudioSegment.ffprobe))

# ➌ pydub이 mediainfo_json 단계에서 ffprobe를 호출할 때
#     실제로 어떤 명령어를 쓰는지 살펴보기 위해,
#     subprocess.run으로 직접 "ffprobe -version"을 실행해 봅니다.
try:
    res = subprocess.run(
        [AudioSegment.ffprobe, "-version"],
        capture_output=True, text=True, check=True
    )
    print("▶ subprocess ffprobe -version →", res.stdout.splitlines()[0])
except Exception as e:
    print("▶ subprocess ffprobe 호출 실패:", e)

# ➍ 이제 실제 오디오 파일을 가져와 보는 단계
audio_path = r"D:\GItData\Proceedings\short_test.mp3"
if not os.path.exists(audio_path):
    raise FileNotFoundError(f"'{audio_path}' 파일이 존재하지 않습니다.")

# 이 단계에서 mediainfo_json이 내부적으로 “AudioSegment.ffprobe”를 사용해야 합니다.
try:
    a = AudioSegment.from_file(audio_path)
    print("▶ short_test.mp3 길이(ms) →", len(a))
    chunk = a[:2000]  # 앞 2초만 잘라서
    out_path = "test_2s.wav"
    chunk.export(out_path, format="wav")
    print("▶🎉 test_2s.wav 생성 완료")
except Exception as ex:
    print("▶ AudioSegment.from_file 오류:", ex)
