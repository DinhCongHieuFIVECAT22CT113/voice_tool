import customtkinter as ctk
from tkinter import filedialog
from pydub import AudioSegment, silence
import threading, os, subprocess, sys, time
from pydub.utils import which

# ============================
# Cấu hình FFMPEG nội bộ (không cần cài hệ thống)
# ============================
def get_ffmpeg_path():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  # Khi chạy exe
    else:
        base_path = os.path.abspath(".")  # Khi chạy .py

    ffmpeg_dir = os.path.join(base_path, "ffmpeg", "bin")
    if ffmpeg_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + ffmpeg_dir  # ✅ Cho pydub tự động nhận
    return os.path.join(ffmpeg_dir, "ffmpeg.exe"), os.path.join(ffmpeg_dir, "ffprobe.exe")

ffmpeg_path, ffprobe_path = get_ffmpeg_path()
AudioSegment.converter = which("ffmpeg") or ffmpeg_path
AudioSegment.ffprobe   = which("ffprobe") or ffprobe_path

# ============================
# Cấu hình frame logic
# ============================
FRAME_RATE = 30
FRAME_MS = 1000 // FRAME_RATE

# Các ngưỡng xử lý
PARA_CUT_MS = FRAME_MS * 24        # 800ms
PHRASE_6_MS = FRAME_MS * 7        # 200ms

# ============================
# Hàm xử lý file âm thanh
# ============================
def process_audio(input_path, output_path, silence_thresh, progress_callback, text_callback, format_out):
    audio = AudioSegment.from_file(input_path)
    silence_ranges = silence.detect_silence(audio, min_silence_len=FRAME_MS*4, silence_thresh=silence_thresh)

    result = AudioSegment.empty()
    last_end = 0
    total = len(silence_ranges)

    import random
    for i, (start, end) in enumerate(silence_ranges):
        silence_len = end - start
        frame_len = silence_len // FRAME_MS

        if start > last_end:
            result += audio[last_end:start]

        # Cuối câu: frame_len >= 20 thì luôn đưa về 24 frame (800ms)
        if frame_len >= 20:
            head, tail = 200, 100
            mid_sil = PARA_CUT_MS - head - tail
            result += audio[start:start + head]
            result += AudioSegment.silent(duration=mid_sil)
            result += audio[end - tail:end]

        # Giữa câu: 1-6 frame thì bỏ qua, không cắt
        elif frame_len <= 6:
            result += audio[start:end]

        # Giữa câu: 6-20 frame thì cắt random còn 5-7 frame
        elif 6 < frame_len < 20:
            keep_frames = random.randint(5, 7)
            keep_ms = keep_frames * FRAME_MS
            head = keep_ms // 2
            tail = keep_ms - head
            result += audio[start:start + head]
            result += AudioSegment.silent(duration=0)
            result += audio[end - tail:end]

        last_end = end
        percent = round((i + 1) / total * 100)
        progress_callback((i + 1) / total)
        text_callback(f"\u23f3 Đang xử lý... {percent}%")

    result += audio[last_end:]
    result.export(output_path, format=format_out)

# ============================
# Giao diện ứng dụng
# ============================
class VoiceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("\U0001F3A7 Voice Silence Editor - Local")
        self.geometry("700x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.input_file = ""
        self.output_file = ""
        self.output_format = ctk.StringVar(value="mp3")

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="\U0001F6E0\ufe0f Voice Silence Editor", font=("Arial", 24)).pack(pady=10)

        ctk.CTkLabel(self, text="\U0001F4E4 Chọn file đầu vào:").pack()
        self.input_btn = ctk.CTkButton(self, text="\U0001F4C2 Duyệt file", command=self.select_input, width=160)
        self.input_btn.pack(pady=4)
        self.input_label = ctk.CTkLabel(self, text="Chưa chọn file.")
        self.input_label.pack()

        ctk.CTkLabel(self, text="\U0001F4BE Nơi lưu file kết quả:").pack(pady=(10, 0))
        self.output_btn = ctk.CTkButton(self, text="\U0001F4C1 Chọn nơi lưu", command=self.select_output, width=160)
        self.output_btn.pack(pady=4)
        self.output_label = ctk.CTkLabel(self, text="Chưa chọn nơi lưu.")
        self.output_label.pack()

        ctk.CTkLabel(self, text="\U0001F509 Ngưỡng dB để nhận im lặng (mặc định -45):").pack(pady=(10, 2))
        self.db_input = ctk.CTkEntry(self, placeholder_text="-45", width=100, justify="center")
        self.db_input.pack()

        ctk.CTkLabel(self, text="\U0001F4DD Chọn định dạng xuất ra:").pack(pady=(10, 0))
        self.format_select = ctk.CTkOptionMenu(self, values=["wav", "mp3"], variable=self.output_format)
        self.format_select.pack()

        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.set(0)
        self.progress.pack(pady=10)

        self.status = ctk.CTkLabel(self, text="", font=("Arial", 13))
        self.status.pack()

        self.start_btn = ctk.CTkButton(self, text="\U0001F680 BẮT ĐẦU XỬ LÝ", command=self.start_processing, width=200)
        self.start_btn.pack(pady=20)

        self.link_label = ctk.CTkLabel(self, text="", text_color="lightblue", cursor="hand2")
        self.link_label.pack()
        self.link_label.bind("<Button-1>", self.open_folder)

    def select_input(self):
        path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav *.mp3")])
        if path:
            self.input_file = path
            self.input_label.configure(text=os.path.basename(path))

    def select_output(self):
        ext = self.output_format.get()
        path = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(ext.upper(), f"*.{ext}")])
        if path:
            self.output_file = path
            self.output_label.configure(text=os.path.basename(path))

    def update_status(self, text, color="white"):
        self.status.configure(text=text, text_color=color)

    def start_processing(self):
        if not self.input_file or not self.output_file:
            self.update_status("\u274c Vui lòng chọn đủ file và nơi lưu.", "red")
            return

        try:
            db_thresh = int(self.db_input.get()) if self.db_input.get() else -45
        except:
            self.update_status("\u274c Ngưỡng dB phải là số nguyên!", "red")
            return

        self.update_status("\u23f3 Chuẩn bị xử lý...", "yellow")
        self.progress.set(0)
        self.link_label.configure(text="")

        thread = threading.Thread(target=self.run_processing, args=(db_thresh,))
        thread.start()

    def run_processing(self, db_thresh):
        try:
            start_time = time.time()
            process_audio(
                self.input_file,
                self.output_file,
                db_thresh,
                self.progress.set,
                self.update_status,
                self.output_format.get()
            )
            elapsed = round(time.time() - start_time, 2)
            self.update_status(f"\u2705 Đã xử lý xong! (⏱ {elapsed} giây)", "green")
            self.link_label.configure(text=self.output_file)

        except Exception as e:
            self.update_status(f"\u274c Lỗi: {e}", "red")

    def open_folder(self, event):
        if os.path.exists(self.output_file):
            folder = os.path.dirname(os.path.abspath(self.output_file))
            if sys.platform == "win32":
                # Không bật terminal khi mở explorer
                subprocess.Popen(f'explorer "{folder}"', creationflags=0x08000000)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])

if __name__ == "__main__":
    app = VoiceApp()
    app.mainloop()
