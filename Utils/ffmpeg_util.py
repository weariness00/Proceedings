import os
import subprocess

def ffmpeg_ensure_wav(input_path: str, tmp_dir: str = "tmp_ffmpeg") -> str:
    """
    입력이 .wav든 아니든 항상 tmp_ffmpeg 폴더에 16kHz, mono wav로 저장 후 경로 반환
    """
    os.makedirs(tmp_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(tmp_dir, f"{base_name}_converted.wav")

    # 이미 wav라면 ffmpeg로 포맷 변환(16kHz, mono) 및 복사
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", output_path
    ]
    print(" ".join(command))

    try:
        subprocess.run(command, check=True)
        print(f"변환/복사 성공: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg 변환 실패: {e}")
        raise RuntimeError("오디오 변환 실패")

# 사용 예시
# wav_path = ensure_wav_in_tmp("myfile.wav")
# print(wav_path)  # 항상 tmp_ffmpeg/myfile_converted.wav
