# whisper_module/cuda_loader.py

import os
import sys
import ctypes

def load_cuda_locally():
    # 1) exe 모드(PyInstaller)라면 sys._MEIPASS, 그렇지 않으면 현재 파일(__file__) 위치 기준으로 폴더 찾기
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.dirname(__file__))

    # 2) DLL이 실제로 들어 있는 곳: “프로젝트 루트/cuda/bin” 이므로, base에서 두 단계 위로 올라가야 합니다.
    #    __file__이 whisper_module/cuda_loader.py 이므로, base는 “…\Proceedings\whisper_module” 같은 경로가 됩니다.
    cuda_bin = os.path.abspath(os.path.join(base, os.pardir, "cuda", "bin"))

    # 3) PATH에 추가해서, 다른 의존 DLL도 자동 로드되도록 합니다.
    os.environ["PATH"] = cuda_bin + os.pathsep + os.environ.get("PATH", "")

    try:
        # 4) ctypes.WinDLL에는 “절대 경로”를 넘겨야 Windows가 정확히 DLL을 찾습니다.
        ctypes.WinDLL(os.path.join(cuda_bin, "cublas64_12.dll"))
        ctypes.WinDLL(os.path.join(cuda_bin, "cublasLt64_12.dll"))
        ctypes.WinDLL(os.path.join(cuda_bin, "cublas64_11.dll"))
        ctypes.WinDLL(os.path.join(cuda_bin, "cublasLt64_11.dll"))

        # 5) CUDA Runtime DLL도 반드시 로드해야 합니다 (예: cudart64_12.dll, cudart64_11.dll)
        ctypes.WinDLL(os.path.join(cuda_bin, "cudart64_12.dll"))
        ctypes.WinDLL(os.path.join(cuda_bin, "cudart64_110.dll"))

        # 6) cuDNN 9 관련 DLL
        ctypes.WinDLL(os.path.join(cuda_bin, "cudnn64_9.dll"))
        ctypes.WinDLL(os.path.join(cuda_bin, "cudnn_ops64_9.dll"))
        ctypes.WinDLL(os.path.join(cuda_bin, "cudnn_cnn64_9.dll"))

        print("✅ CUDA + cuDNN DLLs loaded successfully from:", cuda_bin)
    except Exception as e:
        print("❌ Failed to load CUDA/cuDNN DLLs:", e)
        print("➡️ Ensure that:")
        print(f"   1) cuda_bin folder exists at: {cuda_bin}")
        print("   2) All required DLLs are present, including:")
        print("      • cublas64_12.dll, cublasLt64_12.dll, cublas64_11.dll")
        print("      • cudart64_12.dll (CUDA Runtime for 12.x) and cudart64_11.dll (for 11.x)")
        print("      • cudnn64_9.dll, cudnn_ops64_9.dll, cudnn_cnn64_9.dll")
