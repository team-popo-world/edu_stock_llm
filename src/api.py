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

from src.utils.config import load_api_key, get_model_settings
from src.utils.prompts import get_system_prompt, get_game_scenario_prompt
from src.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
from src.data.data_handler import parse_json_data, save_game_data, load_game_data, create_sample_game_data
from src.simulation.simulator import run_automated_simulation

app = FastAPI(
    title="아기돼지 삼형제 주식회사 투자 시뮬레이션 API",
    description="LLM을 활용한 주식 투자 시나리오 생성 및 시뮬레이션 API입니다.",
    version="0.1.0"
)

# CORS 미들웨어 설정 - 프론트엔드가 API에 접근할 수 있도록 함
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 출처만 허용하는 것이 좋습니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic 모델 정의 ---
class ScenarioParameters(BaseModel):
    # 필요에 따라 LLM에 전달할 파라미터 정의 (예: 난이도, 특정 이벤트 등)
    # 현재는 get_game_scenario_prompt()가 파라미터 없이 작동하므로 비워둡니다.
    pass

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
        llm = initialize_llm()
        system_prompt = get_system_prompt()
        prompt_template = create_prompt_template(system_prompt)
        # params를 사용하여 game_scenario_prompt를 동적으로 변경할 수 있습니다.
        # 현재는 get_game_scenario_prompt가 파라미터 없이 작동합니다.
        game_scenario_prompt_text = get_game_scenario_prompt()

        json_content = generate_game_data(llm, prompt_template, game_scenario_prompt_text)
        game_data = parse_json_data(json_content)

        if game_data is None:
            raise HTTPException(status_code=500, detail="LLM으로부터 유효한 시나리오 데이터를 생성하지 못했습니다.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"game_scenario_{timestamp}.json"
        save_game_data(game_data, BASE_DATA_DIR, output_filename)
        
        return {"scenario_id": output_filename, "data": game_data}

    except Exception as e:
        # 실제 운영 환경에서는 더 구체적인 오류 처리 및 로깅이 필요합니다.
        raise HTTPException(status_code=500, detail=f"시나리오 생성 중 오류 발생: {str(e)}")

@app.get("/scenario/{scenario_id}", summary="특정 게임 시나리오 조회", response_model=Dict[str, Any])
async def get_scenario_by_id(scenario_id: str = Path(..., description="조회할 시나리오의 파일명 (예: game_scenario_20250520_153342.json)")):
    """
    저장된 게임 시나리오를 ID(파일명)를 통해 조회합니다.
    """
    file_path = os.path.join(BASE_DATA_DIR, scenario_id)
    if not scenario_id.endswith(".json"): # 간단한 유효성 검사
        file_path_with_ext = f"{file_path}.json"
        if os.path.exists(file_path_with_ext):
            file_path = file_path_with_ext
        else: # 확장자 없이도 파일이 없다면 원래 경로로 진행하여 에러 처리
             pass


    game_data = load_game_data(file_path)
    if game_data is None:
        raise HTTPException(status_code=404, detail=f"시나리오 '{scenario_id}'를 찾을 수 없습니다.")
    return {"scenario_id": scenario_id, "data": game_data}

@app.post("/simulation/run_automated", summary="자동 투자 시뮬레이션 실행", response_model=SimulationResponse)
async def run_automated_investment_simulation(request: SimulationRequest):
    """
    주어진 시나리오 ID와 전략들을 사용하여 자동 투자 시뮬레이션을 실행하고 결과를 반환합니다.
    """
    scenario_file_path = os.path.join(BASE_DATA_DIR, request.scenario_id)
    game_data = load_game_data(scenario_file_path)

    if game_data is None:
        raise HTTPException(status_code=404, detail=f"시뮬레이션을 위한 시나리오 '{request.scenario_id}'를 찾을 수 없습니다.")

    simulation_results: Dict[str, Optional[SimulationResultItem]] = {}
    for strategy in request.strategies:
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
            print(f"전략 '{strategy}' 실행 중 오류: {e}") # 로깅
            simulation_results[strategy] = None


    valid_results = {k: v for k, v in simulation_results.items() if v is not None}
    best_strategy_name: Optional[str] = None
    best_profit: Optional[float] = None

    if valid_results:
        best_strategy_name = max(valid_results.keys(), key=lambda k: valid_results[k].profit_rate if valid_results[k] else -float('inf'))
        if best_strategy_name and valid_results[best_strategy_name]:
             best_profit = valid_results[best_strategy_name].profit_rate


    return SimulationResponse(
        scenario_id=request.scenario_id,
        results=simulation_results,
        best_strategy=best_strategy_name,
        best_profit_rate=best_profit
    )

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