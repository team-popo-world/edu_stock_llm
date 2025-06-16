import streamlit as st
import json
import os
from src.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
from src.utils.prompts import get_system_prompt, get_game_scenario_prompt
from src.utils.file_manager import save_scenario_to_file, generate_filename
from src.game.session_manager import update_player_action, get_mentor_advice


@st.cache_data(ttl=3600)
def generate_game_scenario_data_llm(scenario_type: str, google_api_key: str):
    """LLM을 사용하여 게임 시나리오 데이터 생성"""
    if not google_api_key:
        return None

    try:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        llm = initialize_llm()
        system_prompt_str = get_system_prompt()
        prompt_template = create_prompt_template(system_prompt_str)
        game_prompt_str = get_game_scenario_prompt(scenario_type)
        
        json_content = generate_game_data(llm, prompt_template, game_prompt_str)
        
        if json_content:
            try:
                raw_json_output = json_content
                if raw_json_output.startswith("```json\n"):
                    raw_json_output = raw_json_output[7:]
                if raw_json_output.endswith("\n```"):
                    raw_json_output = raw_json_output[:-4]
                
                game_data = json.loads(raw_json_output)
                
                # 데이터 유효성 검사
                if not isinstance(game_data, list) or len(game_data) == 0:
                    st.error("생성된 게임 데이터가 올바르지 않습니다.")
                    return None
                
                return game_data
            except json.JSONDecodeError as e:
                st.error(f"게임 데이터 파싱 실패: {e}")
                return None
        else:
            return None
            
    except Exception as e:
        st.error(f"시나리오 생성 실패: {e}")
        return None


def calculate_total_assets(current_turn_data):
    """현재 총 자산 계산"""
    total_assets = st.session_state.player_balance
    for stock_name, shares in st.session_state.player_investments.items():
        if shares > 0:  # 양수인 주식만 계산
            stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
            if stock_info:
                total_assets += shares * stock_info['current_value']
    return total_assets


def process_investment(investment_inputs, current_turn_data, turn_number):
    """투자 처리 로직"""
    total_cost = 0
    
    # 총 비용 계산 (매수만)
    for stock_name, shares_change in investment_inputs.items():
        if shares_change > 0:  # 매수만 비용 계산
            stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
            if stock_info:
                total_cost += shares_change * stock_info['current_value']
    
    # 잔액 확인 (매수 비용만)
    if total_cost > st.session_state.player_balance:
        st.error("💸 코인이 부족해요!")
        return False
    
    # 투자 실행
    actions = []
    for stock_name, shares_change in investment_inputs.items():
        if shares_change != 0:
            stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
            if stock_info:
                cost = shares_change * stock_info['current_value']
                st.session_state.player_balance -= cost
                
                current_shares = st.session_state.player_investments.get(stock_name, 0)
                st.session_state.player_investments[stock_name] = current_shares + shares_change
                
                action_type = "매수" if shares_change > 0 else "매도"
                action_type_en = "buy" if shares_change > 0 else "sell"
                actions.append(f"{stock_name} {abs(shares_change)}주 {action_type}")
                
                # AI 멘토에게 행동 기록
                update_player_action(
                    action_type_en, 
                    stock_name, 
                    abs(shares_change), 
                    stock_info['current_value'], 
                    turn_number
                )
    
    # 변화가 없는 경우 hold 액션 기록
    if not actions:
        update_player_action("hold", "none", 0, 0, turn_number)
    
    if actions:
        st.success(f"✅ 투자 완료: {', '.join(actions)}")
    else:
        st.info("변경사항이 없어요.")
    
    # 히스토리 기록
    total_assets = calculate_total_assets(current_turn_data)
    
    st.session_state.investment_history.append({
        'turn': turn_number,
        'balance': st.session_state.player_balance,
        'total_asset_value': total_assets,
        'investments': dict(st.session_state.player_investments)
    })
    
    return True


def initialize_new_game(game_data, scenario_type):
    """새 게임 초기화"""
    st.session_state.game_data = game_data
    filename = generate_filename(scenario_type)
    save_scenario_to_file(game_data, filename)
    
    # 게임 상태 초기화
    st.session_state.current_turn_index = 0
    st.session_state.player_investments = {}
    st.session_state.player_balance = 1000
    st.session_state.investment_history = []
    st.session_state.game_log = []
    st.session_state.game_started = True
    st.session_state.current_step = 'game'


def reset_game_state():
    """게임 상태 초기화"""
    keys_to_reset = ['game_data', 'current_turn_index', 'player_investments', 
                     'player_balance', 'investment_history', 'game_log', 'game_started']
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
