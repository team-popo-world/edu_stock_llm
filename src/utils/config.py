"""
설정 및 환경 변수 관리 모듈
"""
import os
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path

# 프로젝트 루트 디렉토리 찾기
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
env_file = project_root / '.env'

# .env 파일 로드 (명시적 경로 지정)
load_dotenv(env_file)

def load_api_key():
    """API 키를 로드하는 함수"""
    # 매번 .env 파일을 다시 로드하여 확실히 환경변수를 설정
    load_dotenv(env_file, override=True)
    
    # 1. Streamlit secrets에서 먼저 시도
    try:
        if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
            return st.secrets['GOOGLE_API_KEY']
    except Exception as e:
        pass  # secrets 파일이 없거나 키가 없는 경우는 정상적인 상황
    
    # 2. 환경변수에서 시도 (로컬 개발용)
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key and api_key.strip():  # 빈 문자열 체크도 추가
        return api_key.strip()
    
    # 3. 세션 상태에서 시도 (수동 입력)
    if hasattr(st, 'session_state') and 'manual_api_key' in st.session_state:
        manual_key = st.session_state.manual_api_key
        if manual_key and manual_key.strip():
            return manual_key.strip()
    
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
