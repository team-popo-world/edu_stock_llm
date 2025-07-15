"""
설정 및 환경 변수 관리 모듈
"""
import os
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# 프로젝트 루트 디렉토리 찾기
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
env_file = project_root / '.env'

# .env 파일 로드 (명시적 경로 지정)
load_dotenv(env_file)


@dataclass
class AppConfig:
    """Application configuration"""
    
    # API Settings
    google_api_key: str = ""
    openai_api_key: str = ""
    
    # Server Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    streamlit_port: int = 8501
    
    # Security Settings
    allowed_origins: str = "http://localhost:3000,http://localhost:8501"
    
    # Logging Settings
    log_level: str = "INFO"
    debug: bool = False
    
    # Model Settings
    model_name: str = "gemini-2.5-flash-preview-05-20"
    temperature: float = 1.0
    max_tokens: int = 65536
    
    # Game Settings
    default_player_cash: int = 10000
    max_turns: int = 30
    max_portfolio_size: int = 10
    
    # File Settings
    data_directory: str = "data"
    logs_directory: str = "logs"
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            google_api_key=os.getenv('GOOGLE_API_KEY', ''),
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            api_host=os.getenv('API_HOST', '0.0.0.0'),
            api_port=int(os.getenv('API_PORT', '8000')),
            streamlit_port=int(os.getenv('STREAMLIT_PORT', '8501')),
            allowed_origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8501'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            model_name=os.getenv('MODEL_NAME', 'gemini-2.5-flash-preview-05-20'),
            temperature=float(os.getenv('TEMPERATURE', '1.0')),
            max_tokens=int(os.getenv('MAX_TOKENS', '65536')),
            default_player_cash=int(os.getenv('DEFAULT_PLAYER_CASH', '10000')),
            max_turns=int(os.getenv('MAX_TURNS', '30')),
            max_portfolio_size=int(os.getenv('MAX_PORTFOLIO_SIZE', '10')),
            data_directory=os.getenv('DATA_DIRECTORY', 'data'),
            logs_directory=os.getenv('LOGS_DIRECTORY', 'logs')
        )


# Global configuration instance
config = AppConfig.from_env()

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
