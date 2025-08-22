"""
Module tích hợp WhisperX cho Voice Tools v3.
Yêu cầu: pip install torch openai-whisper whisperx
"""
import whisperx
import torch
from typing import List, Dict

def align_audio_with_text(audio_path: str, transcript: str, lang: str = "vi") -> List[Dict]:
    """
    Sử dụng WhisperX để align audio với text, trả về danh sách segment (start, end, text).
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisperx.load_model("large-v2", device, compute_type="float16" if device=="cuda" else "float32")
    # Nhận diện toàn bộ transcript (nếu cần)
    result = model.transcribe(audio_path, language=lang)
    # Forced alignment
    model_a, metadata = whisperx.load_align_model(language_code=lang, device=device)
    aligned = whisperx.align(result["segments"], model_a, metadata, audio_path, device, return_char_alignments=False)
    # Mỗi segment là 1 câu hoặc cụm từ, có start/end
    return aligned["segments"]
