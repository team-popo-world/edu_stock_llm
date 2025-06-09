
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def create_simple_stock_plot(game_data, title="🎯 우리의 투자 모험"):
    """간단하고 깔끔한 주식 차트 생성 (아동 친화적 버전)"""
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
    
    # 아동 친화적 색상 팔레트
    child_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    
    for i, (stock_name, values) in enumerate(stock_data.items()):
        color = child_colors[i % len(child_colors)]
        
        # 더 굵고 명확한 선과 큰 마커
        fig.add_trace(go.Scatter(
            x=turns,
            y=values,
            mode='lines+markers',
            name=f"🏪 {stock_name}",
            line=dict(color=color, width=4),
            marker=dict(size=10, symbol='circle'),
            hovertemplate=f'<b>{stock_name}</b><br>가격: %{{y}}코인<br>%{{x}}일째<extra></extra>'
        ))
    
    # 시작 가격 기준선
    fig.add_hline(y=100, line_dash="dash", line_color="gray", 
                  annotation_text="🏁 처음 시작 가격", 
                  annotation_position="bottom right")
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'font': {'size': 18, 'family': 'Arial Black'}
        },
        xaxis_title="📅 게임 날짜 (며칠째)",
        yaxis_title="💰 투자 가격 (코인)",
        hovermode='x unified',
        template='plotly_white',
        height=450,
        font=dict(family="Arial, sans-serif", size=14),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="Black",
            borderwidth=1
        ),
        plot_bgcolor='rgba(248,249,250,0.7)',
        paper_bgcolor='white'
    )
    
    # 축 스타일링
    fig.update_xaxes(
        gridcolor='lightgray',
        tickfont=dict(size=12, family="Arial")
    )
    fig.update_yaxes(
        gridcolor='lightgray',
        tickfont=dict(size=12, family="Arial")
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
    """뉴스 카드 생성 (아동 친화적 버전)"""
    result = current_turn_data.get('result', '결과 정보 없음')
    news = current_turn_data.get('news', '뉴스 정보 없음')
    hint = current_turn_data.get('news_hint', '힌트 정보 없음')
    
    return f"""
    <div class="news-card" style="background: linear-gradient(135deg, #FFE5B4 0%, #FFCCCB 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 3px solid #FFA500;">
        <h3 style="color: #FF6B35; margin-bottom: 1rem;">📢 오늘의 특별한 소식!</h3>
        <div style="background: white; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #4CAF50;">
            <p style="margin: 0; font-size: 16px;"><strong>🎉 무슨 일이 일어났을까요?</strong></p>
            <p style="margin: 0.5rem 0 0 0; color: #333; font-size: 15px;">{result}</p>
        </div>
        <div style="background: white; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #2196F3;">
            <p style="margin: 0; font-size: 16px;"><strong>📰 자세한 뉴스:</strong></p>
            <p style="margin: 0.5rem 0 0 0; color: #333; font-size: 15px;">{news}</p>
        </div>
        <div style="background: #FFF9C4; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; border: 2px dashed #FFC107;">
            <p style="margin: 0; font-size: 16px;"><strong>💡 현명한 투자자를 위한 힌트:</strong></p>
            <p style="margin: 0.5rem 0 0 0; color: #E65100; font-size: 15px; font-style: italic;">{hint}</p>
        </div>
    </div>
    """


def create_stock_card(stock):
    """주식 카드 생성 (아동 친화적 버전)"""
    name = stock.get('name', '이름 없음')
    description = stock.get('description', '설명 없음')
    current_value = stock.get('current_value', 0)
    initial_value = stock.get('initial_value', 100)
    risk_level = stock.get('risk_level', '정보 없음')
    
    # 가격 변동 계산
    if initial_value > 0:
        change_percent = ((current_value - initial_value) / initial_value) * 100
        if change_percent > 0:
            change_color = "#4CAF50"
            change_icon = "📈"
            change_text = f"+{change_percent:.1f}%"
        elif change_percent < 0:
            change_color = "#F44336"
            change_icon = "📉"
            change_text = f"{change_percent:.1f}%"
        else:
            change_color = "#9E9E9E"
            change_icon = "➡️"
            change_text = "0%"
    else:
        change_color = "#9E9E9E"
        change_icon = "❓"
        change_text = "변동 없음"
    
    # 위험도별 아이콘
    risk_icons = {
        "저위험": "🟢",
        "중위험": "🟡", 
        "고위험": "🔴"
    }
    risk_icon = "🟢"
    for risk, icon in risk_icons.items():
        if risk in risk_level:
            risk_icon = icon
            break
    
    return f"""
    <div class="stock-card" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 3px solid #dee2e6; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; transition: all 0.3s ease; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #495057; font-size: 18px; font-weight: bold;">🏪 {name}</h4>
            <span style="margin-left: auto; font-size: 20px; color: {change_color}; font-weight: bold;">
                {change_icon} {change_text}
            </span>
        </div>
        
        <p style="color: #6c757d; margin: 0.5rem 0; font-size: 14px; line-height: 1.4;">
            📝 {description}
        </p>
        
        <div style="background: white; border-radius: 10px; padding: 1rem; margin: 1rem 0; border: 2px solid #e9ecef;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 24px; font-weight: bold; color: #212529;">
                        💰 {current_value} 코인
                    </div>
                    <small style="color: #6c757d;">지금 가격</small>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 14px; color: #495057;">
                        {risk_icon} <strong>{risk_level}</strong>
                    </div>
                    <small style="color: #6c757d;">처음 가격: {initial_value} 코인</small>
                </div>
            </div>
        </div>
        
        <div style="background: #e3f2fd; border-radius: 8px; padding: 0.8rem; margin-top: 1rem; border-left: 4px solid #2196F3;">
            <small style="color: #1565C0; font-weight: 500;">
                💭 이 투자는 어떨까요? 뉴스와 힌트를 잘 읽어보세요!
            </small>
        </div>
    </div>
    """


def create_investment_history_chart(investment_history):
    """투자 히스토리 차트 생성 (아동 친화적 버전)"""
    if len(investment_history) <= 1:
        return None
        
    history_df = pd.DataFrame([
        {'턴': h['turn'], '총자산': h['total_asset_value'], '현금': h['balance']} 
        for h in investment_history
    ])
    
    fig = go.Figure()
    
    # 더 밝고 친근한 색상
    fig.add_trace(go.Scatter(
        x=history_df['턴'], 
        y=history_df['총자산'],
        mode='lines+markers',
        name='💰 총 자산 (모든 돈)',
        line=dict(color='#4CAF50', width=4),  # 밝은 녹색
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>%{y}원</b><br>%{x}일째<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=history_df['턴'], 
        y=history_df['현금'],
        mode='lines+markers',
        name='💵 현금 (바로 쓸 수 있는 돈)',
        line=dict(color='#FF9800', width=4),  # 밝은 주황색
        marker=dict(size=10, symbol='diamond'),
        hovertemplate='<b>%{y}원</b><br>%{x}일째<extra></extra>'
    ))
    
    # 시작점 표시
    fig.add_hline(y=1000, line_dash="dash", line_color="gray", 
                  annotation_text="🏁 시작할 때 가진 돈", 
                  annotation_position="bottom right")
    
    fig.update_layout(
        title={
            'text': '🌟 내 투자 성장 이야기 🌟',
            'x': 0.5,
            'font': {'size': 18, 'family': 'Arial Black'}
        },
        xaxis_title="📅 게임 날짜 (며칠째)",
        yaxis_title="💰 돈의 양 (코인)",
        height=450,
        template='plotly_white',
        hovermode='x unified',
        font=dict(family="Arial, sans-serif", size=14),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="Black",
            borderwidth=1
        ),
        plot_bgcolor='rgba(248,249,250,0.7)',
        paper_bgcolor='white'
    )
    
    # 축 스타일링
    fig.update_xaxes(
        gridcolor='lightgray',
        tickfont=dict(size=12, family="Arial")
    )
    fig.update_yaxes(
        gridcolor='lightgray',
        tickfont=dict(size=12, family="Arial")
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
