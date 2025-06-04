from notion_client import Client
from env_config import get_env_setting

def create_page(new_page_payload):
    # 1) 환경변수(또는 JSON 설정)에서 토큰/데이터베이스 ID 불러오기
    token = get_env_setting("notion", "token")
    database_id = get_env_setting("notion", "database_id")
    if not token or not database_id:
        raise RuntimeError("Notion token 또는 database_id가 설정되지 않았습니다 (env_config.json 확인).")

    # 2) Notion Client 초기화
    notion = Client(auth=token)

    # 5) Notion API로 페이지 생성 요청
    response = notion.pages.create(**new_page_payload)
    return response
