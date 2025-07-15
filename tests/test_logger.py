"""
Tests for logger module
"""
import pytest
import logging
import os
from unittest.mock import patch, MagicMock
from src.utils.logger import GameLogger, get_logger, log_info, log_error


class TestGameLogger:
    """Tests for GameLogger class"""
    
    @patch('src.utils.logger.os.makedirs')
    def test_logger_initialization(self, mock_makedirs):
        """Test logger initialization"""
        logger = GameLogger("test_logger")
        assert logger.name == "test_logger"
        assert logger.logger.name == "test_logger"
        mock_makedirs.assert_called_once()
    
    @patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'})
    @patch('src.utils.logger.os.makedirs')
    def test_logger_level_from_env(self, mock_makedirs):
        """Test logger level is set from environment variable"""
        logger = GameLogger("test_logger")
        assert logger.logger.level == logging.DEBUG
    
    @patch('src.utils.logger.os.makedirs')
    def test_logger_default_level(self, mock_makedirs):
        """Test logger default level is INFO"""
        logger = GameLogger("test_logger")
        assert logger.logger.level == logging.INFO
    
    @patch('src.utils.logger.os.makedirs')
    def test_log_methods(self, mock_makedirs):
        """Test various log methods"""
        logger = GameLogger("test_logger")
        
        # Mock the underlying logger
        logger.logger = MagicMock()
        
        # Test info
        logger.info("Test info message")
        logger.logger.info.assert_called_with("Test info message", extra=None)
        
        # Test warning
        logger.warning("Test warning message")
        logger.logger.warning.assert_called_with("Test warning message", extra=None)
        
        # Test error without exception
        logger.error("Test error message")
        logger.logger.error.assert_called_with("Test error message", extra=None)
        
        # Test error with exception
        test_exception = Exception("Test exception")
        logger.error("Test error message", test_exception)
        logger.logger.error.assert_called_with("Test error message: Test exception", exc_info=True, extra=None)
        
        # Test debug
        logger.debug("Test debug message")
        logger.logger.debug.assert_called_with("Test debug message", extra=None)
    
    @patch('src.utils.logger.os.makedirs')
    def test_log_game_event(self, mock_makedirs):
        """Test game event logging"""
        logger = GameLogger("test_logger")
        logger.logger = MagicMock()
        
        logger.log_game_event("PURCHASE", "player123", {"stock": "MAGIC", "amount": 100})
        
        # Check that info was called with correct message
        logger.logger.info.assert_called_once()
        call_args = logger.logger.info.call_args
        assert "GAME_EVENT: PURCHASE" in call_args[0][0]
        assert "player_id" in call_args[1]["extra"]
        assert call_args[1]["extra"]["player_id"] == "player123"
    
    @patch('src.utils.logger.os.makedirs')
    def test_log_api_request(self, mock_makedirs):
        """Test API request logging"""
        logger = GameLogger("test_logger")
        logger.logger = MagicMock()
        
        logger.log_api_request("/scenario/generate", "POST", {"scenario_type": "magic_kingdom"}, 1.5)
        
        # Check that info was called with correct message
        logger.logger.info.assert_called_once()
        call_args = logger.logger.info.call_args
        assert "API_REQUEST: POST /scenario/generate" in call_args[0][0]
        assert "endpoint" in call_args[1]["extra"]
        assert call_args[1]["extra"]["endpoint"] == "/scenario/generate"
    
    @patch('src.utils.logger.os.makedirs')
    def test_log_llm_interaction(self, mock_makedirs):
        """Test LLM interaction logging"""
        logger = GameLogger("test_logger")
        logger.logger = MagicMock()
        
        logger.log_llm_interaction("scenario_generation", 150, 2.3)
        
        # Check that info was called with correct message
        logger.logger.info.assert_called_once()
        call_args = logger.logger.info.call_args
        assert "LLM_INTERACTION: scenario_generation" in call_args[0][0]
        assert "tokens_used" in call_args[1]["extra"]
        assert call_args[1]["extra"]["tokens_used"] == 150


class TestLoggerUtilityFunctions:
    """Tests for logger utility functions"""
    
    def test_get_logger(self):
        """Test get_logger function"""
        logger = get_logger("test_logger")
        assert isinstance(logger, GameLogger)
        assert logger.name == "test_logger"
    
    @patch('src.utils.logger.logger')
    def test_log_info(self, mock_logger):
        """Test log_info utility function"""
        log_info("Test message")
        mock_logger.info.assert_called_once_with("Test message", None)
    
    @patch('src.utils.logger.logger')
    def test_log_error(self, mock_logger):
        """Test log_error utility function"""
        test_exception = Exception("Test error")
        log_error("Test message", test_exception)
        mock_logger.error.assert_called_once_with("Test message", test_exception, None)