import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from src.utils.prompts import get_system_prompt, get_game_scenario_prompt
from src.simulation.simulator import run_automated_simulation
from src.utils.config import load_api_key

# --- Helper Functions ---
def create_simple_stock_plot(game_data, title="주식 가치 변화"):
    """Create a simple interactive plot for stock data"""
    if not game_data:
        return None
    
    # Prepare data for plotting
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
    
    # Create plotly figure
    fig = go.Figure()
    
    colors = ['gold', 'brown', 'firebrick', 'blue', 'green']
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
        height=500
    )
    
    return fig

def round_currency(amount):
    """Round currency amounts to avoid floating point precision issues"""
    return round(amount, 2)

# --- Page Configuration ---
st.set_page_config(
    page_title="EduStock LLM Game",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
DATA_DIR = "data"
VISUALIZATION_DIR = "visualization_results"
DEFAULT_SCENARIO_TYPE = "magic_kingdom"
SCENARIO_TYPES = {
    "마법 왕국 🏰": "magic_kingdom",
    "푸드트럭 왕국 🚚": "foodtruck_kingdom",
    "달빛 도둑 🌙": "moonlight_thief"
}

# --- Helper Functions ---
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
    st.success(f"'{filename}' 파일에 시나리오를 저장했습니다.")

def load_scenario_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Pydantic 모델로 변환 (선택 사항이지만, 데이터 유효성 검사에 유용)
        # validated_data = [TurnData(**turn) for turn in data]
        # return validated_data
        return data # 우선은 dict 리스트로 반환
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다: {filename}")
        return None
    except json.JSONDecodeError:
        st.error(f"JSON 디코딩 오류: {filename}")
        return None

def get_available_scenarios(data_dir=DATA_DIR):
    files = [f for f in os.listdir(data_dir) if f.startswith("game_scenario_") and f.endswith(".json")]
    return sorted(files, reverse=True)


# --- LLM Scenario Generation ---
@st.cache_data(ttl=3600) # Cache for 1 hour
def generate_game_scenario_data_llm(scenario_type: str, openai_api_key: str):
    if not openai_api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. 사이드바에서 키를 입력해주세요.")
        return None

    try:
        # 기존 llm_handler 함수들을 사용하여 일관성 유지
        from src.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
        
        # API 키를 환경변수에 설정
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # LLM 초기화
        llm = initialize_llm()
        
        # 프롬프트 템플릿 생성
        system_prompt_str = get_system_prompt()
        prompt_template = create_prompt_template(system_prompt_str)
        
        # 게임 시나리오 프롬프트 생성
        game_prompt_str = get_game_scenario_prompt(scenario_type)
        
        with st.spinner("AI가 게임 시나리오를 생성 중입니다... 잠시만 기다려주세요 ✨"):
            # 기존 generate_game_data 함수 사용
            json_content = generate_game_data(llm, prompt_template, game_prompt_str)
        
        if json_content:
            raw_json_output = json_content
            # 때때로 LLM이 마크다운 코드 블록으로 감싸서 반환하는 경우가 있어 제거
            if raw_json_output.startswith("```json\n"):
                raw_json_output = raw_json_output[7:]
            if raw_json_output.endswith("\n```"):
                raw_json_output = raw_json_output[:-4]
            
            game_data = json.loads(raw_json_output)
            # Pydantic 모델로 변환 시도 (선택적)
            # validated_data = [TurnData(**turn) for turn in game_data]
            # return validated_data
            return game_data # 우선은 dict 리스트로 반환
        else:
            st.error("LLM에서 유효한 JSON 응답을 받지 못했습니다.")
            return None
            
    except json.JSONDecodeError as e:
        st.error(f"LLM으로부터 받은 JSON 응답을 파싱하는 데 실패했습니다: {e}")
        if 'raw_json_output' in locals():
            st.text_area("Raw LLM Output", value=raw_json_output, height=200)
        return None
    except Exception as e:
        st.error(f"시나리오 생성 중 오류 발생: {e}")
        return None

# --- Streamlit App UI ---

# --- Sidebar ---
st.sidebar.title("게임 설정 ⚙️")

# API 키 상태 관리 - 환경변수에서 자동으로 불러오기
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = load_api_key()

# API 키 상태 표시
st.sidebar.header("OpenAI API 상태")
if st.session_state.openai_api_key:
    st.sidebar.success("✅ OpenAI API 키가 환경변수에서 로드되었습니다.")
    # 키의 일부만 표시 (보안상)
    masked_key = st.session_state.openai_api_key[:10] + "..." + st.session_state.openai_api_key[-4:] if len(st.session_state.openai_api_key) > 14 else "키가 설정됨"
    st.sidebar.caption(f"사용 중인 키: {masked_key}")
else:
    st.sidebar.error("❌ OpenAI API 키를 찾을 수 없습니다.")
    st.sidebar.info("💡 다음 방법 중 하나로 API 키를 설정하세요:")
    st.sidebar.markdown("""
    1. 환경변수 설정:
       ```bash
       export OPENAI_API_KEY="your-api-key"
       ```
    
    2. .env 파일에 추가:
       ```
       OPENAI_API_KEY=your-api-key
       ```
    """)
    
    # 긴급 상황용 직접 입력 옵션 (접을 수 있는 형태로)
    with st.sidebar.expander("🔧 API 키 직접 입력 (임시용)"):
        manual_key = st.text_input("API 키를 입력하세요", type="password", help="이 방법은 임시용입니다. 환경변수 설정을 권장합니다.")
        if manual_key:
            st.session_state.openai_api_key = manual_key
            st.success("API 키가 임시로 설정되었습니다.")
            st.rerun()


st.sidebar.header("게임 모드 선택")
game_mode = st.sidebar.radio("모드 선택", ("새 시나리오 생성", "기존 시나리오 불러오기"), key="game_mode_selection")

selected_scenario_display_name = st.sidebar.selectbox(
    "시나리오 테마 선택",
    options=list(SCENARIO_TYPES.keys()),
    index=0,
    key="scenario_theme_selection"
)
selected_scenario_type = SCENARIO_TYPES[selected_scenario_display_name]


# --- Main Page ---
st.title("📊 어린이 주식 투자 학습 게임 🎮")
st.markdown("--- ")

# --- Session State Initialization ---
if 'game_data' not in st.session_state:
    st.session_state.game_data = None
if 'current_turn_index' not in st.session_state:
    st.session_state.current_turn_index = 0
if 'player_investments' not in st.session_state: # {stock_name: amount_invested}
    st.session_state.player_investments = {}
if 'player_balance' not in st.session_state:
    st.session_state.player_balance = 100 # 초기 자금
if 'investment_history' not in st.session_state: # For plotting investment changes
    st.session_state.investment_history = [] # [{'turn': t, 'stock': name, 'value': val, 'type': 'investment'}]
if 'game_log' not in st.session_state:
    st.session_state.game_log = []
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'simulation_results_df' not in st.session_state:
    st.session_state.simulation_results_df = None


# --- Game Logic ---
if game_mode == "새 시나리오 생성":
    st.subheader("✨ 새 게임 시나리오 생성하기")
    if st.button(f"'{selected_scenario_display_name}' 테마로 시나리오 생성 시작", key="generate_new_scenario_button"):
        if not st.session_state.openai_api_key:
            st.error("❌ OpenAI API 키가 설정되지 않았습니다.")
            st.info("💡 사이드바의 'OpenAI API 상태' 섹션을 확인하고 환경변수를 설정해주세요.")
        else:
            st.session_state.game_data = None # Reset previous data
            st.session_state.current_turn_index = 0
            st.session_state.player_investments = {}
            st.session_state.player_balance = 100
            st.session_state.investment_history = []
            st.session_state.game_log = ["새 게임 시작!"]
            st.session_state.game_started = False
            st.session_state.simulation_results_df = None

            generated_data = generate_game_scenario_data_llm(selected_scenario_type, st.session_state.openai_api_key)
            if generated_data:
                st.session_state.game_data = generated_data
                filename = generate_filename(selected_scenario_type)
                save_scenario_to_file(st.session_state.game_data, filename)
                st.success(f"'{selected_scenario_display_name}' 시나리오 생성 완료! 게임을 시작할 수 있습니다.")
                st.balloons()


elif game_mode == "기존 시나리오 불러오기":
    st.subheader("📂 기존 게임 시나리오 불러오기")
    available_files = get_available_scenarios()
    if not available_files:
        st.warning("저장된 시나리오 파일이 없습니다. 먼저 '새 시나리오 생성'을 진행해주세요.")
    else:
        selected_file = st.selectbox("불러올 시나리오 파일을 선택하세요:", available_files, key="load_scenario_file_select")
        if st.button("선택한 시나리오 불러오기", key="load_scenario_button"):
            if selected_file:
                loaded_data = load_scenario_from_file(os.path.join(DATA_DIR, selected_file))
                if loaded_data:
                    st.session_state.game_data = loaded_data
                    st.session_state.current_turn_index = 0
                    st.session_state.player_investments = {}
                    st.session_state.player_balance = 100
                    st.session_state.investment_history = []
                    st.session_state.game_log = [f"'{selected_file}' 게임 시작!"]
                    st.session_state.game_started = False
                    st.session_state.simulation_results_df = None
                    st.success(f"'{selected_file}' 시나리오를 성공적으로 불러왔습니다. 게임을 시작할 수 있습니다.")
                    st.balloons()

# --- Display Game ---
if st.session_state.game_data:
    game_data = st.session_state.game_data
    
    if not st.session_state.game_started:
        if st.button("게임 시작!", key="start_game_button"):
            st.session_state.game_started = True
            st.session_state.current_turn_index = 0
            # Initialize player investments and history for the first turn's stocks
            first_turn_data = game_data[0]
            st.session_state.player_investments = {stock['name']: 0 for stock in first_turn_data['stocks']}
            st.session_state.investment_history.append({
                'turn': 0, # Before first turn
                'balance': st.session_state.player_balance,
                'total_asset_value': st.session_state.player_balance # Initially only balance
            })
            st.rerun() # Rerun to reflect game start

    if st.session_state.game_started:
        current_turn_index = st.session_state.current_turn_index
        
        if current_turn_index < len(game_data):
            current_turn_data = game_data[current_turn_index]
            turn_number = current_turn_data['turn']

            st.header(f"턴 {turn_number} / {len(game_data)}")
            
            # Display Player Balance
            st.subheader(f"💰 나의 자산 현황")
            col_bal, col_asset = st.columns(2)
            col_bal.metric("현재 보유 코인", f"{st.session_state.player_balance} 코인")
            
            total_asset_value = st.session_state.player_balance
            for stock_name, invested_amount in st.session_state.player_investments.items():
                if invested_amount > 0:
                    # Find current value of this stock
                    stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
                    if stock_info:
                        # Assuming invested_amount is number of shares, need initial price to calculate shares
                        # For simplicity, let's assume invested_amount is the *value* invested at purchase time.
                        # This needs refinement if we track shares.
                        # For now, let's assume player_investments stores the *current value* of that stock holding.
                        # This part needs a clearer logic for how shares vs. value are tracked.
                        # Let's assume player_investments stores the number of shares.
                        # We need to know the purchase price to calculate this.
                        # For now, let's simplify: player_investments stores the amount of *coins* invested in that stock.
                        # The value of this investment changes with current_value.
                        # This is still tricky. Let's assume player_investments stores number of shares.
                        # We need to store purchase price or initial value at purchase.

                        # Simplified: Let's track current value of holdings directly.
                        # When buying: player_investments[stock_name] += amount_to_buy (value)
                        # Value update: player_investments[stock_name] *= (current_price / previous_price)
                        # This requires storing previous price.

                        # Simplest for now: player_investments stores number of shares.
                        # initial_buy_prices must be stored somewhere or assumed to be initial_value of the stock.
                        # Let's assume shares were bought at stock['initial_value'] for simplicity in this version.
                        # This is a major simplification and should be improved for a real game.
                        
                        # To avoid overcomplicating now, let's assume player_investments stores the *number of shares*.
                        # And we need to track the price at which they were bought or use a running average.
                        # For this example, let's assume shares are bought at current turn's price.
                        
                        # Let's refine: player_investments = {stock_name: {'shares': X, 'avg_purchase_price': Y}}
                        # For now, let's stick to a simpler model if possible or clearly state assumptions.

                        # Re-simplification: player_investments stores the *value* of the stock they hold, updated each turn.
                        # This means when a stock price changes, the value of their holding changes.
                        # This is what the simulator does.
                        # So, total_asset_value += sum(st.session_state.player_investments.values()) - this is not quite right.
                        # player_investments should store number of shares.

                        # Let's reset and use a clear model:
                        # st.session_state.player_portfolio = {stock_name: {'shares': float, 'purchase_turn_prices': list[float]}}
                        # player_balance is cash.
                        # total_asset_value = player_balance + sum(portfolio[stock]['shares'] * current_stock_price[stock] for stock in portfolio)

                        # For this iteration, let's use the existing simpler `player_investments`
                        # and assume it stores the *number of shares*.
                        # We'll need to fetch the current price of those shares.
                        current_stock_price = stock_info['current_value']
                        total_asset_value += invested_amount * current_stock_price # invested_amount is shares

            col_asset.metric("총 자산 가치", f"{total_asset_value:.0f} 코인")


            st.markdown("--- ")
            st.subheader("📢 이번 턴 소식")
            
            # Display Result (from previous turn's news)
            st.info(f"**지난 턴 결과:** {current_turn_data['result']}")
            
            # Display News (for next turn)
            st.warning(f"**새로운 소식:** {current_turn_data['news']}")
            st.caption(f"힌트: {current_turn_data['news_hint']}")
            
            st.markdown("--- ")
            st.subheader("📈 투자 아이템 현황 및 투자하기")

            form = st.form(key=f"turn_{turn_number}_investment_form")
            cols = form.columns(len(current_turn_data['stocks']))
            
            investment_inputs = {}

            for i, stock in enumerate(current_turn_data['stocks']):
                with cols[i]:
                    st.markdown(f"#### {stock['name']}")
                    st.markdown(f"*{stock['description']}*", help=f"위험도: {stock['risk_level']}")
                    st.metric(label="현재 가치", value=f"{stock['current_value']} 코인", delta=f"{stock['current_value'] - stock['initial_value']} (초기 대비)")
                    st.caption(f"다음 턴 예상: {stock['expectation']}")
                    
                    # Investment input
                    # Allow buying shares. Selling is more complex for now (which shares to sell if bought at different prices?)
                    # Simple model: can adjust total number of shares.
                    # If current_shares = player_investments.get(stock['name'], 0)
                    # new_total_shares = number_input(...)
                    # cost_or_gain = (new_total_shares - current_shares) * stock['current_value']
                    # player_balance -= cost_or_gain
                    
                    # Simpler: Input how many *additional* shares to buy or sell.
                    # Positive to buy, negative to sell.
                    
                    current_shares_held = st.session_state.player_investments.get(stock['name'], 0)
                    st.write(f"현재 보유 수량: {current_shares_held} 주")

                    investment_inputs[stock['name']] = form.number_input(
                        label=f"{stock['name']} 투자 수량 (매수+/매도-)", 
                        min_value=-current_shares_held, # Can sell up to what they have
                        # max_value can be limited by balance / current_price if buying
                        value=0, 
                        step=1, 
                        key=f"invest_{stock['name']}_{turn_number}"
                    )
            
            submit_button = form.form_submit_button(label="이번 턴 투자 결정! ✨")

            if submit_button:
                total_investment_cost = 0
                actions_taken_this_turn = []

                # Calculate total cost/gain from proposed transactions
                for stock_name, shares_to_change in investment_inputs.items():
                    if shares_to_change != 0:
                        stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
                        if stock_info:
                            price_per_share = stock_info['current_value']
                            total_investment_cost += shares_to_change * price_per_share
                            
                if total_investment_cost > st.session_state.player_balance and any(s > 0 for s in investment_inputs.values()): # If trying to buy more than balance allows
                    st.error(f"코인이 부족합니다! 총 필요 코인: {total_investment_cost}, 보유 코인: {st.session_state.player_balance}")
                else:
                    # Process transactions
                    for stock_name, shares_to_change in investment_inputs.items():
                        if shares_to_change != 0:
                            stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
                            if stock_info:
                                price_per_share = stock_info['current_value']
                                cost_for_this_stock = shares_to_change * price_per_share
                                
                                st.session_state.player_balance -= cost_for_this_stock
                                current_shares = st.session_state.player_investments.get(stock_name, 0)
                                st.session_state.player_investments[stock_name] = current_shares + shares_to_change
                                
                                action = "매수" if shares_to_change > 0 else "매도"
                                log_message = f"턴 {turn_number}: {stock_name} {abs(shares_to_change)}주 {action} (주당 {price_per_share}코인). 잔액: {st.session_state.player_balance}"
                                st.session_state.game_log.append(log_message)
                                actions_taken_this_turn.append(log_message)
                    
                    if actions_taken_this_turn:
                        for log in actions_taken_this_turn:
                            st.success(log)
                    else:
                        st.info("이번 턴에는 투자 변경사항이 없습니다.")

                    # Record asset history for this turn *after* investment decisions
                    current_total_asset_value = st.session_state.player_balance
                    for stock_name, shares_held in st.session_state.player_investments.items():
                        if shares_held > 0:
                            stock_info_for_value = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
                            if stock_info_for_value:
                                current_total_asset_value += shares_held * stock_info_for_value['current_value']
                    
                    # Record consolidated investment history for this turn
                    st.session_state.investment_history.append({
                        'turn': turn_number,
                        'balance': st.session_state.player_balance,
                        'total_asset_value': current_total_asset_value,
                        'investments': dict(st.session_state.player_investments)
                    })


                    # Move to next turn
                    st.session_state.current_turn_index += 1
                    if st.session_state.current_turn_index < len(game_data):
                        st.info("투자가 완료되었습니다. '다음 턴으로' 버튼을 눌러 진행하세요.")
                    # Auto-advance or use a button
                    # For now, let's make it so the form submission itself implies readiness for next turn's display
                    # We need a clear "Next Turn" button if form submission doesn't auto-advance the view.
                    # The current structure will re-render the *new* current_turn_index data.
                    st.rerun()


            if st.session_state.current_turn_index < len(game_data) and turn_number != game_data[st.session_state.current_turn_index]['turn']:
                 if st.button("다음 턴으로 이동 ➡️", key="next_turn_button_main"):
                    st.rerun()


        else: # Game finished
            st.header("🎉 게임 종료! 🎉")
            st.balloons()
            
            final_balance = st.session_state.player_balance
            final_total_asset_value = st.session_state.investment_history[-1]['total_asset_value'] if st.session_state.investment_history and 'total_asset_value' in st.session_state.investment_history[-1] else final_balance


            st.subheader("최종 결과")
            st.metric("최종 보유 코인", f"{final_balance} 코인")
            st.metric("최종 총 자산 가치", f"{final_total_asset_value:.0f} 코인")
            
            initial_total_asset = 100 # Assuming starting with 100 coins and no stocks
            profit = final_total_asset_value - initial_total_asset
            profit_percentage = (profit / initial_total_asset) * 100 if initial_total_asset > 0 else 0
            
            st.metric("총 수익", f"{profit:.0f} 코인", delta=f"{profit_percentage:.2f}%")

            if profit > 0:
                st.success("축하합니다! 투자를 통해 자산을 늘렸습니다! 🥳")
            elif profit < 0:
                st.error("아쉽지만, 이번에는 자산이 줄었네요. 다음 기회에 더 잘할 수 있을 거예요! 💪")
            else:
                st.info("본전이네요! 다음번엔 수익을 내봐요! 🧐")

            # Display investment history plot
            if st.session_state.investment_history:
                st.subheader("📊 나의 자산 변화 그래프")
                
                # Prepare data for plotting total asset value and balance over turns
                history_df_main = pd.DataFrame([h for h in st.session_state.investment_history if 'balance' in h and 'total_asset_value' in h])
                if not history_df_main.empty:
                    history_df_main = history_df_main.set_index('turn')
                    st.line_chart(history_df_main[['balance', 'total_asset_value']])
                
                # Prepare data for plotting individual stock holdings
                if st.session_state.investment_history:
                    st.subheader("📦 보유 주식 수량 변화")
                    # Create a dataframe showing portfolio changes over time
                    portfolio_data = []
                    for entry in st.session_state.investment_history:
                        if 'investments' in entry:
                            for stock_name, shares in entry['investments'].items():
                                if shares > 0:
                                    portfolio_data.append({
                                        'turn': entry['turn'],
                                        'stock_name': stock_name,
                                        'shares_held': shares
                                    })
                    
                    if portfolio_data:
                        portfolio_df = pd.DataFrame(portfolio_data)
                        pivot_portfolio = portfolio_df.pivot_table(index='turn', columns='stock_name', values='shares_held', fill_value=0)
                        st.area_chart(pivot_portfolio)


            # Display game log
            st.subheader("📜 게임 로그")
            for log_entry in reversed(st.session_state.game_log):
                st.text(log_entry)
            
            # Option to restart or load new scenario
            if st.button("새 게임 시작 또는 다른 시나리오 불러오기", key="restart_game_end"):
                # Reset all relevant session state variables
                st.session_state.game_data = None
                st.session_state.current_turn_index = 0
                st.session_state.player_investments = {}
                st.session_state.player_balance = 100
                st.session_state.investment_history = []
                st.session_state.game_log = []
                st.session_state.game_started = False
                st.session_state.simulation_results_df = None
                # Potentially switch game_mode or clear selections if needed
                # For now, just rerun to go back to the selection screen
                st.rerun()

    # --- Simulation Section (Optional, can be expanded) ---
    if st.session_state.game_data and not st.session_state.game_started : # Show simulation option only if data is loaded but game not started by player
        st.markdown("--- ")
        st.subheader("🤖 AI 시뮬레이션 (참고용)")
        st.write("현재 불러온 시나리오에 대해 AI가 자동으로 투자를 시뮬레이션한 결과를 볼 수 있습니다.")
        
        if st.button("AI 투자 시뮬레이션 실행하기", key="run_simulation_button"):
            if st.session_state.game_data:
                try:
                    # Use the existing run_automated_simulation function
                    simulation_result = run_automated_simulation(st.session_state.game_data, "random")
                    
                    if simulation_result:
                        final_capital = simulation_result.get('final_capital', 0)
                        profit_rate = simulation_result.get('profit_rate', 0)
                        
                        st.success(f"AI 시뮬레이션 완료! 최종 자산: {final_capital:.2f} 코인 (수익률: {profit_rate:.2f}%)")
                        
                        # Display simulation plot
                        fig = create_simple_stock_plot(st.session_state.game_data, "AI 시뮬레이션 결과 - 주식 가치 변화")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

                        # Show investment history if available
                        if 'investment_history' in simulation_result:
                            st.subheader("AI 투자 히스토리")
                            history_df = pd.DataFrame(simulation_result['investment_history'])
                            st.dataframe(history_df, use_container_width=True)
                    else:
                        st.error("시뮬레이션 실행에 실패했습니다.")

                except Exception as e:
                    st.error(f"시뮬레이션 중 오류 발생: {e}")
                    st.error("게임 데이터 형식을 확인해주세요.")


# --- Footer or additional info ---
st.markdown("--- ")
st.caption("EduStock LLM Game - 아이들을 위한 재미있는 투자 학습 게임")
