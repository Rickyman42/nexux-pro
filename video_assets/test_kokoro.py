import sys
import os

output_path = "Y:\\nexux-pro\\video_assets\\test_result.txt"
try:
    import kokoro_onnx
    import soundfile
    with open(output_path, "w") as f:
        f.write("SUCCESS: kokoro_onnx and soundfile are importable!\n")
        f.write(f"Python executable: {sys.executable}\n")
except Exception as e:
    with open(output_path, "w") as f:
        f.write(f"FAILURE: {str(e)}\n")
        f.write(f"Python path: {sys.path}\n")
