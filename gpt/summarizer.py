from openai import OpenAI
from env_config import *
from gpt.gpt_define import *
from tkinter import messagebox
from notion.Notion_Define import *
import datetime

def summarize_meeting(meeting_text: str) -> str:
    prompt = ((get_env_setting(gpt_env, gpt_prompt_env)
               + f"다음 내용은 니가 필수적으로 숙지하고 있어야 할 사항들이야"
              + f"데이터 베이스 id는 {get_env_setting(notion_key, notion_database_id_key)}를 적는다.")
              + f"현재 날자 : {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()}")

    client = OpenAI(api_key=get_env_setting(gpt_env, gpt_api_env))
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": meeting_text}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages= messages,
            temperature=0.4
        )
    except Exception as e:
        # 그 외 모든 예외 처리
        print(e)
        messagebox.showerror("오류", f"알 수 없는 오류가 발생했습니다:\n{str(e)}")

    if not response.choices:
        # (거의 일어나지 않는 케이스지만) 만약 choices가 비어 있으면 실패 간주
        messagebox.showerror("내용이 비어있음", f"OpenAI 응답은 왔지만, choices가 비어 있습니다.")
        raise RuntimeError("OpenAI 응답은 왔지만, choices가 비어 있습니다.")

    return response.choices[0].message.content
