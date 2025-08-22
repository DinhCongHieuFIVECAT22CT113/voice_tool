# Script PowerShell để chạy Voice Tools v3 với toàn bộ cache/model AI lưu trên ổ D
$env:HF_HOME="D:\voice_tools\hf_cache"
$env:TRANSFORMERS_CACHE="D:\voice_tools\hf_cache"
$env:TORCH_HOME="D:\voice_tools\torch_cache"
$env:XDG_CACHE_HOME="D:\voice_tools\ai_cache"

# Kích hoạt môi trường ảo và chạy app
D:/voice_tools/dev/.venv/Scripts/python.exe voice_app_v3.py
