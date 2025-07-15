import os
import sys
import json
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# 기존 프로젝트 모듈 임포트
# 경로 문제를 피하기 위해 sys.path에 프로젝트 루트 추가 고려
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.config import load_api_key, get_model_settings, config
from src.utils.logger import log_error, log_warning, log_info
from src.utils.validators import InputValidator, ValidationError, validate_game_data
from src.utils.prompts import get_system_prompt, get_game_scenario_prompt
from src.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
from src.data.data_handler import parse_json_data, save_game_data, load_game_data, create_sample_game_data
from src.simulation.simulator import run_automated_simulation

app = FastAPI(
    title="스토리텔링 주식 투자 시뮬레이션 API",
    description="LLM을 활용한 주식 투자 시나리오 생성 및 시뮬레이션 API입니다.",
    version="0.1.0"
)

# CORS 미들웨어 설정 - 프론트엔드가 API에 접근할 수 있도록 함
# 환경 변수로 허용된 출처를 설정할 수 있습니다
allowed_origins = config.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- Pydantic 모델 정의 ---
class ScenarioParameters(BaseModel):
    scenario_type: str = Field(default="magic_kingdom", description="시나리오 타입 (magic_kingdom, foodtruck_kingdom, moonlight_thief, 또는 three_little_pigs)")

class SimulationRequest(BaseModel):
    scenario_id: str = Field(..., description="시뮬레이션을 실행할 시나리오 ID (파일명)")
    strategies: List[str] = Field(default=["random", "conservative", "aggressive", "trend"], description="실행할 투자 전략 목록")

class SimulationResultItem(BaseModel):
    final_capital: float
    profit_rate: float

class SimulationResponse(BaseModel):
    scenario_id: str
    results: Dict[str, Optional[SimulationResultItem]]
    best_strategy: Optional[str] = None
    best_profit_rate: Optional[float] = None

# --- API 엔드포인트 ---

BASE_DATA_DIR = os.path.join(project_root, "data")
if not os.path.exists(BASE_DATA_DIR):
    os.makedirs(BASE_DATA_DIR)

@app.post("/scenario/generate", summary="새로운 게임 시나리오 생성", response_model=Dict[str, Any])
async def generate_new_scenario(params: Optional[ScenarioParameters] = None):
    """
    LLM을 사용하여 새로운 게임 시나리오를 생성하고 JSON으로 반환합니다.
    생성된 시나리오는 'data' 디렉토리에 저장됩니다.
    """
    try:
        # 시나리오 타입 결정 및 검증
        scenario_type = "magic_kingdom"  # 기본값
        if params and params.scenario_type:
            try:
                scenario_type = InputValidator.validate_scenario_type(params.scenario_type)
            except ValidationError as e:
                log_error(f"Invalid scenario type: {params.scenario_type}", e)
                raise HTTPException(status_code=400, detail=str(e))
        
        llm = initialize_llm()
        system_prompt = get_system_prompt()
        prompt_template = create_prompt_template(system_prompt)
        # 선택된 시나리오 타입을 사용하여 프롬프트 생성
        game_scenario_prompt_text = get_game_scenario_prompt(scenario_type)

        json_content = generate_game_data(llm, prompt_template, game_scenario_prompt_text)
        game_data = parse_json_data(json_content)

        if game_data is None:
            log_error("LLM failed to generate valid scenario data")
            raise HTTPException(status_code=500, detail="LLM으로부터 유효한 시나리오 데이터를 생성하지 못했습니다.")
        
        # 생성된 데이터 검증
        try:
            game_data = validate_game_data(game_data)
        except ValidationError as e:
            log_error(f"Generated game data validation failed: {e}")
            raise HTTPException(status_code=500, detail=f"생성된 게임 데이터가 유효하지 않습니다: {str(e)}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"game_scenario_{scenario_type}_{timestamp}.json"
        save_game_data(game_data, BASE_DATA_DIR, output_filename)
        
        return {"scenario_id": output_filename, "scenario_type": scenario_type, "data": game_data}

    except HTTPException:
        raise
    except ValidationError as e:
        log_error(f"Validation error during scenario generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_error(f"Unexpected error during scenario generation: {e}", e)
        raise HTTPException(status_code=500, detail="시나리오 생성 중 예상치 못한 오류가 발생했습니다.")

@app.get("/scenario/{scenario_id}", summary="특정 게임 시나리오 조회", response_model=Dict[str, Any])
async def get_scenario_by_id(scenario_id: str = Path(..., description="조회할 시나리오의 파일명 (예: game_scenario_20250520_153342.json)")):
    """
    저장된 게임 시나리오를 ID(파일명)를 통해 조회합니다.
    """
    file_path = os.path.join(BASE_DATA_DIR, scenario_id)
    # 파일 경로 검증
    try:
        scenario_id = InputValidator.validate_file_path(scenario_id, must_exist=False)
    except ValidationError as e:
        log_error(f"Invalid scenario ID: {scenario_id}", e)
        raise HTTPException(status_code=400, detail=str(e))
    
    if not scenario_id.endswith(".json"):
        file_path_with_ext = f"{file_path}.json"
        if os.path.exists(file_path_with_ext):
            file_path = file_path_with_ext
        else:
             pass


    try:
        game_data = load_game_data(file_path)
        if game_data is None:
            log_warning(f"Scenario not found: {scenario_id}")
            raise HTTPException(status_code=404, detail=f"시나리오 '{scenario_id}'를 찾을 수 없습니다.")
        
        log_info(f"Successfully loaded scenario: {scenario_id}")
        return {"scenario_id": scenario_id, "data": game_data}
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error loading scenario {scenario_id}: {e}", e)
        raise HTTPException(status_code=500, detail="시나리오 로딩 중 오류가 발생했습니다.")

@app.post("/simulation/run_automated", summary="자동 투자 시뮬레이션 실행", response_model=SimulationResponse)
async def run_automated_investment_simulation(request: SimulationRequest):
    """
    주어진 시나리오 ID와 전략들을 사용하여 자동 투자 시뮬레이션을 실행하고 결과를 반환합니다.
    """
    try:
        # 요청 데이터 검증
        scenario_id = InputValidator.validate_file_path(request.scenario_id, must_exist=False)
        strategies = InputValidator.validate_strategies(request.strategies)
        
        scenario_file_path = os.path.join(BASE_DATA_DIR, scenario_id)
        game_data = load_game_data(scenario_file_path)

        if game_data is None:
            log_warning(f"Scenario not found for simulation: {scenario_id}")
            raise HTTPException(status_code=404, detail=f"시뮬레이션을 위한 시나리오 '{scenario_id}'를 찾을 수 없습니다.")
        
        log_info(f"Starting simulation for scenario: {scenario_id} with strategies: {strategies}")
    except ValidationError as e:
        log_error(f"Validation error in simulation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"Error preparing simulation: {e}", e)
        raise HTTPException(status_code=500, detail="시뮬레이션 준비 중 오류가 발생했습니다.")

    simulation_results: Dict[str, Optional[SimulationResultItem]] = {}
    for strategy in strategies:
        try:
            # run_automated_simulation 함수가 반환하는 값의 형태에 따라 result 처리
            raw_result = run_automated_simulation(game_data, strategy) # 기존 함수 호출
            if raw_result and 'final_capital' in raw_result and 'profit_rate' in raw_result:
                 simulation_results[strategy] = SimulationResultItem(
                    final_capital=raw_result['final_capital'],
                    profit_rate=raw_result['profit_rate']
                )
            else:
                simulation_results[strategy] = None # 혹은 오류 처리
        except Exception as e:
            # 개별 전략 실행 오류 처리
            log_error(f"Strategy '{strategy}' execution failed: {e}", e)
            simulation_results[strategy] = None


    valid_results = {k: v for k, v in simulation_results.items() if v is not None}
    best_strategy_name: Optional[str] = None
    best_profit: Optional[float] = None

    if valid_results:
        best_strategy_name = max(valid_results.keys(), key=lambda k: valid_results[k].profit_rate if valid_results[k] else -float('inf'))
        if best_strategy_name and valid_results[best_strategy_name]:
             best_profit = valid_results[best_strategy_name].profit_rate


    try:
        log_info(f"Simulation completed for scenario: {scenario_id}. Best strategy: {best_strategy_name}")
        return SimulationResponse(
            scenario_id=scenario_id,
            results=simulation_results,
            best_strategy=best_strategy_name,
            best_profit_rate=best_profit
        )
    except Exception as e:
        log_error(f"Error creating simulation response: {e}", e)
        raise HTTPException(status_code=500, detail="시뮬레이션 결과 생성 중 오류가 발생했습니다.")

@app.get("/scenario-types", summary="사용 가능한 시나리오 타입 조회", response_model=Dict[str, Any])
async def get_scenario_types():
    """
    사용 가능한 게임 시나리오 타입 목록과 설명을 반환합니다.
    """
    return {
        "scenario_types": [
            {
                "id": "magic_kingdom",
                "name": "🏰 마법 왕국",
                "description": "빵집, 서커스단, 마법연구소 - 마법사가 되어 마법 코인으로 투자하는 이야기"
            },
            {
                "id": "foodtruck_kingdom", 
                "name": "🚚 푸드트럭 왕국",
                "description": "샌드위치 트럭, 아이스크림 트럭, 퓨전 타코 트럭 - 요리사가 되어 미식 코인으로 투자하는 이야기"
            },
            {
                "id": "moonlight_thief",
                "name": "🌙 달빛 도둑",
                "description": "달빛 가루 수집, 달조각 목걸이, 달빛 방패 - 달빛 도둑이 되어 달빛 코인으로 투자하는 이야기"
            },
            {
                "id": "three_little_pigs",
                "name": "🐷 아기돼지 삼형제",
                "description": "첫째 돼지(지푸라기집), 둘째 돼지(나무집), 셋째 돼지(벽돌집) - 투자 고문이 되어 건설 코인으로 투자하는 이야기"
            }
        ]
    }

@app.get("/scenarios", summary="저장된 모든 시나리오 목록 조회", response_model=List[str])
async def list_all_scenarios():
    """
    'data' 디렉토리에 저장된 모든 게임 시나리오 파일 목록을 반환합니다.
    """
    try:
        files = [f for f in os.listdir(BASE_DATA_DIR) if os.path.isfile(os.path.join(BASE_DATA_DIR, f)) and f.endswith(".json")]
        return files
    except FileNotFoundError:
        return [] # data 디렉토리가 없는 경우 빈 리스트 반환
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시나리오 목록 조회 중 오류 발생: {str(e)}")


# --- Uvicorn 실행을 위한 설정 (선택 사항) ---
# 이 파일이 직접 실행될 때 uvicorn 서버를 시작하려면 아래 주석을 해제합니다.
# if __name__ == "__main__":
#     import uvicorn
#     # load_dotenv() # .env 파일 로드를 위해 필요할 수 있음 (initialize_llm 내부에서 호출되지만 명시적으로 호출 가능)
#     uvicorn.run(app, host="0.0.0.0", port=8000)