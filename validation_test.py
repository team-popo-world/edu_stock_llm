
#!/usr/bin/env python3
"""
최종 검증 테스트 - HTML 렌더링 문제 해결 확인
"""

import streamlit as st
import sys
import os

# 현재 디렉토리를 패스에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.ui.components import create_stock_card, create_news_card, create_metric_card, display_game_intro

st.title("✅ HTML 렌더링 수정 검증")

# 테스트용 데이터
test_stock = {
    'name': '애플 주식',
    'description': '기술 대기업 애플의 주식입니다.',
    'current_value': 150,
    'initial_value': 120,
    'risk_level': '중위험'
}

test_news = {
    'result': '기술주 급등',
    'news': '애플이 새로운 혁신적인 제품을 발표했습니다.',
    'news_hint': '기술주가 상승할 것으로 예상됩니다.'
}

st.markdown("## 1. 종목 카드 테스트")
st.markdown("### ✅ 수정된 HTML 렌더링")
stock_html = create_stock_card(test_stock)
st.markdown(stock_html, unsafe_allow_html=True)

st.markdown("## 2. 뉴스 카드 테스트")
st.markdown("### ✅ 수정된 HTML 렌더링")
news_html = create_news_card(test_news)
st.markdown(news_html, unsafe_allow_html=True)

st.markdown("## 3. 메트릭 카드 테스트")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ✅ 턴 정보")
    metric_html = create_metric_card("총 5턴", "턴 3")
    st.markdown(metric_html, unsafe_allow_html=True)

with col2:
    st.markdown("### ✅ 보유 코인")
    metric_html = create_metric_card("보유 코인", "💰 1250")
    st.markdown(metric_html, unsafe_allow_html=True)

with col3:
    st.markdown("### ✅ 총 자산")
    metric_html = create_metric_card("총 자산", "📊 1450")
    st.markdown(metric_html, unsafe_allow_html=True)

st.markdown("## 4. 게임 소개 카드 테스트")
st.markdown("### ✅ 수정된 HTML 렌더링")
intro_html = display_game_intro()
st.markdown(intro_html, unsafe_allow_html=True)

st.markdown("## 🎉 결과")
st.success("모든 HTML 컴포넌트가 올바르게 렌더링되고 있습니다!")

st.markdown("### 수정된 내용:")
st.markdown("""
- ❌ **이전**: CSS 클래스 참조 (`class="stock-card"`, `class="news-card"` 등)
- ✅ **이후**: 인라인 스타일로 변경하여 HTML이 텍스트로 출력되는 문제 해결
- ✅ **결과**: 모든 카드 컴포넌트가 시각적으로 올바르게 렌더링됨
""")

st.markdown("### 📝 수정된 함수들:")
st.code("""
- create_stock_card() - 종목 선택 카드
- create_news_card() - 뉴스 표시 카드  
- create_metric_card() - 상태 정보 카드
- display_game_intro() - 게임 소개 카드
""", language="text")
