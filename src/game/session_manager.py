
import streamlit as st
from src.utils.config import load_api_key


def initialize_session_state():
    """세션 상태 초기화"""
    session_defaults = {
        'game_data': None,
        'current_turn_index': 0,
        'player_investments': {},
        'player_balance': 1000,
        'investment_history': [],
        'game_log': [],
        'game_started': False,
        'current_step': 'welcome',
        'google_api_key': load_api_key()
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_session_value(key, default=None):
    """세션 상태 값 안전하게 가져오기"""
    return st.session_state.get(key, default)


def set_session_value(key, value):
    """세션 상태 값 설정"""
    st.session_state[key] = value


def is_game_finished():
    """게임이 끝났는지 확인"""
    game_data = get_session_value('game_data')
    current_turn_index = get_session_value('current_turn_index', 0)
    
    if not game_data:
        return False
    
    return current_turn_index >= len(game_data)


def get_current_turn_data():
    """현재 턴 데이터 가져오기"""
    game_data = get_session_value('game_data')
    current_turn_index = get_session_value('current_turn_index', 0)
    
    if not game_data or current_turn_index >= len(game_data):
        return None
    
    return game_data[current_turn_index]


def advance_turn():
    """다음 턴으로 진행"""
    current_index = get_session_value('current_turn_index', 0)
    set_session_value('current_turn_index', current_index + 1)
    
    if is_game_finished():
        set_session_value('current_step', 'result')
