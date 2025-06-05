from ui import run_app
from whisper_module.cuda_loader import load_cuda_locally
from runtime_installer import ensure_dependencies

if __name__ == "__main__":
    #ensure_dependencies()  # pip 설치 안되거 설치
    # load_cuda_locally()  # 실행 시 프로젝트 내부 CUDA 경로 등록
    run_app()
