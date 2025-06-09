
import json
import os
from datetime import datetime


# 설정 상수
DATA_DIR = "data"
VISUALIZATION_DIR = "visualization_results"
DEFAULT_SCENARIO_TYPE = "magic_kingdom"
SCENARIO_TYPES = {
    "🏰 마법 왕국": "magic_kingdom",
    "🚚 푸드트럭 왕국": "foodtruck_kingdom", 
    "🌙 달빛 도둑": "moonlight_thief",
    "🐷 아기돼지 삼형제": "three_little_pigs"
}


def ensure_dir(directory_path):
    """디렉토리가 없으면 생성"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def generate_filename(scenario_type, prefix="game_scenario"):
    """타임스탬프를 포함한 파일명 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(DATA_DIR, f"{prefix}_{scenario_type}_{timestamp}.json")


def save_scenario_to_file(scenario_data, filename):
    """게임 시나리오를 JSON 파일로 저장"""
    ensure_dir(DATA_DIR)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(scenario_data, f, ensure_ascii=False, indent=2)


def load_scenario_from_file(filename):
    """JSON 파일에서 게임 시나리오 로드"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_available_scenarios(data_dir=DATA_DIR):
    """사용 가능한 게임 시나리오 파일 목록 반환"""
    if not os.path.exists(data_dir):
        return []
    files = [f for f in os.listdir(data_dir) if f.startswith("game_scenario_") and f.endswith(".json")]
    return sorted(files, reverse=True)


# 디렉토리 초기화
ensure_dir(DATA_DIR)
ensure_dir(VISUALIZATION_DIR)
