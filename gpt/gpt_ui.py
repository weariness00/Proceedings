import tkinter as tk
from tkinter import filedialog, messagebox
from gpt.gpt_define import *
from env_config import *

def show_gpt_settings_ui(parent):
    prompt_text = get_env_setting(gpt_env, gpt_prompt_env)
    api_key = get_env_setting(gpt_env, gpt_api_env)

    def on_save():
        api = api_entry.get().strip()
        prompt = prompt_box.get("1.0", tk.END).strip()

        if api:
            set_env_setting(gpt_env, gpt_api_env, api)
        if prompt:
            set_env_setting(gpt_env, gpt_prompt_env, prompt)

        window.destroy()

    window = tk.Toplevel(parent)
    window.title("GPT 요약 설정")
    window.geometry("600x450")
    window.transient(parent)
    window.attributes('-topmost', True)
    window.lift(parent)

    # API 키 입력
    tk.Label(window, text="🔑 OpenAI API Key:").pack(anchor="w", padx=10, pady=(10, 0))
    api_entry = tk.Entry(window, width=60, show="*")
    api_entry.insert(0, api_key)
    api_entry.pack(padx=10, pady=5)

    # 프롬프트 입력
    tk.Label(window, text="📝 요약 프롬프트:").pack(anchor="w", padx=10, pady=(15, 0))
    prompt_box = tk.Text(window, height=12, width=72)
    prompt_box.insert("1.0", prompt_text)
    prompt_box.pack(padx=10, pady=5)

    # 출력 경로 선택
    tk.Label(window, text="3. Select output folder:").pack(pady=5)
    output_dir_var = tk.StringVar()
    output_dir_var.set(get_env_setting(gpt_env, gpt_output_dir_env))

    def choose_output_folder():
        path = filedialog.askdirectory()
        output_dir_var.set(path)
        set_env_setting(gpt_env, gpt_output_dir_env, path)

    tk.Button(window, text="Choose Folder", command=choose_output_folder).pack()
    tk.Label(window, textvariable=output_dir_var, fg="green").pack(pady=5)

    # 저장 버튼
    tk.Button(window, text="✅ Save Settings", command=on_save).pack(pady=15)
    window.mainloop()