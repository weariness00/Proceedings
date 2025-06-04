import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from typing import Tuple

SPEAKER_DB = "speaker_db"

class SpeakerManagerUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.speakers = []
        self.pack(side="right", fill="both", expand=False)
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="화자 구분 UI", bg="lightgreen", font=("Arial", 11, "bold")).pack(fill="x")

        self.list_frame = tk.Frame(self)
        self.list_frame.pack(padx=5, pady=5)

        self.speaker_rows = []

        self.add_button = tk.Button(self, text="＋", fg="purple", command=self.add_speaker_row)
        self.add_button.pack(side="left", padx=5, pady=5)

        self.remove_button = tk.Button(self, text="－", command=self.remove_last_row)
        self.remove_button.pack(side="left", padx=5, pady=5)

    def add_speaker_row(self, data:Tuple[str, str]):
        row_frame = tk.Frame(self.list_frame)
        row_frame.pack(fill="x", pady=2)

        name_var = tk.StringVar()
        path_var = tk.StringVar()
        if data is not None:
            path_var.set(data[0])
            name_var.set(data[1])

        tk.Entry(row_frame, textvariable=name_var, width=15).pack(side="left", padx=2)
        tk.Entry(row_frame, textvariable=path_var, width=30).pack(side="left", padx=2)

        ext = os.path.splitext(data[0])[1]
        old_path_container = [os.path.join(SPEAKER_DB, f"{data[1]}{ext}")]
        def choose_file():
            path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav"), ("Audio", "*.mp3 *.m4a *.ogg")])
            if path:
                path_var.set(path)
        def on_name_change(*args):
            new_name = name_var.get().strip()
            if not new_name:
                return

            new_path = os.path.join(SPEAKER_DB, f"{new_name}{ext}")
            old_path = old_path_container[0]

            try:
                if os.path.exists(old_path) and old_path != new_path:
                    os.rename(old_path, new_path)
                    path_var.set(new_path)
                    old_path_container[0] = new_path  # 업데이트
            except Exception as e:
                messagebox.showerror("이름 변경 실패", f"{old_name} → {new_name} 이름 변경 중 오류:\n{e}")

        name_var.trace_add("write", on_name_change)
        tk.Button(row_frame, text="Browse", command=choose_file).pack(side="left")

        self.speaker_rows.append((name_var, path_var))

    def remove_last_row(self):
        if self.speaker_rows:
            row = self.list_frame.winfo_children()[-1]
            row.destroy()
            self.speaker_rows.pop()

    def save_all_speakers(self):
        os.makedirs(SPEAKER_DB, exist_ok=True)
        for name_var, path_var in self.speaker_rows:
            name = name_var.get().strip()
            path = path_var.get().strip()
            if not name or not path:
                continue
            try:
                dest = os.path.join(SPEAKER_DB, f"{name}{os.path.splitext(path)[1]}")
                shutil.copy(path, dest)
            except Exception as e:
                messagebox.showerror("Error", f"{name}: 복사 실패\n{e}")
