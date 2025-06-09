#!/usr/bin/env python3
"""
HTML 렌더링 테스트 스크립트
종목 선택 페이지에서 HTML이 텍스트로 출력되는 문제를 진단
"""

import streamlit as st
import sys
import os

# 현재 디렉토리를 패스에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.ui.components import create_stock_card, create_news_card

st.title("🔍 HTML 렌더링 테스트")

# 테스트용 주식 데이터
test_stock = {
    'name': '테스트 주식',
    'description': '이것은 테스트용 주식입니다.',
    'current_value': 120,
    'initial_value': 100,
    'risk_level': '중위험'
}

# 테스트용 뉴스 데이터
test_news = {
    'result': '테스트 결과입니다.',
    'news': '테스트 뉴스입니다.',
    'news_hint': '테스트 힌트입니다.'
}

st.markdown("## 1. HTML 렌더링 테스트 (unsafe_allow_html=True)")

# 테스트 1: create_stock_card with unsafe_allow_html=True
st.markdown("### 📈 종목 카드 테스트")
stock_html = create_stock_card(test_stock)
st.markdown(stock_html, unsafe_allow_html=True)

# 테스트 2: create_news_card with unsafe_allow_html=True  
st.markdown("### 📰 뉴스 카드 테스트")
news_html = create_news_card(test_news)
st.markdown(news_html, unsafe_allow_html=True)

st.markdown("## 2. HTML 렌더링 테스트 (unsafe_allow_html=False)")

# 테스트 3: unsafe_allow_html=False로 테스트 (문제 재현용)
st.markdown("### ❌ 잘못된 렌더링 예제")
st.markdown(stock_html, unsafe_allow_html=False)

st.markdown("## 3. 직접 HTML 테스트")

# 테스트 4: 직접 HTML 작성 테스트
direct_html = """
<div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 3px solid #dee2e6; border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
    <h4 style="color: #495057;">🏪 직접 작성한 HTML</h4>
    <p>이 HTML이 올바르게 렌더링되는지 확인합니다.</p>
</div>
"""

st.markdown("### ✅ 직접 HTML (unsafe_allow_html=True)")
st.markdown(direct_html, unsafe_allow_html=True)

st.markdown("### ❌ 직접 HTML (unsafe_allow_html=False)")
st.markdown(direct_html, unsafe_allow_html=False)

# 디버깅 정보
st.markdown("## 4. 디버깅 정보")
st.markdown("### 생성된 HTML 코드:")
st.code(stock_html, language='html')
