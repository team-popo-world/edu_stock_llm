"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api import app

client = TestClient(app)


class TestScenarioEndpoints:
    """Tests for scenario-related API endpoints"""
    
    def test_get_scenario_types(self):
        """Test getting available scenario types"""
        response = client.get("/scenario-types")
        assert response.status_code == 200
        
        data = response.json()
        assert "scenario_types" in data
        assert len(data["scenario_types"]) == 4
        
        # Check for required scenario types
        scenario_ids = [s["id"] for s in data["scenario_types"]]
        expected_ids = ["magic_kingdom", "foodtruck_kingdom", "moonlight_thief", "three_little_pigs"]
        assert all(sid in scenario_ids for sid in expected_ids)
    
    @patch('src.api.os.listdir')
    def test_list_scenarios_success(self, mock_listdir):
        """Test listing scenarios successfully"""
        mock_listdir.return_value = ["game1.json", "game2.json", "not_json.txt"]
        
        response = client.get("/scenarios")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert "game1.json" in data
        assert "game2.json" in data
        assert "not_json.txt" not in data
    
    @patch('src.api.os.listdir')
    def test_list_scenarios_directory_not_found(self, mock_listdir):
        """Test listing scenarios when directory doesn't exist"""
        mock_listdir.side_effect = FileNotFoundError()
        
        response = client.get("/scenarios")
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('src.api.load_game_data')
    def test_get_scenario_by_id_success(self, mock_load):
        """Test getting scenario by ID successfully"""
        mock_data = [{"turn": 1, "stocks": []}]
        mock_load.return_value = mock_data
        
        response = client.get("/scenario/test_scenario.json")
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario_id"] == "test_scenario.json"
        assert data["data"] == mock_data
    
    @patch('src.api.load_game_data')
    def test_get_scenario_by_id_not_found(self, mock_load):
        """Test getting non-existent scenario"""
        mock_load.return_value = None
        
        response = client.get("/scenario/non_existent.json")
        assert response.status_code == 404
    
    @patch('src.api.generate_game_data')
    @patch('src.api.initialize_llm')
    @patch('src.api.parse_json_data')
    @patch('src.api.save_game_data')
    def test_generate_scenario_success(self, mock_save, mock_parse, mock_llm, mock_generate):
        """Test generating new scenario successfully"""
        mock_llm.return_value = MagicMock()
        mock_generate.return_value = '{"test": "data"}'
        mock_parse.return_value = {"test": "data"}
        mock_save.return_value = "저장 성공"
        
        response = client.post("/scenario/generate", json={"scenario_type": "magic_kingdom"})
        assert response.status_code == 200
        
        data = response.json()
        assert "scenario_id" in data
        assert data["scenario_type"] == "magic_kingdom"
        assert data["data"] == {"test": "data"}
    
    @patch('src.api.initialize_llm')
    def test_generate_scenario_llm_failure(self, mock_llm):
        """Test scenario generation when LLM fails"""
        mock_llm.side_effect = Exception("LLM failed")
        
        response = client.post("/scenario/generate")
        assert response.status_code == 500


class TestSimulationEndpoints:
    """Tests for simulation-related API endpoints"""
    
    @patch('src.api.load_game_data')
    @patch('src.api.run_automated_simulation')
    def test_run_simulation_success(self, mock_simulation, mock_load):
        """Test running simulation successfully"""
        mock_load.return_value = [{"turn": 1, "stocks": []}]
        mock_simulation.return_value = {
            "final_capital": 11000,
            "profit_rate": 0.1
        }
        
        request_data = {
            "scenario_id": "test_scenario.json",
            "strategies": ["conservative", "aggressive"]
        }
        
        response = client.post("/simulation/run_automated", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["scenario_id"] == "test_scenario.json"
        assert "results" in data
        assert data["results"]["conservative"]["final_capital"] == 11000
        assert data["results"]["aggressive"]["final_capital"] == 11000
    
    @patch('src.api.load_game_data')
    def test_run_simulation_scenario_not_found(self, mock_load):
        """Test running simulation with non-existent scenario"""
        mock_load.return_value = None
        
        request_data = {
            "scenario_id": "non_existent.json",
            "strategies": ["conservative"]
        }
        
        response = client.post("/simulation/run_automated", json=request_data)
        assert response.status_code == 404
    
    @patch('src.api.load_game_data')
    @patch('src.api.run_automated_simulation')
    def test_run_simulation_strategy_failure(self, mock_simulation, mock_load):
        """Test running simulation when strategy fails"""
        mock_load.return_value = [{"turn": 1, "stocks": []}]
        mock_simulation.side_effect = Exception("Strategy failed")
        
        request_data = {
            "scenario_id": "test_scenario.json",
            "strategies": ["conservative"]
        }
        
        response = client.post("/simulation/run_automated", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["results"]["conservative"] is None