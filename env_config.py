# === utils/env_config.py ===
import os
import json
from Util import *

CONFIG_PATH = "env_config.json"

# 전체 프로파일 저장

def save_env_profile(profile_name: str, settings: dict):
    path = get_resource_path(CONFIG_PATH)
    all_data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    all_data[profile_name] = settings
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

# 개별 키 저장

def set_env_setting(profile_name: str, key: str, value):
    path = get_resource_path(CONFIG_PATH)

    all_data = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    if profile_name not in all_data:
        all_data[profile_name] = {}
    all_data[profile_name][key] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

# 프로파일 로딩

def load_env_profile(profile_name: str) -> dict:
    path = get_resource_path(CONFIG_PATH)

    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    return all_data.get(profile_name, {})

# 특정 키 조회

def get_env_setting(profile_name: str, key: str, default=None):
    return load_env_profile(profile_name).get(key, default)

# 모든 프로파일 이름 조회

def get_all_profiles() -> list:
    path = get_resource_path(CONFIG_PATH)

    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    return list(all_data.keys())
