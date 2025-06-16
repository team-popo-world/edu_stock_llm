import streamlit as st
from src.utils.config import load_api_key
from src.ai.agents.mentor_agent import InvestmentMentorAgent
from src.ai.player_profile import PlayerProfile


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
        'google_api_key': load_api_key(),
        # AI 멘토 관련 추가
        'mentor_agent': None,
        'player_profile': None,
        'mentor_enabled': True,
        'show_mentor_advice': False
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def initialize_mentor_agent(player_id: str = "default_player"):
    """AI 멘토 초기화"""
    if st.session_state.get('mentor_agent') is None:
        try:
            # 기존 프로필 로드 또는 새 프로필 생성
            mentor_agent = InvestmentMentorAgent.load_profile(player_id=player_id)
            st.session_state.mentor_agent = mentor_agent
            st.session_state.player_profile = mentor_agent.player_profile
        except Exception as e:
            st.error(f"AI 멘토 초기화 실패: {e}")
            # 기본 프로필로 폴백
            profile = PlayerProfile(player_id=player_id)
            st.session_state.mentor_agent = InvestmentMentorAgent(profile)
            st.session_state.player_profile = profile


def get_mentor_agent() -> InvestmentMentorAgent:
    """멘토 에이전트 가져오기"""
    if st.session_state.get('mentor_agent') is None:
        initialize_mentor_agent()
    return st.session_state.mentor_agent


def update_player_action(action_type: str, stock_name: str, shares: int, price: float, turn_number: int):
    """플레이어 행동 업데이트"""
    if st.session_state.get('mentor_enabled', True):
        mentor_agent = get_mentor_agent()
        if mentor_agent:
            mentor_agent.update_player_action(action_type, stock_name, shares, price, turn_number)


def get_mentor_advice(current_turn_data, player_investments, player_balance, turn_number):
    """멘토 조언 가져오기"""
    if not st.session_state.get('mentor_enabled', True):
        return None
    
    mentor_agent = get_mentor_agent()
    if not mentor_agent:
        return None
    
    try:
        # 현재 상황 분석
        situation_analysis = mentor_agent.analyze_current_situation(
            current_turn_data, player_investments, player_balance, turn_number
        )
        
        # 개인맞춤형 조언 생성
        advice = mentor_agent.generate_personalized_advice(situation_analysis, current_turn_data)
        
        return {
            "advice": advice,
            "analysis": situation_analysis
        }
    except Exception as e:
        st.error(f"멘토 조언 생성 실패: {e}")
        return None


def save_player_progress():
    """플레이어 진행상황 저장"""
    mentor_agent = get_mentor_agent()
    if mentor_agent:
        try:
            mentor_agent.save_profile()
        except Exception as e:
            st.warning(f"진행상황 저장 실패: {e}")


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


def get_session_value(key, default=None):
    """세션 상태 값 안전하게 가져오기"""
    return st.session_state.get(key, default)


def set_session_value(key, value):
    """세션 상태 값 설정"""
    st.session_state[key] = value
