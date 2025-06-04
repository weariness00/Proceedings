import os
from notion_client import Client
from env_config import *
import tkinter as tk
from notion.Notion_Define import *

class NotionUI:
    def __init__(self, database_id: str = None):
        """
        NotionUI 생성자
        :param database_id: 코드에서 직접 지정할 데이터베이스 ID. 지정하지 않으면 env_config의 설정값 사용.
        """
        # env_config.json에서 token과 database_id를 기본값으로 로드
        self._token = get_env_setting("notion", "token")
        if not self._token:
            raise RuntimeError("Notion token이 설정되지 않았습니다. env_config.json을 확인하세요.")

        # 코드에서 database_id가 전달되었을 경우 우선 사용, 그렇지 않으면 env 설정을 사용
        if database_id:
            self._database_id = database_id
        else:
            default_db = get_env_setting("notion", "database_id")
            if not default_db:
                raise RuntimeError("Notion database_id가 설정되지 않았습니다. env_config.json을 확인하세요.")
            self._database_id = default_db

        # Notion Client 초기화
        self._client = Client(auth=self._token)

    def show_setting_gui(self):
        # 제목 입력 라벨 및 엔트리
        self.setting_window = tk.Tk()
        self.setting_window.title("Notion 요약 설정")
        self.setting_window.geometry("600x450")

        root = self.setting_window

        tk.Label(root, text="API Token").pack(anchor='w', padx=10, pady=(10,0))
        self.api_text = tk.Entry(root, width=60)
        self.api_text.pack(padx=10, pady=(0,10))
        self.api_text.insert(0, get_env_setting(notion_key, notion_token_key))

        # 요약문 입력 라벨 및 스크롤 텍스트
        tk.Label(root, text="Notion Database ID").pack(anchor='w', padx=10,  pady=(10,0))
        self.database_id_text = tk.Entry(root, width=60)
        self.database_id_text.pack(padx=10, pady=(0,10))
        self.database_id_text.insert(0, get_env_setting(notion_key, notion_database_id_key))

        # 저장 버튼
        tk.Button(root, text="✅ Save Settings", command=self.on_save).pack(pady=15)
        root.mainloop()

    def on_save(self):
        api = self.api_text.get().strip()
        database_id = self.database_id_text.get("1.0", tk.END).strip()

        if api:
            save_env_profile(notion_key, notion_token_key, api)
        if database_id:
            save_env_profile(notion_key, notion_database_id_key, database_id)

        self.window.destroy()

    def set_database_id(self, database_id: str):
        """
        런타임 중에 database_id를 변경합니다.
        :param database_id: 새로 사용할 데이터베이스 ID
        """
        if not database_id:
            raise ValueError("유효한 database_id를 입력하세요.")
        self._database_id = database_id

    def get_database_id(self) -> str:
        """
        현재 설정된 database_id를 반환합니다.
        """
        return self._database_id

    def get_client(self) -> Client:
        """
        Notion Client 인스턴스를 반환합니다.
        """
        return self._client


# 모듈 사용 예시:
# from notion_ui import NotionUI
# ui = NotionUI()  # env_config에 설정된 database_id 사용
# custom_ui = NotionUI(database_id="다른_DB_ID")  # 런타임에 DB ID 변경 가능
# payload = ui.build_payload("2025-06-04 회의 요약", "여기에 요약 텍스트")
# created_page = ui.create_page(payload)
# print(created_page.get("url"))
