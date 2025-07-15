"""
Tests for data handler module
"""
import json
import pytest
from unittest.mock import patch, mock_open
from src.data.data_handler import parse_json_data, save_game_data, load_game_data


class TestParseJsonData:
    """Tests for parse_json_data function"""
    
    def test_parse_valid_json(self, sample_game_data):
        """Test parsing valid JSON data"""
        json_content = json.dumps(sample_game_data)
        result = parse_json_data(json_content)
        assert result == sample_game_data
    
    def test_parse_empty_json(self):
        """Test parsing empty JSON content"""
        result = parse_json_data("")
        assert result is None
    
    def test_parse_none_json(self):
        """Test parsing None JSON content"""
        result = parse_json_data(None)
        assert result is None
    
    def test_parse_markdown_code_block(self, sample_game_data):
        """Test parsing JSON wrapped in markdown code blocks"""
        json_content = f"```json\n{json.dumps(sample_game_data)}\n```"
        result = parse_json_data(json_content)
        assert result == sample_game_data
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON"""
        with patch('src.data.data_handler.create_sample_game_data') as mock_sample:
            mock_sample.return_value = {"test": "data"}
            result = parse_json_data("invalid json")
            assert result == {"test": "data"}
    
    def test_parse_single_dict_to_list(self):
        """Test converting single dict with stocks to list"""
        single_dict = {
            "turn": 1,
            "stocks": [{"name": "Test", "symbol": "TEST", "price": 100}]
        }
        json_content = json.dumps(single_dict)
        result = parse_json_data(json_content)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == single_dict


class TestSaveGameData:
    """Tests for save_game_data function"""
    
    def test_save_game_data_success(self, sample_game_data, temporary_data_dir):
        """Test successful game data saving"""
        filename = "test_game.json"
        result = save_game_data(sample_game_data, str(temporary_data_dir), filename)
        
        assert "성공적으로 저장되었습니다" in result
        
        # Verify file was created
        saved_file = temporary_data_dir / filename
        assert saved_file.exists()
        
        # Verify file contents
        with open(saved_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == sample_game_data
    
    def test_save_game_data_creates_directory(self, sample_game_data, tmp_path):
        """Test that save_game_data creates directory if it doesn't exist"""
        new_dir = tmp_path / "new_data_dir"
        filename = "test_game.json"
        
        result = save_game_data(sample_game_data, str(new_dir), filename)
        
        assert "성공적으로 저장되었습니다" in result
        assert new_dir.exists()
        assert (new_dir / filename).exists()


class TestLoadGameData:
    """Tests for load_game_data function"""
    
    def test_load_game_data_success(self, sample_game_data, temporary_data_dir):
        """Test successful game data loading"""
        filename = "test_game.json"
        file_path = temporary_data_dir / filename
        
        # Create test file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_game_data, f, ensure_ascii=False, indent=2)
        
        result = load_game_data(str(file_path))
        assert result == sample_game_data
    
    def test_load_game_data_file_not_found(self):
        """Test loading non-existent file"""
        result = load_game_data("non_existent_file.json")
        assert result is None
    
    def test_load_game_data_invalid_json(self, temporary_data_dir):
        """Test loading file with invalid JSON"""
        filename = "invalid.json"
        file_path = temporary_data_dir / filename
        
        # Create file with invalid JSON
        with open(file_path, 'w') as f:
            f.write("invalid json content")
        
        result = load_game_data(str(file_path))
        assert result is None