# === utils/env_config.py ===
import os
import json

CONFIG_PATH = "env_config.json"

# 전체 프로파일 저장

def save_env_profile(profile_name: str, settings: dict):
    all_data = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    all_data[profile_name] = settings
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

# 개별 키 저장

def set_env_setting(profile_name: str, key: str, value):
    all_data = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    if profile_name not in all_data:
        all_data[profile_name] = {}
    all_data[profile_name][key] = value
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

# 프로파일 로딩

def load_env_profile(profile_name: str) -> dict:
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    return all_data.get(profile_name, {})

# 특정 키 조회

def get_env_setting(profile_name: str, key: str, default=None):
    return load_env_profile(profile_name).get(key, default)

# 모든 프로파일 이름 조회

def get_all_profiles() -> list:
    if not os.path.exists(CONFIG_PATH):
        return []
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    return list(all_data.keys())
