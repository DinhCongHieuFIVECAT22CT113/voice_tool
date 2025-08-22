# Voice Tools v3

## Mục tiêu
- Cắt audio theo dấu câu, ngắt nghỉ tự nhiên dựa trên AI alignment và rule.
- Tích hợp tốt cho tiếng Việt.

## Hướng phát triển
- Tích hợp WhisperX hoặc API alignment.
- Kết hợp rule hậu kiểm để điều chỉnh ngắt nghỉ.
- Giao diện đơn giản, dễ mở rộng.

## Cài đặt đề xuất
```bash
pip install customtkinter pydub
# Nếu dùng AI alignment:
# pip install torch openai-whisper whisperx
```

## Sử dụng
- Chạy `voice_app_v3.py` để mở giao diện.
- Chọn file audio, nhập kịch bản text, chọn nơi lưu, nhấn BẮT ĐẦU AI ALIGN.
- (Demo: hiện tại chỉ tìm điểm cắt theo dấu câu, chưa cắt audio thực tế)
