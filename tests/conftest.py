"""
pytest configuration and fixtures
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def mock_env():
    """Mock environment variables"""
    with patch.dict(os.environ, {
        'GOOGLE_API_KEY': 'test_api_key',
        'LOG_LEVEL': 'DEBUG',
        'ALLOWED_ORIGINS': 'http://localhost:3000,http://localhost:8501'
    }):
        yield

@pytest.fixture
def sample_game_data():
    """Sample game data for testing"""
    return [
        {
            "turn": 1,
            "day": "1일차",
            "news": "마법 왕국의 새로운 하루가 시작되었습니다!",
            "stocks": [
                {
                    "name": "마법 빵집",
                    "symbol": "MAGIC",
                    "price": 100,
                    "change": 0,
                    "description": "맛있는 마법 빵을 만드는 빵집입니다."
                },
                {
                    "name": "서커스단",
                    "symbol": "CIRCUS",
                    "price": 150,
                    "change": 0,
                    "description": "재미있는 서커스 공연을 하는 단체입니다."
                },
                {
                    "name": "마법연구소",
                    "symbol": "RESEARCH",
                    "price": 200,
                    "change": 0,
                    "description": "새로운 마법을 연구하는 연구소입니다."
                }
            ]
        },
        {
            "turn": 2,
            "day": "2일차",
            "news": "마법 빵집에서 새로운 레시피를 개발했습니다!",
            "stocks": [
                {
                    "name": "마법 빵집",
                    "symbol": "MAGIC",
                    "price": 110,
                    "change": 10,
                    "description": "맛있는 마법 빵을 만드는 빵집입니다."
                },
                {
                    "name": "서커스단",
                    "symbol": "CIRCUS",
                    "price": 145,
                    "change": -5,
                    "description": "재미있는 서커스 공연을 하는 단체입니다."
                },
                {
                    "name": "마법연구소",
                    "symbol": "RESEARCH",
                    "price": 190,
                    "change": -10,
                    "description": "새로운 마법을 연구하는 연구소입니다."
                }
            ]
        }
    ]

@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    return '''
    [
        {
            "turn": 1,
            "day": "1일차",
            "news": "테스트 뉴스",
            "stocks": [
                {
                    "name": "테스트 주식",
                    "symbol": "TEST",
                    "price": 100,
                    "change": 0,
                    "description": "테스트용 주식입니다."
                }
            ]
        }
    ]
    '''

@pytest.fixture
def mock_streamlit_session():
    """Mock Streamlit session state"""
    return {
        'game_data': [],
        'current_turn': 1,
        'player_cash': 10000,
        'player_stocks': {},
        'portfolio_history': [],
        'current_theme': 'magic_kingdom'
    }

@pytest.fixture
def temporary_data_dir(tmp_path):
    """Create temporary directory for test data"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir