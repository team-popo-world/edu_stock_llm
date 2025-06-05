"""
설정 및 환경 변수 관리 모듈
"""
import os
from dotenv import load_dotenv

def load_api_key():
    """
    Google API 키를 환경변수에서 로드합니다.
    
    Returns:
        str: Google API 키
    """
    try:
        # 환경 변수 캐시 초기화
        import os
        if 'GOOGLE_API_KEY' in os.environ:
            del os.environ['GOOGLE_API_KEY']
            
        load_dotenv(override=True)  # override=True로 강제 재로드
        api_key = os.getenv("GOOGLE_API_KEY")
        return api_key
    except Exception as e:
        print(f"API 키 로드 중 오류 발생: {e}")
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
