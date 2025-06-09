
import streamlit as st
import os
from src.ui.components import (
    create_metric_card, create_news_card, create_stock_card, 
    display_api_key_warning, display_game_intro, create_investment_history_chart
)
from src.game.game_logic import (
    generate_game_scenario_data_llm, process_investment, 
    initialize_new_game, reset_game_state, calculate_total_assets
)
from src.game.session_manager import (
    get_session_value, set_session_value, get_current_turn_data, advance_turn
)
from src.utils.file_manager import (
    SCENARIO_TYPES, get_available_scenarios, load_scenario_from_file, DATA_DIR
)


def show_welcome_screen():
    """환영 화면 - 미니멀하고 깔끔하게"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(display_game_intro(), unsafe_allow_html=True)
        
        if st.button("🚀 게임 시작하기", key=f"start_game_{get_session_value('current_step', 'welcome')}", use_container_width=True):
            set_session_value('current_step', 'setup')
            st.rerun()


def show_setup_screen():
    """설정 화면 - 간단한 선택"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎭 게임 테마 선택")
        
        # 테마 선택을 카드 형식으로
        selected_theme = st.radio(
            "어떤 모험을 시작할까요?",
            options=list(SCENARIO_TYPES.keys()),
            index=0,
            key="theme_selection"
        )
        
        st.markdown("### 🎲 게임 모드")
        game_mode = st.radio(
            "게임 모드를 선택하세요",
            options=["새 게임 시작", "저장된 게임 불러오기"],
            key="mode_selection"
        )
        
        # API 키 확인
        google_api_key = get_session_value('google_api_key')
        if not google_api_key and game_mode == "새 게임 시작":
            display_api_key_warning()
            manual_key = st.text_input("또는 여기에 직접 입력:", type="password")
            if manual_key:
                set_session_value('google_api_key', manual_key)
        
        # 저장된 게임 불러오기 옵션
        selected_file = None
        if game_mode == "저장된 게임 불러오기":
            available_files = get_available_scenarios()
            if available_files:
                selected_file = st.selectbox("불러올 게임을 선택하세요:", available_files)
            else:
                st.warning("저장된 게임이 없어요. 새 게임을 시작해주세요.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 버튼 처리
        if st.button("다음 단계", use_container_width=True):
            _handle_setup_button_click(game_mode, selected_theme, selected_file)


def _handle_setup_button_click(game_mode, selected_theme, selected_file):
    """설정 화면 버튼 클릭 처리"""
    if game_mode == "새 게임 시작":
        google_api_key = get_session_value('google_api_key')
        if google_api_key:
            with st.spinner("🎮 게임 세상을 만들고 있어요...(약 1-2분 소요..)"):
                scenario_type = SCENARIO_TYPES[selected_theme]
                game_data = generate_game_scenario_data_llm(scenario_type, google_api_key)
                
                if game_data:
                    initialize_new_game(game_data, scenario_type)
                    st.success("게임 세상이 완성되었어요! 🎉")
                    st.rerun()
                else:
                    st.error("게임 생성에 실패했어요. 다시 시도해주세요.")
        else:
            st.error("API 키를 먼저 설정해주세요.")
    else:
        # 저장된 게임 불러오기
        if selected_file:
            game_data = load_scenario_from_file(os.path.join(DATA_DIR, selected_file))
            if game_data:
                initialize_new_game(game_data, "loaded")
                st.success("게임을 불러왔어요! 🎉")
                st.rerun()
            else:
                st.error("게임 파일을 읽을 수 없어요.")
        else:
            st.warning("먼저 불러올 게임을 선택해주세요.")


def show_game_screen():
    """게임 화면 - 깔끔하고 직관적"""
    game_data = get_session_value('game_data')
    if not game_data:
        st.error("게임 데이터가 없습니다.")
        return
    
    current_turn_data = get_current_turn_data()
    if not current_turn_data:
        set_session_value('current_step', 'result')
        st.rerun()
        return
    
    # 턴 데이터 유효성 검사
    if 'stocks' not in current_turn_data or not current_turn_data['stocks']:
        st.error("게임 데이터에 문제가 있습니다. 새 게임을 시작해주세요.")
        return
    
    turn_number = current_turn_data.get('turn', get_session_value('current_turn_index', 0) + 1)
    
    # 상단 정보 표시
    _display_game_status(turn_number, len(game_data), current_turn_data)
    
    # 뉴스 카드
    st.markdown(create_news_card(current_turn_data), unsafe_allow_html=True)
    
    # 투자 폼
    _display_investment_form(current_turn_data, turn_number)


def _display_game_status(turn_number, total_turns, current_turn_data):
    """게임 상태 정보 표시"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card(f"총 {total_turns}턴", f"턴 {turn_number}"), unsafe_allow_html=True)
    
    with col2:
        balance = get_session_value('player_balance', 1000)
        st.markdown(create_metric_card("보유 코인", f"💰 {balance}"), unsafe_allow_html=True)
    
    with col3:
        total_assets = calculate_total_assets(current_turn_data)
        st.markdown(create_metric_card("총 자산", f"📊 {total_assets:.0f}"), unsafe_allow_html=True)


def _display_investment_form(current_turn_data, turn_number):
    """투자 폼 표시"""
    st.markdown("### 📈 투자 선택")
    
    with st.form(key=f"investment_form_{turn_number}"):
        investment_inputs = {}
        
        for stock in current_turn_data['stocks']:
            st.markdown(create_stock_card(stock), unsafe_allow_html=True)
            
            current_shares = get_session_value('player_investments', {}).get(stock['name'], 0)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"현재 보유: {current_shares}주")
            with col2:
                max_buy = int(get_session_value('player_balance', 0) // stock['current_value']) if stock['current_value'] > 0 else 0
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
    """결과 화면 - 성과 요약"""
    st.markdown("### 🎉 게임 완료!")
    
    investment_history = get_session_value('investment_history', [])
    if not investment_history:
        _show_error_result()
        return
    
    _display_final_results(investment_history)
    _display_investment_chart(investment_history)
    _display_restart_buttons()


def _show_error_result():
    """에러 상황 결과 화면"""
    st.error("게임 데이터가 없습니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 새 게임 시작", use_container_width=True):
            reset_game_state()
            set_session_value('current_step', 'welcome')
            st.rerun()
    
    with col2:
        if st.button("⚙️ 게임 설정으로", use_container_width=True):
            set_session_value('current_step', 'setup')
            st.rerun()


def _display_final_results(investment_history):
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
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 2px solid #dee2e6; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; text-align: center;">
            <h3 style="margin: 0 0 0.5rem 0; color: {color};">{icon} {profit:+.0f}</h3>
            <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">수익/손실</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 2px solid #dee2e6; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; text-align: center;">
            <h3 style="margin: 0 0 0.5rem 0; color: {color};">{profit_rate:+.1f}%</h3>
            <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">수익률</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 성과 메시지
    _display_performance_message(profit)


def _display_performance_message(profit):
    """성과 메시지 표시"""
    if profit > 20:
        st.success("🏆 대박! 정말 훌륭한 투자였어요!")
    elif profit > 0:
        st.success("👍 잘했어요! 수익을 냈네요!")
    elif profit > -10:
        st.info("😊 아쉽지만 나쁘지 않아요!")
    else:
        st.warning("😅 다음엔 더 잘할 수 있을 거예요!")


def _display_investment_chart(investment_history):
    """투자 히스토리 차트 표시"""
    if len(investment_history) > 1:
        st.markdown("### 📊 내 투자 여정")
        fig = create_investment_history_chart(investment_history)
        if fig:
            st.plotly_chart(fig, use_container_width=True)


def _display_restart_buttons():
    """재시작 버튼들 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 새 게임 시작", use_container_width=True):
            reset_game_state()
            set_session_value('current_step', 'welcome')
            st.rerun()
    
    with col2:
        if st.button("⚙️ 다른 테마로 플레이", use_container_width=True):
            reset_game_state()
            set_session_value('current_step', 'setup')
            st.rerun()
