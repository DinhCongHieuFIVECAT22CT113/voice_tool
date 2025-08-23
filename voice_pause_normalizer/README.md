# Voice Pause Normalizer

Công cụ dòng lệnh chuẩn hoá khoảng lặng giữa các câu nói tiếng Việt dựa vào dấu câu trong kịch bản.

## Cài đặt

```bash
pip install -r requirements.txt
# cần cài sẵn ffmpeg trong PATH
```

## Sử dụng

```bash
python -m voice_pause_normalizer.cli \
  --audio input.wav \
  --script "script.txt" \
  --out output.mp3 \
  --format mp3 \
  --punct-map default \
  --crossfade-ms 3
```

* `--script` có thể là đường dẫn tới file hoặc chuỗi văn bản được paste trực tiếp.
* Mặc định xuất `mp3`; chọn `--format wav` nếu muốn WAV.
* Công cụ giữ nguyên phần voice, chỉ thay khoảng lặng bằng độ dài mục tiêu theo dấu câu.
