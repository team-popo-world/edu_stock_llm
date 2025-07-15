"""
Input validation and sanitization utilities
"""
import re
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from .logger import log_warning, log_error


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Input validation and sanitization utilities"""
    
    # Valid scenario types
    VALID_SCENARIO_TYPES = {
        "magic_kingdom", "foodtruck_kingdom", "moonlight_thief", "three_little_pigs"
    }
    
    # Valid investment strategies
    VALID_STRATEGIES = {
        "random", "conservative", "aggressive", "trend"
    }
    
    @staticmethod
    def validate_scenario_type(scenario_type: str) -> str:
        """
        Validate and sanitize scenario type
        
        Args:
            scenario_type: The scenario type to validate
            
        Returns:
            str: Validated scenario type
            
        Raises:
            ValidationError: If scenario type is invalid
        """
        if not isinstance(scenario_type, str):
            raise ValidationError("Scenario type must be a string")
        
        # Sanitize input
        scenario_type = scenario_type.strip().lower()
        
        if not scenario_type:
            raise ValidationError("Scenario type cannot be empty")
        
        if scenario_type not in InputValidator.VALID_SCENARIO_TYPES:
            raise ValidationError(f"Invalid scenario type: {scenario_type}. "
                                f"Valid types are: {', '.join(InputValidator.VALID_SCENARIO_TYPES)}")
        
        return scenario_type
    
    @staticmethod
    def validate_strategies(strategies: List[str]) -> List[str]:
        """
        Validate and sanitize investment strategies
        
        Args:
            strategies: List of strategy names to validate
            
        Returns:
            List[str]: Validated strategies
            
        Raises:
            ValidationError: If any strategy is invalid
        """
        if not isinstance(strategies, list):
            raise ValidationError("Strategies must be a list")
        
        if not strategies:
            raise ValidationError("At least one strategy must be provided")
        
        if len(strategies) > 10:
            raise ValidationError("Too many strategies provided (maximum 10)")
        
        validated_strategies = []
        for strategy in strategies:
            if not isinstance(strategy, str):
                raise ValidationError("Each strategy must be a string")
            
            # Sanitize input
            strategy = strategy.strip().lower()
            
            if not strategy:
                log_warning("Empty strategy name provided, skipping")
                continue
            
            if strategy not in InputValidator.VALID_STRATEGIES:
                raise ValidationError(f"Invalid strategy: {strategy}. "
                                    f"Valid strategies are: {', '.join(InputValidator.VALID_STRATEGIES)}")
            
            if strategy not in validated_strategies:
                validated_strategies.append(strategy)
        
        if not validated_strategies:
            raise ValidationError("No valid strategies provided")
        
        return validated_strategies
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True) -> str:
        """
        Validate and sanitize file path
        
        Args:
            file_path: The file path to validate
            must_exist: Whether the file must exist
            
        Returns:
            str: Validated file path
            
        Raises:
            ValidationError: If file path is invalid
        """
        if not isinstance(file_path, str):
            raise ValidationError("File path must be a string")
        
        # Sanitize input
        file_path = file_path.strip()
        
        if not file_path:
            raise ValidationError("File path cannot be empty")
        
        # Check for path traversal attempts
        if ".." in file_path or file_path.startswith("/"):
            raise ValidationError("Invalid file path: path traversal detected")
        
        # Validate file extension
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        # Validate filename characters
        filename = Path(file_path).name
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
            raise ValidationError("Invalid filename: contains illegal characters")
        
        if must_exist and not Path(file_path).exists():
            raise ValidationError(f"File does not exist: {file_path}")
        
        return file_path
    
    @staticmethod
    def validate_investment_amount(amount: Union[int, float]) -> float:
        """
        Validate investment amount
        
        Args:
            amount: The investment amount to validate
            
        Returns:
            float: Validated amount
            
        Raises:
            ValidationError: If amount is invalid
        """
        if not isinstance(amount, (int, float)):
            raise ValidationError("Investment amount must be a number")
        
        if amount < 0:
            raise ValidationError("Investment amount cannot be negative")
        
        if amount > 1000000:
            raise ValidationError("Investment amount too large (maximum 1,000,000)")
        
        return float(amount)
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> str:
        """
        Validate stock symbol
        
        Args:
            symbol: The stock symbol to validate
            
        Returns:
            str: Validated symbol
            
        Raises:
            ValidationError: If symbol is invalid
        """
        if not isinstance(symbol, str):
            raise ValidationError("Stock symbol must be a string")
        
        # Sanitize input
        symbol = symbol.strip().upper()
        
        if not symbol:
            raise ValidationError("Stock symbol cannot be empty")
        
        if len(symbol) > 10:
            raise ValidationError("Stock symbol too long (maximum 10 characters)")
        
        if not re.match(r'^[A-Z][A-Z0-9_]*$', symbol):
            raise ValidationError("Invalid stock symbol format")
        
        return symbol
    
    @staticmethod
    def validate_turn_number(turn: int) -> int:
        """
        Validate turn number
        
        Args:
            turn: The turn number to validate
            
        Returns:
            int: Validated turn number
            
        Raises:
            ValidationError: If turn number is invalid
        """
        if not isinstance(turn, int):
            raise ValidationError("Turn number must be an integer")
        
        if turn < 1:
            raise ValidationError("Turn number must be positive")
        
        if turn > 365:
            raise ValidationError("Turn number too large (maximum 365)")
        
        return turn
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize text input
        
        Args:
            text: The text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized text
            
        Raises:
            ValidationError: If text is invalid
        """
        if not isinstance(text, str):
            raise ValidationError("Text input must be a string")
        
        # Remove potential HTML/script tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove potential SQL injection patterns
        text = re.sub(r'(union|select|insert|update|delete|drop|create|alter)\s', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        if len(text) > max_length:
            raise ValidationError(f"Text too long (maximum {max_length} characters)")
        
        return text
    
    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """
        Validate API key format
        
        Args:
            api_key: The API key to validate
            
        Returns:
            str: Validated API key
            
        Raises:
            ValidationError: If API key is invalid
        """
        if not isinstance(api_key, str):
            raise ValidationError("API key must be a string")
        
        api_key = api_key.strip()
        
        if not api_key:
            raise ValidationError("API key cannot be empty")
        
        if len(api_key) < 10:
            raise ValidationError("API key too short")
        
        if len(api_key) > 200:
            raise ValidationError("API key too long")
        
        # Check for common test/placeholder keys
        if api_key.lower() in ['test', 'placeholder', 'your_api_key_here', 'your-api-key']:
            raise ValidationError("Invalid API key: appears to be a placeholder")
        
        return api_key


def validate_game_data(data: Any) -> List[Dict[str, Any]]:
    """
    Validate game data structure
    
    Args:
        data: The game data to validate
        
    Returns:
        List[Dict[str, Any]]: Validated game data
        
    Raises:
        ValidationError: If data structure is invalid
    """
    if not isinstance(data, list):
        raise ValidationError("Game data must be a list")
    
    if not data:
        raise ValidationError("Game data cannot be empty")
    
    if len(data) > 30:
        raise ValidationError("Too many turns in game data (maximum 30)")
    
    validated_data = []
    for i, turn_data in enumerate(data):
        if not isinstance(turn_data, dict):
            raise ValidationError(f"Turn {i+1} data must be a dictionary")
        
        # Validate required fields
        required_fields = ['turn', 'day', 'news', 'stocks']
        for field in required_fields:
            if field not in turn_data:
                raise ValidationError(f"Turn {i+1} missing required field: {field}")
        
        # Validate turn number
        turn_number = InputValidator.validate_turn_number(turn_data['turn'])
        
        # Validate stocks
        stocks = turn_data['stocks']
        if not isinstance(stocks, list):
            raise ValidationError(f"Turn {i+1} stocks must be a list")
        
        if not stocks:
            raise ValidationError(f"Turn {i+1} must have at least one stock")
        
        validated_stocks = []
        for stock in stocks:
            if not isinstance(stock, dict):
                raise ValidationError(f"Turn {i+1} stock data must be a dictionary")
            
            # Validate stock fields
            stock_fields = ['name', 'symbol', 'price']
            for field in stock_fields:
                if field not in stock:
                    raise ValidationError(f"Turn {i+1} stock missing required field: {field}")
            
            # Validate stock data
            validated_stock = {
                'name': InputValidator.sanitize_text_input(stock['name'], 50),
                'symbol': InputValidator.validate_stock_symbol(stock['symbol']),
                'price': InputValidator.validate_investment_amount(stock['price']),
                'change': stock.get('change', 0),
                'description': InputValidator.sanitize_text_input(stock.get('description', ''), 200)
            }
            
            validated_stocks.append(validated_stock)
        
        validated_turn = {
            'turn': turn_number,
            'day': InputValidator.sanitize_text_input(turn_data['day'], 20),
            'news': InputValidator.sanitize_text_input(turn_data['news'], 500),
            'stocks': validated_stocks
        }
        
        validated_data.append(validated_turn)
    
    return validated_data