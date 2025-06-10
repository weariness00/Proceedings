import subprocess
from pydub import AudioSegment
import os, math
from typing import List

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

def split_audio_to_chunks(input_path: str, chunk_length_s: int = 300) -> List[str]:
    """
    input_path(mp3/wav)을 chunk_length_s(초) 단위로 자르고,
    임시 WAV 파일로 저장한 뒤 파일 경로 리스트를 리턴합니다.
    """
    chunk_paths: List[str] = []

    # 1) audio 로드
    try:
        audio = AudioSegment.from_file(input_path)
    except Exception as e:
        print(f"split_audio_to_chunks: 오디오 로드 실패: {e}")
        return []  # 로드 자체가 실패하면 빈 리스트 반환

    total_ms = len(audio)
    chunk_ms = chunk_length_s * 1000

    # 2) tmp_chunks 디렉토리 준비
    os.makedirs("tmp_chunks", exist_ok=True)

    # 3) 청크 분할
    for start_ms in range(0, total_ms, chunk_ms):
        end_ms = min(start_ms + chunk_ms, total_ms)
        chunk = audio[start_ms:end_ms]
        if len(chunk) <= 0:
            continue
        start_s = start_ms // 1000
        end_s = math.ceil(end_ms / 1000)
        chunk_name = f"tmp_chunks/chunk_{start_s}_{end_s}.wav"
        try:
            chunk.export(chunk_name, format="wav")
            chunk_paths.append(chunk_name)
        except Exception as ex:
            print(f"split_audio_to_chunks: 청크(export) 실패 ({chunk_name}): {ex}")

    # 4) 청크가 하나도 없으면 원본 전체를 하나의 청크로
    if not chunk_paths:
        fallback_name = "tmp_chunks/chunk_0_0.wav"
        try:
            audio.export(fallback_name, format="wav")
            chunk_paths.append(fallback_name)
        except Exception as ex:
            print(f"fallback chunk 생성 실패: {ex}")

    return chunk_paths