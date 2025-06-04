# === whisper_module/cuda_loader.py ===
import os
import ctypes

def load_cuda_locally():
    cuda_path = os.path.abspath("cuda/bin")
    os.environ["PATH"] = cuda_path + os.pathsep + os.environ["PATH"]

    try:
        # CUDA 런타임
        ctypes.WinDLL("cudart64_12.dll")
        ctypes.WinDLL("cudart64Lt_12.dll")
        ctypes.WinDLL("cudart64_11.dll")

        # cuDNN 9 DLL들
        ctypes.WinDLL("cudnn64_9.dll")
        ctypes.WinDLL("cudnn_ops64_9.dll")
        ctypes.WinDLL("cudnn_cnn64_9.dll")

        print("✅ CUDA + cuDNN 9 DLLs loaded from local folder!")
    except Exception as e:
        print("❌ Failed to load CUDA/cuDNN DLLs:", e)
        print("➡️ Please ensure 'cuda/bin' folder has all required DLLs.")
