"""
설정 및 환경 변수 관리 모듈
"""
import os
from dotenv import load_dotenv
import streamlit as st

def load_api_key():
    """API 키를 로드하는 함수"""
    # 1. Streamlit secrets에서 먼저 시도
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            return st.secrets['GOOGLE_API_KEY']
    except Exception as e:
        print(f"Streamlit secrets 로드 실패: {e}")
    
    # 2. 환경변수에서 시도 (로컬 개발용)
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        return api_key
    
    # 3. 세션 상태에서 시도 (수동 입력)
    if hasattr(st, 'session_state') and 'manual_api_key' in st.session_state:
        return st.session_state.manual_api_key
    
    return None

def get_model_settings():
    """
    모델 설정값을 반환합니다.
    
    Returns:
        dict: 모델 설정값
    """
    return {
        "model_name": "gemini-2.5-flash-preview-05-20",
        "temperature": 1.0,  # Gemini의 권장 온도 설정
        "max_tokens": 65536
    }
