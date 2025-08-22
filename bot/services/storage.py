import json
from typing import List

FANS_FILE = "data/fans.json"
POSTS_FILE = "data/posts.json"
BANWORDS_FILE = "data/banwords.json"
CONTENT_FILE = "data/content.txt"
BANNED_USERS_FILE = "data/banned_users.json"

def _read_json(file_path: str, default_type: type = list):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_type()

def _write_json(file_path: str, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_fans() -> List[str]:
    return _read_json(FANS_FILE)

def add_fan(fan_text: str):
    fans = get_fans()
    fans.append(fan_text)
    _write_json(FANS_FILE, fans)

def remove_fan_by_text_part(text_part_to_find: str):
    fans = get_fans()
    original_len = len(fans)
    fans_after_removal = [fan for fan in fans if text_part_to_find not in fan]

    if len(fans_after_removal) < original_len:
        _write_json(FANS_FILE, fans_after_removal)
        return True
    return False

def get_banned_users() -> dict:
    return _read_json(BANNED_USERS_FILE, default_type=dict)

def ban_user(user_id: int, reason: str, admin_id: int):
    banned_users = get_banned_users()
    banned_users[str(user_id)] = {
        "reason": reason,
        "banned_by": admin_id
    }
    _write_json(BANNED_USERS_FILE, banned_users)

def unban_user(user_id: int) -> bool:
    banned_users = get_banned_users()
    if str(user_id) in banned_users:
        del banned_users[str(user_id)]
        _write_json(BANNED_USERS_FILE, banned_users)
        return True
    return False

def get_posts() -> List[int]:
    return _read_json(POSTS_FILE)

def update_posts(post_ids: List[int]):
    _write_json(POSTS_FILE, post_ids)

def get_banwords() -> List[str]:
    return _read_json(BANWORDS_FILE)

def add_banword(word: str) -> bool:
    banwords = get_banwords()
    if word.lower() not in [bw.lower() for bw in banwords]:
        banwords.append(word)
        _write_json(BANWORDS_FILE, banwords)
        return True
    return False

def set_content_text(text: str):
    with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
        f.write(text)

def get_content_text() -> str | None:
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            text = f.read().strip()
            return text if text else None
    except FileNotFoundError:
        # Если файла нет, создаем пустой
        open(CONTENT_FILE, 'w').close()
        return None