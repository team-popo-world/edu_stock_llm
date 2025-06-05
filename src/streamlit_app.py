
import streamlit as st

# 페이지 설정 (반드시 첫 번째로 실행되어야 함)
st.set_page_config(
    page_title="EduStock",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import os
import sys
import json
from datetime import datetime

# 현재 디렉토리를 패스에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.utils.config import load_api_key
from src.utils.file_manager import SCENARIO_TYPES, get_available_scenarios, load_scenario_from_file, DATA_DIR
from src.game.game_logic import generate_game_scenario_data_llm, initialize_new_game, reset_game_state, calculate_total_assets, process_investment
from src.game.session_manager import get_current_turn_data, advance_turn
from src.ui.components import create_metric_card, create_news_card, create_stock_card, create_investment_history_chart
import plotly.graph_objects as go


def get_custom_css():
    """CSS 스타일 반환"""
    return """
    <style>
        .main > div { padding-top: 2rem; padding-bottom: 2rem; }
        .card { background: white; border-radius: 12px; padding: 1.5rem; 
                box-shadow: 0 2px 12px rgba(0,0,0,0.08); border: 1px solid #f0f0f0; margin: 1rem 0; }
        .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                           color: white; border: none; border-radius: 8px; padding: 0.75rem 2rem;
                           font-weight: 500; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); }
        .metric-card { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                      border-radius: 10px; padding: 1rem; text-align: center; margin: 0.5rem 0; }
        .news-card { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                    border-radius: 10px; padding: 1.5rem; margin: 1rem 0; }
        .stock-card { background: white; border: 2px solid #f8f9fa; border-radius: 12px;
                     padding: 1.5rem; margin: 1rem 0; transition: all 0.3s ease; }
        .stDeployButton {display:none;} footer {visibility: hidden;} .stApp > header {visibility: hidden;}
    </style>
    """


def initialize_session_state():
    """세션 상태 초기화"""
    defaults = {
        'game_data': None, 'current_turn_index': 0, 'player_investments': {},
        'player_balance': 1000, 'investment_history': [], 'game_log': [],
        'game_started': False, 'current_step': 'welcome', 'google_api_key': load_api_key()
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def main():
    """메인 애플리케이션 함수"""
    # CSS 스타일 적용
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 현재 스텝에 따른 화면 표시
    current_step = st.session_state.get('current_step', 'welcome')
    
    if current_step == 'welcome':
        show_welcome_screen()
    elif current_step == 'setup':
        show_setup_screen()
    elif current_step == 'game':
        show_game_screen()
    elif current_step == 'result':
        show_result_screen()


def show_welcome_screen():
    """환영 화면"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 3rem;">
            <h2>🎮 게임 방법</h2>
            <br>
            <div style="text-align: left; margin: 2rem 0;">
                <p>🎯 <strong>목표:</strong> 1000코인으로 시작해서 투자를 통해 돈을 늘려보세요!</p>
                <p>📰 <strong>방법:</strong> 매 턴마다 나오는 뉴스를 보고 어떤 주식을 살지 결정하세요</p>
                <p>💡 <strong>팁:</strong> 뉴스를 잘 읽고 힌트를 활용해보세요</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 게임 시작하기", use_container_width=True):
            st.session_state.current_step = 'setup'
            st.rerun()


def show_setup_screen():
    """설정 화면"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎭 게임 테마 선택")
        selected_theme = st.radio(
            "어떤 모험을 시작할까요?",
            options=list(SCENARIO_TYPES.keys()),
            index=0
        )
        
        st.markdown("### 🎲 게임 모드")
        game_mode = st.radio(
            "게임 모드를 선택하세요",
            options=["새 게임 시작", "저장된 게임 불러오기"]
        )
        
        # API 키 확인
        if not st.session_state.google_api_key and game_mode == "새 게임 시작":
            st.warning("⚠️ API 키가 필요합니다. 환경변수에 GOOGLE_API_KEY를 설정해주세요")
            manual_key = st.text_input("또는 여기에 직접 입력:", type="password")
            if manual_key:
                st.session_state.google_api_key = manual_key
        
        # 저장된 게임 불러오기 옵션
        selected_file = None
        if game_mode == "저장된 게임 불러오기":
            available_files = get_available_scenarios()
            if available_files:
                selected_file = st.selectbox("불러올 게임을 선택하세요:", available_files)
            else:
                st.warning("저장된 게임이 없어요. 새 게임을 시작해주세요.")
        
        if st.button("다음 단계", use_container_width=True):
            handle_setup_button(game_mode, selected_theme, selected_file)


def handle_setup_button(game_mode, selected_theme, selected_file):
    """설정 화면 버튼 처리"""
    if game_mode == "새 게임 시작":
        if st.session_state.google_api_key:
            with st.spinner("🎮 게임 세상을 만들고 있어요..."):
                scenario_type = SCENARIO_TYPES[selected_theme]
                game_data = generate_game_scenario_data_llm(scenario_type, st.session_state.google_api_key)
                
                if game_data:
                    initialize_new_game(game_data, scenario_type)
                    st.success("게임 세상이 완성되었어요! 🎉")
                    st.rerun()
                else:
                    st.error("게임 생성에 실패했어요.")
        else:
            st.error("API 키를 먼저 설정해주세요.")
    else:
        if selected_file:
            game_data = load_scenario_from_file(os.path.join(DATA_DIR, selected_file))
            if game_data:
                initialize_new_game(game_data, "loaded")
                st.success("게임을 불러왔어요! 🎉")
                st.rerun()
            else:
                st.error("게임 파일을 읽을 수 없어요.")


def show_game_screen():
    """게임 화면"""
    if not st.session_state.game_data:
        st.error("게임 데이터가 없습니다.")
        return
    
    current_turn_data = get_current_turn_data()
    if not current_turn_data:
        st.session_state.current_step = 'result'
        st.rerun()
        return
    
    # 턴 데이터 유효성 검사
    if 'stocks' not in current_turn_data or not current_turn_data['stocks']:
        st.error("게임 데이터에 문제가 있습니다. 새 게임을 시작해주세요.")
        return
    
    turn_number = current_turn_data.get('turn', st.session_state.current_turn_index + 1)
    
    # 상단 정보 표시
    display_game_status(turn_number, len(st.session_state.game_data), current_turn_data)
    
    # 뉴스 카드
    st.markdown(create_news_card(current_turn_data), unsafe_allow_html=True)
    
    # 투자 폼
    display_investment_form(current_turn_data, turn_number)


def display_game_status(turn_number, total_turns, current_turn_data):
    """게임 상태 정보 표시"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card(f"총 {total_turns}턴", f"턴 {turn_number}"), unsafe_allow_html=True)
    
    with col2:
        balance = st.session_state.player_balance
        st.markdown(create_metric_card("보유 코인", f"💰 {balance}"), unsafe_allow_html=True)
    
    with col3:
        total_assets = calculate_total_assets(current_turn_data)
        st.markdown(create_metric_card("총 자산", f"📊 {total_assets:.0f}"), unsafe_allow_html=True)


def display_investment_form(current_turn_data, turn_number):
    """투자 폼 표시"""
    st.markdown("### 📈 투자 선택")
    
    with st.form(key=f"investment_form_{turn_number}"):
        investment_inputs = {}
        
        for stock in current_turn_data['stocks']:
            st.markdown(create_stock_card(stock), unsafe_allow_html=True)
            
            current_shares = st.session_state.player_investments.get(stock['name'], 0)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"현재 보유: {current_shares}주")
            with col2:
                max_buy = int(st.session_state.player_balance // stock['current_value']) if stock['current_value'] > 0 else 0
                investment_inputs[stock['name']] = st.number_input(
                    f"매수(+)/매도(-) 수량",
                    min_value=int(-current_shares),
                    max_value=int(max_buy + current_shares),
                    value=0,
                    step=1,
                    key=f"invest_{stock['name']}_{turn_number}",
                    help=f"최대 매수 가능: {max_buy}주"
                )
        
        # 투자 실행 버튼
        if st.form_submit_button("💼 투자 실행", use_container_width=True):
            if process_investment(investment_inputs, current_turn_data, turn_number):
                advance_turn()
                st.rerun()


def show_result_screen():
    """결과 화면"""
    st.markdown("### 🎉 게임 완료!")
    
    investment_history = st.session_state.get('investment_history', [])
    if not investment_history:
        show_error_result()
        return
    
    display_final_results(investment_history)
    display_investment_chart(investment_history)
    display_restart_buttons()


def show_error_result():
    """에러 상황 결과 화면"""
    st.error("게임 데이터가 없습니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 새 게임 시작", key="restart_new", use_container_width=True):
            reset_game_state()
            st.session_state.current_step = 'welcome'
            st.rerun()
    
    with col2:
        if st.button("⚙️ 게임 설정으로", key="restart_setup", use_container_width=True):
            st.session_state.current_step = 'setup'
            st.rerun()


def display_final_results(investment_history):
    """최종 결과 표시"""
    final_assets = investment_history[-1]['total_asset_value']
    initial_assets = 1000
    profit = final_assets - initial_assets
    profit_rate = (profit / initial_assets) * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card("최종 자산", f"💰 {final_assets:.0f}"), unsafe_allow_html=True)
    
    with col2:
        color = "green" if profit >= 0 else "red"
        icon = "📈" if profit >= 0 else "📉"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {color};">{icon} {profit:+.0f}</h3>
            <p>수익/손실</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {color};">{profit_rate:+.1f}%</h3>
            <p>수익률</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 성과 메시지
    display_performance_message(profit)


def display_performance_message(profit):
    """성과 메시지 표시"""
    if profit > 20:
        st.success("🏆 대박! 정말 훌륭한 투자였어요!")
    elif profit > 0:
        st.success("👍 잘했어요! 수익을 냈네요!")
    elif profit > -10:
        st.info("😊 아쉽지만 나쁘지 않아요!")
    else:
        st.warning("😅 다음엔 더 잘할 수 있을 거예요!")


def display_investment_chart(investment_history):
    """투자 히스토리 차트 표시"""
    if len(investment_history) > 1:
        st.markdown("### 📊 내 투자 여정")
        fig = create_investment_history_chart(investment_history)
        if fig:
            st.plotly_chart(fig, use_container_width=True)


def display_restart_buttons():
    """재시작 버튼들 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 새 게임 시작", key="final_restart_new", use_container_width=True):
            reset_game_state()
            st.session_state.current_step = 'welcome'
            st.rerun()
    
    with col2:
        if st.button("⚙️ 다른 테마로 플레이", key="final_restart_theme", use_container_width=True):
            reset_game_state()
            st.session_state.current_step = 'setup'
            st.rerun()


if __name__ == "__main__":
    main()
