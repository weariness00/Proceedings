# === ui/main_ui.py ===
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from gpt.gpt_define import gpt_env, gpt_output_dir_env
from gpt.summarizer import summarize_meeting
from whisper_module.transcriber import Transcribe
from whisper_module.speaker_identifier import *
from whisper_module.speaker_manager_ui import SpeakerManagerUI
from gpt.gpt_ui import show_gpt_settings_ui  # <-- GPT 설정 통합 UI
from notion.NotionUI import *
from env_config import *
import os
import time
import notion.NotionDataBaseManager as NotionDBM

notion_ui = NotionUI()

def run_app():
    root = tk.Tk()
    root.title("Whisper GUI - Meeting Transcriber")
    root.geometry("900x550")
    frame_left = tk.Frame(root)
    frame_left.pack(side="left", fill="both", expand=True)

    frame_right = tk.Frame(root)
    frame_right.pack(side="right", fill="y")

    menu(root)
    set_test_frame(frame_left)
    set_speaker_frame(frame_right)
    root.mainloop()

def menu(window):
    menubar = tk.Menu(window)
    window.config(menu=menubar)
    # 3) 'Settings' 메뉴(드롭다운) 추가
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)

    # 4) Settings 안에 실제 항목들 추가

    settings_menu.add_command(label="GPT Setting", command=lambda :show_gpt_settings_ui(window))
    settings_menu.add_command(label="Notion Setting", command=notion_ui.show_setting_gui)
    settings_menu.add_separator()
    settings_menu.add_command(label="종료", command=window.quit)


def set_test_frame(frame):
    # Whisper 모델 선택
    tk.Label(frame, text="1. Select Whisper model:").pack(pady=5)
    model_var = tk.StringVar(value= get_env_setting("whisper_module", "current_model"))
    model_box = ttk.Combobox(frame, textvariable=model_var, values=["tiny", "base", "medium", "large-v2"])
    model_box.pack(pady=5)
    model_box.bind("<<ComboboxSelected>>", lambda e: set_env_setting("whisper_module", "current_model", model_var.get()))

    # 새로운: 화자 수 입력 영역
    tk.Label(frame, text="2. Number of speakers:").pack(pady=5)
    num_speakers_var = tk.IntVar(value=2)  # 기본값 2
    num_spin = tk.Spinbox(frame, from_=1, to=10, textvariable=num_speakers_var, width=5)
    num_spin.pack(pady=5)

    # 오디오 파일 선택
    tk.Label(frame, text="2. Select audio/video file:").pack(pady=5)
    file_var = tk.StringVar()

    def choose_file():
        path = filedialog.askopenfilename(filetypes=[("Audio/Video", "*.mp3 *.wav *.mp4")])
        file_var.set(path)

    tk.Button(frame, text="Browse", command=choose_file).pack()
    tk.Label(frame, textvariable=file_var, fg="blue").pack(pady=5)

    # 출력 경로 선택
    tk.Label(frame, text="3. Select output folder:").pack(pady=5)
    output_dir_var = tk.StringVar()
    output_dir_var.set(get_env_setting("whisper_module","save_dir"))

    def choose_output_folder():
        path = filedialog.askdirectory()
        output_dir_var.set(path)
        set_env_setting("whisper_module","save_dir", path)

    tk.Button(frame, text="Choose Folder", command=choose_output_folder).pack()
    tk.Label(frame, textvariable=output_dir_var, fg="green").pack(pady=5)

    # 화자 샘플 등록 영역
    # tk.Label(frame, text="4. Register speaker sample:").pack(pady=5)
    # speaker_name_var = tk.StringVar()
    # tk.Entry(frame, textvariable=speaker_name_var).pack()
    #
    # def register_sample():
    #     path = filedialog.askopenfilename(filetypes=[("files", "*.mp3 *.wav *.mp4")])
    #     if not path:
    #         return
    #     name = speaker_name_var.get().strip()
    #     if not name:
    #         messagebox.showwarning("No name", "Please enter speaker name.")
    #         return
    #     os.makedirs("speaker_db", exist_ok=True)
    #     shutil.copy(path, f"speaker_db/{name}.wav")
    #     messagebox.showinfo("Registered", f"Sample for '{name}' registered.")
    #
    # tk.Button(frame, text="Select & Register WAV File", command=register_sample).pack(pady=5)

    progress_label = tk.Label(frame, text="")
    progress_label.pack(pady=5)

    def on_transcribe():
        if not file_var.get():
            messagebox.showwarning("No file", "Please select an audio or video file.")
            return
        if not output_dir_var.get():
            messagebox.showwarning("No output folder", "Please specify where to save the transcript.")
            return

        transcribe = Transcribe()
        progress_label.config(text="🔄 Transcribing... please wait.")
        frame.update()

        start_time = time.time()
        try:
            transcribe.model_name = model_var.get()
            transcribe.speaker_count = num_speakers_var.get()
            results = transcribe.execute(file_var.get(), chunk_length_s=300)
            print("전사 완료")
        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"Transcription failed:\n{e}")
            return

        try:
            final_output = ""
            for seg in results:
                final_output += f"[{seg['speaker']}] {seg['text']}\n"

            base_name = os.path.splitext(os.path.basename(file_var.get()))[0]
            output_path = os.path.join(output_dir_var.get(), f"{base_name}_transcript.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_output)
        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"Transcription Write failed:\n{e}")
            return

        progress_label.config(text="")
        elapsed = time.time() - start_time
        print("Transcription complete!\nSaved to: {output_path}\nTime taken: {elapse0d:.2f} seconds")
        messagebox.showinfo("Done",f"Transcription complete!\nSaved to: {output_path}\nTime taken: {elapsed:.2f} seconds")

    tk.Button(frame, text="Start Transcription", command=on_transcribe).pack(pady=20)

    show_open_ai_gui(frame)
    test(frame)

import json

def show_open_ai_gui(frame):
    file_var = tk.StringVar()
    def choose_file():
        path = filedialog.askopenfilename(filetypes=[("Transcript", "*.txt")])
        file_var.set(path)

    def summary():
        file_path = file_var.get()
        start_time = time.time()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            # 이제 text_content 변수에 파일의 내용 전체가 문자열로 들어있습니다.
            raw = summarize_meeting(text_content)
            # 1) 앞뒤 큰따옴표 제거
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]

            # 2) 이스케이프된 따옴표나 줄바꿈(\n) 같은 걸 실제 JSON 형식으로 바꿔주기
            json_str = raw.encode('utf-8').decode('unicode_escape')

            base_name = os.path.splitext(os.path.basename(file_var.get()))[0]
            output_path = os.path.join(get_env_setting(gpt_env, gpt_output_dir_env), f"{base_name}_summary.json")
            try:
                json_str = json_str.encode('latin-1').decode('utf-8')
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
            except json.JSONDecodeError as e:
                print("JSON 파싱 오류:", e)
                messagebox.showerror("JSON 파싱 오류", f"{e}")

            # with open(output_path, "w", encoding="utf-8") as f:
            #     json.dump(json_str, f, ensure_ascii=False, indent=2)
            elapsed = time.time() - start_time
            print("Done",f"GPT Summary Complete!\nSaved to: {output_path}\nTime taken: {elapsed:.2f} seconds")
            messagebox.showinfo("Done",f"GPT Summary Complete!\nSaved to: {output_path}\nTime taken: {elapsed:.2f} seconds")
        except Exception as e:
            messagebox.showerror("오류", f"파일 읽기 중 오류 발생:\n{str(e)}")
            print("파일 읽기 중 오류 발생:", e)

    tk.Button(frame, text="Choose Transcript", command=choose_file).pack()
    tk.Label(frame, textvariable=file_var, fg="blue").pack(pady=5)
    tk.Button(frame, text="Start Summary", command=summary).pack()



def set_speaker_frame(frame):
    speaker_ui = SpeakerManagerUI(frame)
    for data in get_speaker_name_and_path():
        speaker_ui.add_speaker_row(data)

def test(frame):
    def choose_file():
        path = filedialog.askopenfilename(filetypes=[("json", "*.json")])
        try:
            with open(path, "r", encoding="utf-8") as f:
                # 문자열이 아니라 dict 로 바로 읽어옴
                notion_payload = json.load(f)

            # 이제 notion_payload는 dict 타입이므로 create_page에 그대로 넘길 수 있음
            NotionDBM.create_page(notion_payload)
        except Exception as e:
            messagebox.showerror("오류", f"{str(e)}")
            print("파일 읽기 중 오류 발생:", e)

    tk.Button(frame, text="test", command=choose_file).pack()


