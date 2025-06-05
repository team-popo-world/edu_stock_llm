
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


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


def create_metric_card(title, value, subtitle=""):
    """메트릭 카드 생성"""
    return f"""
    <div class="metric-card">
        <h3>{value}</h3>
        <p>{title}</p>
        {f'<small>{subtitle}</small>' if subtitle else ''}
    </div>
    """


def create_news_card(current_turn_data):
    """뉴스 카드 생성"""
    return f"""
    <div class="news-card">
        <h3>📰 이번 턴 소식</h3>
        <p><strong>결과:</strong> {current_turn_data.get('result', '결과 정보 없음')}</p>
        <p><strong>뉴스:</strong> {current_turn_data.get('news', '뉴스 정보 없음')}</p>
        <p><em>💡 힌트: {current_turn_data.get('news_hint', '힌트 정보 없음')}</em></p>
    </div>
    """


def create_stock_card(stock):
    """주식 카드 생성"""
    return f"""
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
    """


def create_investment_history_chart(investment_history):
    """투자 히스토리 차트 생성"""
    if len(investment_history) <= 1:
        return None
        
    history_df = pd.DataFrame([
        {'턴': h['turn'], '총자산': h['total_asset_value'], '현금': h['balance']} 
        for h in investment_history
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
    
    return fig


def display_api_key_warning():
    """API 키 경고 메시지 표시"""
    st.markdown("""
    <div style="background: #fff3cd; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        ⚠️ <strong>API 키가 필요합니다</strong><br>
        환경변수에 GOOGLE_API_KEY를 설정해주세요
    </div>
    """, unsafe_allow_html=True)


def display_game_intro():
    """게임 소개 카드"""
    return """
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
    """
