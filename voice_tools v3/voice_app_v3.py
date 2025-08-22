"""
Voice Tools v3 - Khung ứng dụng sử dụng AI alignment để cắt audio theo dấu câu và rule.
"""
import customtkinter as ctk
from tkinter import filedialog
import threading, os, sys, time
from pydub import AudioSegment

from rules import find_punctuation_indices, adjust_cut_points
from whisperx_integration import align_audio_with_text
from pydub import AudioSegment, silence

class VoiceAppV3(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voice Tools v3 - AI Alignment")
        self.geometry("700x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.input_file = ""
        self.input_text = ""
        self.output_file = ""
        self.cut_mode = ctk.StringVar(value="AI")
        self.output_format = ctk.StringVar(value="wav")
        self.create_widgets()

    def create_widgets(self):
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=12, pady=12)
        ctk.CTkLabel(main, text="Chọn file audio:").pack()
        ctk.CTkButton(main, text="Chọn file", command=self.select_input).pack()
        self.lbl_input = ctk.CTkLabel(main, text="Chưa chọn file")
        self.lbl_input.pack()
        ctk.CTkLabel(main, text="Nhập hoặc dán kịch bản text:").pack(pady=(10,0))
        self.text_input = ctk.CTkTextbox(main, height=120)
        self.text_input.pack(fill="x", pady=5)
        ctk.CTkButton(main, text="Chọn nơi lưu", command=self.select_output).pack(pady=(10,0))
        self.lbl_output = ctk.CTkLabel(main, text="Chưa chọn nơi lưu")
        self.lbl_output.pack()
        ctk.CTkLabel(main, text="Chọn chế độ cắt:").pack(pady=(10,0))
        ctk.CTkOptionMenu(main, values=["AI", "Rule", "Hybrid"], variable=self.cut_mode).pack()
        ctk.CTkLabel(main, text="Định dạng xuất:").pack(pady=(10,0))
        ctk.CTkOptionMenu(main, values=["wav", "mp3"], variable=self.output_format).pack()
        ctk.CTkButton(main, text="BẮT ĐẦU XỬ LÝ", command=self.start_processing).pack(pady=20)
        self.status = ctk.CTkLabel(main, text="")
        self.status.pack()

    def select_input(self):
        path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav *.mp3")])
        if path:
            self.input_file = path
            self.lbl_input.configure(text=os.path.basename(path))

    def select_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav"), ("MP3", "*.mp3")])
        if path:
            self.output_file = path
            self.lbl_output.configure(text=os.path.basename(path))

    def start_processing(self):
        self.status.configure(text="Đang xử lý...")
        thread = threading.Thread(target=self.run_processing)
        thread.start()

    def run_processing(self):
        try:
            text = self.text_input.get("1.0", "end").strip()
            mode = self.cut_mode.get()
            fmt = self.output_format.get()
            audio = AudioSegment.from_file(self.input_file)
            segments = []
            if mode == "AI":
                self.status.configure(text="Đang AI align...")
                self.update()
                segments = align_audio_with_text(self.input_file, text, lang="vi")
                cut_points = [(int(seg['start']*1000), int(seg['end']*1000)) for seg in segments]
            elif mode == "Rule":
                self.status.configure(text="Đang tìm dấu câu bằng rule...")
                self.update()
                punct_indices = find_punctuation_indices(text)
                punct_indices = adjust_cut_points(punct_indices)
                # Giả lập: chia đều audio theo số dấu câu (cần đồng bộ ms <-> char index thực tế)
                total_len = len(audio)
                cut_points = []
                last = 0
                for idx in punct_indices:
                    t = int(idx/len(text)*total_len)
                    cut_points.append((last, t))
                    last = t
                cut_points.append((last, total_len))
            else:  # Hybrid
                self.status.configure(text="Đang AI align + hậu kiểm...")
                self.update()
                segments = align_audio_with_text(self.input_file, text, lang="vi")
                cut_points = [(int(seg['start']*1000), int(seg['end']*1000)) for seg in segments]
                # Hậu kiểm: loại bỏ đoạn quá ngắn, thêm im lặng nếu cần
                min_len = 300  # ms
                checked = []
                for s, e in cut_points:
                    if e-s >= min_len:
                        checked.append((s, e))
                cut_points = checked
            # Cắt và ghép lại thành 1 file hoàn chỉnh
            chunks = []
            for idx, (start_ms, end_ms) in enumerate(cut_points):
                chunk = audio[start_ms:end_ms]
                # Hậu kiểm: nếu đoạn quá ngắn, thêm im lặng
                if len(chunk) < 300:
                    chunk += AudioSegment.silent(duration=300-len(chunk))
                chunks.append(chunk)
                # Xuất từng đoạn nhỏ nếu muốn
                out_path = self.output_file.replace(f'.{fmt}', f'_seg{idx+1}.{fmt}')
                chunk.export(out_path, format=fmt)
            # Ghép lại thành 1 file
            final = sum(chunks[1:], chunks[0]) if chunks else audio
            final.export(self.output_file, format=fmt)
            self.status.configure(text=f"Đã cắt {len(chunks)} đoạn và ghép lại thành 1 file hoàn chỉnh.")
        except Exception as e:
            self.status.configure(text=f"Lỗi: {e}")

if __name__ == "__main__":
    app = VoiceAppV3()
    app.mainloop()
