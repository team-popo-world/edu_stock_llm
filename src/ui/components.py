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
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 2px solid #dee2e6; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; text-align: center;">
        <h3 style="margin: 0 0 0.5rem 0; color: #495057;">{value}</h3>
        <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">{title}</p>
        {f'<small style="color: #adb5bd;">{subtitle}</small>' if subtitle else ''}
    </div>
    """


def create_news_card(current_turn_data):
    """뉴스 카드 생성 (아동 친화적 버전)"""
    result = current_turn_data.get('result', '결과 정보 없음')
    news = current_turn_data.get('news', '뉴스 정보 없음')
    
    return f"""
<div style="background: linear-gradient(135deg, #FFE5B4 0%, #FFCCCB 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 2px solid #FFA500;">
    <h3 style="color: #FF6B35; margin-bottom: 1rem;">📢 오늘의 특별한 소식!</h3>
    <div style="background: white; border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
        <p style="margin: 0; font-size: 16px;"><strong>🎉 무슨 일이 일어났을까요?</strong></p>
        <p style="margin: 0.5rem 0 0 0; color: #333; font-size: 15px;">{result}</p>
    </div>
    <div style="background: white; border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
        <p style="margin: 0; font-size: 16px;"><strong>📰 자세한 뉴스:</strong></p>
        <p style="margin: 0.5rem 0 0 0; color: #333; font-size: 15px;">{news}</p>
    </div>
</div>"""


def create_stock_card(stock):
    """주식 카드 생성 (아동 친화적 버전)"""
    name = stock.get('name', '이름 없음')
    description = stock.get('description', '설명 없음')
    current_value = stock.get('current_value', 0)
    initial_value = stock.get('initial_value', 100)
    risk_level = stock.get('risk_level', '정보 없음')
    expectation = stock.get('expectation', '이 투자는 어떨까요? 뉴스와 힌트를 잘 읽어보세요!')
    
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
<div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 2px solid #dee2e6; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <h4 style="margin: 0; color: #495057; font-size: 18px; font-weight: bold;">{name}</h4>
        <span style="margin-left: auto; font-size: 18px; color: {change_color}; font-weight: bold;">
            {change_icon} {change_text}
        </span>
    </div>
    <p style="color: #6c757d; margin: 0.5rem 0; font-size: 14px;">
        📝 {description}
    </p>
    <div style="background: white; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 22px; font-weight: bold; color: #212529;">
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
    <div style="background: #e3f2fd; border-radius: 8px; padding: 0.8rem; margin-top: 1rem;">
        <small style="color: #1565C0; font-weight: 500;">
            💭 {expectation}
        </small>
    </div>
</div>"""


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
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 2px solid #dee2e6; border-radius: 15px; padding: 3rem; margin: 1rem 0; text-align: center;">
        <h2 style="color: #495057; margin-bottom: 1rem;">🎮 게임 방법</h2>
        <br>
        <div style="text-align: left; margin: 2rem 0;">
            <p style="margin: 0.5rem 0; color: #495057;">🎯 <strong>목표:</strong> 1000코인으로 시작해서 투자를 통해 돈을 늘려보세요!</p>
            <p style="margin: 0.5rem 0; color: #495057;">📰 <strong>방법:</strong> 매 턴마다 나오는 뉴스를 보고 어떤 주식을 살지 결정하세요</p>
            <p style="margin: 0.5rem 0; color: #495057;">💡 <strong>팁:</strong> 뉴스를 잘 읽고 힌트를 활용해보세요</p>
        </div>
        <br>
    </div>
    """


def create_mentor_advice_card(mentor_data):
    """AI 멘토 조언 카드 생성"""
    if not mentor_data or not mentor_data.get('advice'):
        return
    
    advice = mentor_data['advice']
    analysis = mentor_data.get('analysis', {})
    
    # 멘토 카드 스타일
    mentor_card_style = """
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #e1e8ed;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    """
    
    with st.container():
        st.markdown(f"""
        <div style="{mentor_card_style}">
            <h3 style="margin: 0; color: white; font-size: 1.2em;">
                🤖 AI 투자 멘토의 조언
            </h3>
            <p style="margin: 10px 0 0 0; font-size: 1.1em; line-height: 1.5;">
                {advice.get('main_message', '계속해서 좋은 투자를 해보세요!')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 상세 분석 정보 (접을 수 있는 형태)
        with st.expander("📊 상세 분석 보기", expanded=False):
            if analysis.get('portfolio'):
                portfolio = analysis['portfolio']
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("💰 총 자산", f"{portfolio.get('total_assets', 0):.0f}코인")
                    st.metric("📈 투자 비율", f"{portfolio.get('investment_ratio', 0):.1f}%")
                
                with col2:
                    st.metric("💵 현금", f"{portfolio.get('cash_balance', 0):.0f}코인")
                    st.metric("🏪 투자 가치", f"{portfolio.get('investment_value', 0):.0f}코인")
            
            if advice.get('tips'):
                st.write("💡 **맞춤형 팁:**")
                for tip in advice['tips']:
                    st.write(f"• {tip}")


def create_learning_progress_card(player_profile):
    """학습 진도 카드 생성"""
    if not player_profile:
        return
    
    progress_style = """
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        color: white;
    """
    
    with st.container():
        st.markdown(f"""
        <div style="{progress_style}">
            <h4 style="margin: 0; color: white;">📚 나의 학습 현황</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎮 플레이한 게임", player_profile.games_played)
        
        with col2:
            st.metric("🎯 총 턴 수", player_profile.total_turns_played)
        
        with col3:
            learning_style_emoji = {
                "visual": "👀",
                "auditory": "👂", 
                "hands_on": "✋",
                "analytical": "🧠",
                "exploring": "🔍"
            }
            style_emoji = learning_style_emoji.get(player_profile.learning_style.value, "🔍")
            st.metric("📖 학습 스타일", f"{style_emoji} {player_profile.learning_style.value}")
        
        # 강점과 개선점
        if player_profile.strengths or player_profile.areas_for_improvement:
            with st.expander("🎯 나의 강점과 개선점"):
                if player_profile.strengths:
                    st.write("💪 **강점:**")
                    for strength in player_profile.strengths:
                        st.write(f"• {strength}")
                
                if player_profile.areas_for_improvement:
                    st.write("📈 **개선할 점:**")
                    for area in player_profile.areas_for_improvement:
                        st.write(f"• {area}")


def create_mentor_toggle():
    """AI 멘토 켜기/끄기 토글"""
    mentor_enabled = st.session_state.get('mentor_enabled', True)
    
    new_state = st.toggle(
        "🤖 AI 멘토 활성화", 
        value=mentor_enabled,
        help="AI 멘토가 투자 조언을 제공합니다"
    )
    
    if new_state != mentor_enabled:
        st.session_state.mentor_enabled = new_state
        if new_state:
            st.success("AI 멘토가 활성화되었습니다!")
        else:
            st.info("AI 멘토가 비활성화되었습니다.")
        st.rerun()


def show_mentor_advice_button():
    """멘토 조언 보기 버튼"""
    if st.session_state.get('mentor_enabled', True):
        if st.button("🤖 AI 멘토 조언 보기", type="secondary"):
            st.session_state.show_mentor_advice = True
            st.rerun()


def create_learning_progress_chart(player_profile):
    """학습 진도 차트"""
    if not player_profile or not player_profile.decision_patterns:
        return
    
    # 학습 영역별 점수 계산
    learning_areas = {
        "위험 관리": min(100, (1.0 - abs(player_profile.decision_patterns.get("risk_taking", 0.5) - 0.3)) * 100),
        "분산 투자": player_profile.consistency_score * 100,
        "시장 분석": min(100, player_profile.decision_patterns.get("buy_frequency", 0) * 200),
        "감정 조절": min(100, (1.0 - player_profile.decision_patterns.get("hold_frequency", 0.3)) * 150)
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(learning_areas.values()),
        theta=list(learning_areas.keys()),
        fill='toself',
        name='현재 수준',
        line_color='rgb(102, 126, 234)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="📚 나의 투자 학습 진도",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_encouragement_banner(message):
    """격려 메시지 배너"""
    banner_style = """
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-size: 18px;
    font-weight: bold;
    margin: 15px 0;
    animation: pulse 2s infinite;
    """
    
    st.markdown(f"""
    <div style="{banner_style}">
        {message}
    </div>
    """, unsafe_allow_html=True)
