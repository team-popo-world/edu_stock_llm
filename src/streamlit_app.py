import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from src.utils.prompts import get_system_prompt, get_game_scenario_prompt
from src.simulation.simulator import run_automated_simulation
from src.utils.config import load_api_key

# 페이지 설정
st.set_page_config(
    page_title="EduStock",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 스타일링 - 미니멀 디자인
st.markdown("""
<style>
    /* 메인 컨테이너 */
    .main > div {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 헤더 스타일 */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 3rem;
    }
    
    /* 카드 스타일 */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin: 1rem 0;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* 주식 카드 */
    .stock-card {
        background: white;
        border: 2px solid #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
    }
    
    /* 성공 메시지 */
    .success-message {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* 뉴스 카드 */
    .news-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* 스텝 인디케이터 */
    .step-indicator {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .step {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #e9ecef;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 0.5rem;
        font-weight: bold;
    }
    
    .step.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .step.completed {
        background: #28a745;
        color: white;
    }
    
    /* 숨기기 */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 유틸리티 함수들
def create_simple_stock_plot(game_data, title="주식 가치 변화"):
    """간단하고 깔끔한 주식 차트 생성"""
    if not game_data:
        return None
    
    turns = []
    stock_data = {}
    
    for turn in game_data:
        turn_num = turn.get('turn', turn.get('turn_number', 0))
        turns.append(turn_num)
        
        if 'stocks' in turn:
            for stock in turn['stocks']:
                stock_name = stock.get('name', '')
                stock_value = stock.get('current_value', 0)
                
                if stock_name not in stock_data:
                    stock_data[stock_name] = []
                stock_data[stock_name].append(stock_value)
    
    fig = go.Figure()
    
    colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a']
    for i, (stock_name, values) in enumerate(stock_data.items()):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=turns,
            y=values,
            mode='lines+markers',
            name=stock_name,
            line=dict(color=color, width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="턴",
        yaxis_title="가치 (코인)",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        font=dict(family="Arial, sans-serif", size=12)
    )
    
    return fig

# 데이터 디렉토리 설정
DATA_DIR = "data"
VISUALIZATION_DIR = "visualization_results"
DEFAULT_SCENARIO_TYPE = "magic_kingdom"
SCENARIO_TYPES = {
    "🏰 마법 왕국": "magic_kingdom",
    "🚚 푸드트럭 왕국": "foodtruck_kingdom", 
    "🌙 달빛 도둑": "moonlight_thief"
}

def ensure_dir(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

ensure_dir(DATA_DIR)
ensure_dir(VISUALIZATION_DIR)

def generate_filename(scenario_type, prefix="game_scenario"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(DATA_DIR, f"{prefix}_{scenario_type}_{timestamp}.json")

def save_scenario_to_file(scenario_data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(scenario_data, f, ensure_ascii=False, indent=2)

def load_scenario_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def get_available_scenarios(data_dir=DATA_DIR):
    files = [f for f in os.listdir(data_dir) if f.startswith("game_scenario_") and f.endswith(".json")]
    return sorted(files, reverse=True)

@st.cache_data(ttl=3600)
def generate_game_scenario_data_llm(scenario_type: str, openai_api_key: str):
    if not openai_api_key:
        return None

    try:
        from src.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
        
        os.environ["OPENAI_API_KEY"] = openai_api_key
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

# 세션 상태 초기화
if 'game_data' not in st.session_state:
    st.session_state.game_data = None
if 'current_turn_index' not in st.session_state:
    st.session_state.current_turn_index = 0
if 'player_investments' not in st.session_state:
    st.session_state.player_investments = {}
if 'player_balance' not in st.session_state:
    st.session_state.player_balance = 1000
if 'investment_history' not in st.session_state:
    st.session_state.investment_history = []
if 'game_log' not in st.session_state:
    st.session_state.game_log = []
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'welcome'
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = load_api_key()

# 메인 앱 시작
def main():

    # 현재 스텝에 따른 화면 표시
    if st.session_state.current_step == 'welcome':
        show_welcome_screen()
    elif st.session_state.current_step == 'setup':
        show_setup_screen()
    elif st.session_state.current_step == 'game':
        show_game_screen()
    elif st.session_state.current_step == 'result':
        show_result_screen()

def show_welcome_screen():
    """환영 화면 - 미니멀하고 깔끔하게"""
    
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
            <br>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 게임 시작하기", key="start_game", use_container_width=True):
            st.session_state.current_step = 'setup'
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
        
        # API 키 확인 (카드 안에 포함)
        if not st.session_state.openai_api_key and game_mode == "새 게임 시작":
            st.markdown("""
            <div style="background: #fff3cd; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                ⚠️ <strong>API 키가 필요합니다</strong><br>
                환경변수에 OPENAI_API_KEY를 설정해주세요
            </div>
            """, unsafe_allow_html=True)
            
            manual_key = st.text_input("또는 여기에 직접 입력:", type="password")
            if manual_key:
                st.session_state.openai_api_key = manual_key
        
        # 저장된 게임 불러오기 옵션 (카드 안에 포함)
        if game_mode == "저장된 게임 불러오기":
            available_files = get_available_scenarios()
            if available_files:
                selected_file = st.selectbox("불러올 게임을 선택하세요:", available_files)
            else:
                st.warning("저장된 게임이 없어요. 새 게임을 시작해주세요.")
        
        # 다음 단계 버튼 (카드 안에 포함)
        st.markdown("<br>", unsafe_allow_html=True)  # 여백 추가
        
        
        # 버튼 처리
        if st.button("다음 단계", use_container_width=True):
            if game_mode == "새 게임 시작":
                if st.session_state.openai_api_key:
                    # 게임 데이터 생성
                    with st.spinner("🎮 게임 세상을 만들고 있어요...(약 1-2분 소요..)"):
                        scenario_type = SCENARIO_TYPES[selected_theme]
                        game_data = generate_game_scenario_data_llm(scenario_type, st.session_state.openai_api_key)
                        
                        if game_data:
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
                            
                            st.success("게임 세상이 완성되었어요! 🎉")
                            st.rerun()
                        else:
                            st.error("게임 생성에 실패했어요. 다시 시도해주세요.")
                else:
                    st.error("API 키를 먼저 설정해주세요.")
            else:
                # 저장된 게임 불러오기
                available_files = get_available_scenarios()
                if available_files and 'selected_file' in locals():
                    game_data = load_scenario_from_file(os.path.join(DATA_DIR, selected_file))
                    if game_data:
                        st.session_state.game_data = game_data
                        
                        # 게임 상태 초기화
                        st.session_state.current_turn_index = 0
                        st.session_state.player_investments = {}
                        st.session_state.player_balance = 1000
                        st.session_state.investment_history = []
                        st.session_state.game_log = []
                        st.session_state.game_started = True
                        st.session_state.current_step = 'game'
                        
                        st.success("게임을 불러왔어요! 🎉")
                        st.rerun()
                    else:
                        st.error("게임 파일을 읽을 수 없어요.")
                else:
                    st.warning("먼저 불러올 게임을 선택해주세요.")

def show_game_screen():
    """게임 화면 - 깔끔하고 직관적"""
    
    if not st.session_state.game_data:
        st.error("게임 데이터가 없습니다.")
        return
    
    game_data = st.session_state.game_data
    current_turn_index = st.session_state.current_turn_index
    
    # 게임 종료 체크
    if current_turn_index >= len(game_data):
        st.session_state.current_step = 'result'
        st.rerun()
        return
    
    current_turn_data = game_data[current_turn_index]
    turn_number = current_turn_data.get('turn', current_turn_index + 1)
    
    # 턴 데이터 유효성 검사
    if 'stocks' not in current_turn_data or not current_turn_data['stocks']:
        st.error("게임 데이터에 문제가 있습니다. 새 게임을 시작해주세요.")
        return
    
    # 상단 정보 카드
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>턴 {turn_number}</h3>
            <p>총 {len(game_data)}턴</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 {st.session_state.player_balance}</h3>
            <p>보유 코인</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # 총 자산 계산
        total_assets = st.session_state.player_balance
        for stock_name, shares in st.session_state.player_investments.items():
            if shares > 0:  # 양수인 주식만 계산
                stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
                if stock_info:
                    total_assets += shares * stock_info['current_value']
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 {total_assets:.0f}</h3>
            <p>총 자산</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 뉴스 카드
    st.markdown(f"""
    <div class="news-card">
        <h3>📰 이번 턴 소식</h3>
        <p><strong>결과:</strong> {current_turn_data.get('result', '결과 정보 없음')}</p>
        <p><strong>뉴스:</strong> {current_turn_data.get('news', '뉴스 정보 없음')}</p>
        <p><em>💡 힌트: {current_turn_data.get('news_hint', '힌트 정보 없음')}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 주식 카드들
    st.markdown("### 📈 투자 선택")
    
    with st.form(key=f"investment_form_{turn_number}"):
        investment_inputs = {}
        
        for stock in current_turn_data['stocks']:
            st.markdown(f"""
            <div class="stock-card">
                <h4>{stock.get('name', '이름 없음')}</h4>
                <p style="color: #666;">{stock.get('description', '설명 없음')}</p>
                <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                    <div>
                        <strong>{stock.get('current_value', 0)} 코인</strong>
                        <small style="color: #888;">현재 가격</small>
                    </div>
                    <div style="text-align: right;">
                        <small style="color: #888;">위험도: {stock.get('risk_level', '정보 없음')}</small><br>
                        <small style="color: #666;">예상: {stock.get('expectation', '정보 없음')}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            current_shares = st.session_state.player_investments.get(stock['name'], 0)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"현재 보유: {current_shares}주")
            with col2:
                max_buy = st.session_state.player_balance // stock['current_value'] if stock['current_value'] > 0 else 0
                investment_inputs[stock['name']] = st.number_input(
                    f"매수(+)/매도(-) 수량",
                    min_value=-current_shares,
                    max_value=max_buy + current_shares,  # 현재 보유 + 최대 매수 가능
                    value=0,
                    step=1,
                    key=f"invest_{stock['name']}_{turn_number}",
                    help=f"최대 매수 가능: {max_buy}주"
                )
        
        # 투자 실행 버튼
        if st.form_submit_button("💼 투자 실행", use_container_width=True):
            process_investment(investment_inputs, current_turn_data, turn_number)

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
        return
    
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
                actions.append(f"{stock_name} {abs(shares_change)}주 {action_type}")
    
    if actions:
        st.success(f"✅ 투자 완료: {', '.join(actions)}")
    else:
        st.info("변경사항이 없어요.")
    
    # 히스토리 기록
    total_assets = st.session_state.player_balance
    for stock_name, shares in st.session_state.player_investments.items():
        if shares > 0:
            stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
            if stock_info:
                total_assets += shares * stock_info['current_value']
    
    st.session_state.investment_history.append({
        'turn': turn_number,
        'balance': st.session_state.player_balance,
        'total_asset_value': total_assets,
        'investments': dict(st.session_state.player_investments)
    })
    
    # 다음 턴으로
    st.session_state.current_turn_index += 1
    
    # 자동으로 다음 화면으로
    if st.session_state.current_turn_index >= len(st.session_state.game_data):
        st.session_state.current_step = 'result'
    
    st.rerun()

def show_result_screen():
    """결과 화면 - 성과 요약"""
    
    st.markdown("### 🎉 게임 완료!")
    
    if not st.session_state.investment_history:
        st.error("게임 데이터가 없습니다.")
        
        # 에러 상황에서도 사용자가 다시 시작할 수 있는 옵션 제공
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 새 게임 시작", use_container_width=True):
                # 상태 초기화
                for key in ['game_data', 'current_turn_index', 'player_investments', 
                           'player_balance', 'investment_history', 'game_log', 'game_started']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.session_state.current_step = 'welcome'
                st.rerun()
        
        with col2:
            if st.button("⚙️ 게임 설정으로", use_container_width=True):
                st.session_state.current_step = 'setup'
                st.rerun()
        
        return
    
    final_assets = st.session_state.investment_history[-1]['total_asset_value']
    initial_assets = 1000
    profit = final_assets - initial_assets
    profit_rate = (profit / initial_assets) * 100
    
    # 결과 카드
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 {final_assets:.0f}</h3>
            <p>최종 자산</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color = "green" if profit >= 0 else "red"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {color};">{'📈' if profit >= 0 else '📉'} {profit:+.0f}</h3>
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
    if profit > 20:
        st.success("🏆 대박! 정말 훌륭한 투자였어요!")
    elif profit > 0:
        st.success("👍 잘했어요! 수익을 냈네요!")
    elif profit > -10:
        st.info("😊 아쉽지만 나쁘지 않아요!")
    else:
        st.warning("😅 다음엔 더 잘할 수 있을 거예요!")
    
    # 자산 변화 그래프
    if len(st.session_state.investment_history) > 1:
        st.markdown("### 📊 내 투자 여정")
        
        history_df = pd.DataFrame([
            {'턴': h['turn'], '총자산': h['total_asset_value'], '현금': h['balance']} 
            for h in st.session_state.investment_history
        ])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=history_df['턴'], 
            y=history_df['총자산'],
            mode='lines+markers',
            name='총 자산',
            line=dict(color='#667eea', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=history_df['턴'], 
            y=history_df['현금'],
            mode='lines+markers',
            name='현금',
            line=dict(color='#f093fb', width=3)
        ))
        
        fig.update_layout(
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 다시 시작 버튼
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 새 게임 시작", use_container_width=True):
            # 상태 초기화
            for key in ['game_data', 'current_turn_index', 'player_investments', 
                       'player_balance', 'investment_history', 'game_log', 'game_started']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.session_state.current_step = 'welcome'
            st.rerun()
    
    with col2:
        if st.button("⚙️ 다른 테마로 플레이", use_container_width=True):
            # 상태 초기화
            for key in ['game_data', 'current_turn_index', 'player_investments', 
                       'player_balance', 'investment_history', 'game_log', 'game_started']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.session_state.current_step = 'setup'
            st.rerun()

if __name__ == "__main__":
    main()