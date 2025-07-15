import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional


class GameLogger:
    """
    교육용 주식 투자 게임을 위한 로거 클래스
    """
    
    def __init__(self, name: str = "edu_stock_game"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """로거 설정"""
        if self.logger.handlers:
            return  # 이미 설정되어 있으면 중복 설정 방지
        
        # 로그 레벨 설정
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # 로그 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 (회전 로그)
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(logs_dir, f"{self.name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 에러 전용 파일 핸들러
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(logs_dir, f"{self.name}_error.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """정보 로그"""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """경고 로그"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exception: Optional[Exception] = None, extra: Optional[dict] = None):
        """에러 로그"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True, extra=extra)
        else:
            self.logger.error(message, extra=extra)
    
    def debug(self, message: str, extra: Optional[dict] = None):
        """디버그 로그"""
        self.logger.debug(message, extra=extra)
    
    def log_game_event(self, event_type: str, player_id: str, details: dict):
        """게임 이벤트 로깅"""
        self.info(f"GAME_EVENT: {event_type}", extra={
            "player_id": player_id,
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_api_request(self, endpoint: str, method: str, params: dict, response_time: float):
        """API 요청 로깅"""
        self.info(f"API_REQUEST: {method} {endpoint}", extra={
            "endpoint": endpoint,
            "method": method,
            "params": params,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_llm_interaction(self, prompt_type: str, tokens_used: int, response_time: float):
        """LLM 상호작용 로깅"""
        self.info(f"LLM_INTERACTION: {prompt_type}", extra={
            "prompt_type": prompt_type,
            "tokens_used": tokens_used,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })


# 전역 로거 인스턴스
logger = GameLogger()

# 편의 함수들
def get_logger(name: str = "edu_stock_game") -> GameLogger:
    """로거 인스턴스 반환"""
    return GameLogger(name)

def log_info(message: str, extra: Optional[dict] = None):
    """정보 로그 편의 함수"""
    logger.info(message, extra)

def log_warning(message: str, extra: Optional[dict] = None):
    """경고 로그 편의 함수"""
    logger.warning(message, extra)

def log_error(message: str, exception: Optional[Exception] = None, extra: Optional[dict] = None):
    """에러 로그 편의 함수"""
    logger.error(message, exception, extra)

def log_debug(message: str, extra: Optional[dict] = None):
    """디버그 로그 편의 함수"""
    logger.debug(message, extra)