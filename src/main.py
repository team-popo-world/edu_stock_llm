"""
메인 파이프라인 실행 모듈 - 데이터 생성에서 시각화까지
"""
import os
import sys
import argparse
from datetime import datetime

# 현재 파일의 상위 디렉토리를 시스템 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 내부 모듈 가져오기
from src.utils.config import load_api_key, get_model_settings
from src.utils.prompts import get_system_prompt, get_game_scenario_prompt
from src.models.llm_handler import initialize_llm, create_prompt_template, generate_game_data
from src.data.data_handler import parse_json_data, save_game_data, load_game_data
from src.visualization.visualize import visualize_stock_values, save_visualization
from src.simulation.simulator import run_simulation, run_automated_simulation

def create_directory_if_not_exists(path):
    """지정된 경로가 존재하지 않으면 생성합니다."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"디렉토리 생성: {path}")

def select_scenario_type(args):
    """
    시나리오 타입을 선택합니다.
    
    Args:
        args: 명령줄 인자
        
    Returns:
        str: 선택된 시나리오 타입
    """
    # 명령줄에서 시나리오가 지정된 경우
    if args.scenario_type:
        return args.scenario_type
    
    # 인터랙티브 선택
    print("🎭 게임 시나리오를 선택해주세요!")
    print("=" * 50)
    print("1) 🏰 마법 왕국 (magic_kingdom)")
    print("   - 빵집, 서커스단, 마법연구소")
    print("   - 마법사가 되어 마법 코인으로 투자하는 이야기")
    print()
    print("2) 🚚 푸드트럭 왕국 (foodtruck_kingdom)")
    print("   - 샌드위치 트럭, 아이스크림 트럭, 퓨전 타코 트럭")
    print("   - 요리사가 되어 미식 코인으로 투자하는 이야기")
    print()
    print("3) 🌙 달빛 도둑 (moonlight_thief)")
    print("   - 암시장 도둑단, 밀수업체, 정보브로커")
    print("   - 달빛 도시의 암시장에서 루나 코인으로 투자하는 이야기")
    print()
    
    while True:
        choice = input("시나리오를 선택하세요 (1, 2, 또는 3): ").strip()
        if choice == "1":
            return "magic_kingdom"
        elif choice == "2":
            return "foodtruck_kingdom"
        elif choice == "3":
            return "moonlight_thief"
        else:
            print("❌ 잘못된 선택입니다. 1, 2, 또는 3을 입력해주세요.")

def generate_pipeline(args):
    """전체 파이프라인을 실행합니다."""
    print("스토리텔링 주식회사 투자 시뮬레이션 파이프라인 시작...")
    
    # 시나리오 타입 선택
    scenario_type = select_scenario_type(args)
    print(f"\n✅ 선택된 시나리오: {scenario_type}")
    
    # 기본 디렉토리 확인 및 생성
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_dir, "data")
    create_directory_if_not_exists(data_dir)
    
    if args.use_existing and args.input_file:
        # 기존 데이터 사용
        print(f"기존 데이터 파일 사용: {args.input_file}")
        game_data = load_game_data(args.input_file)
        if game_data is None:
            print("데이터 로드 실패. 프로그램을 종료합니다.")
            return
    else:
        # 새로운 데이터 생성
        max_retries = 3  # 최대 재시도 횟수
        attempt = 0
        game_data = None
        
        while game_data is None and attempt < max_retries:
            attempt += 1
            print(f"\n시도 {attempt}/{max_retries}")
            
            try:
                # LLM 초기화
                llm = initialize_llm()
                
                # 프롬프트 준비
                system_prompt = get_system_prompt()
                prompt_template = create_prompt_template(system_prompt)
                game_scenario_prompt = get_game_scenario_prompt(scenario_type)  # 선택된 시나리오 타입 전달
                
                # 게임 데이터 생성
                json_content = generate_game_data(llm, prompt_template, game_scenario_prompt)
                
                # JSON 파싱
                game_data = parse_json_data(json_content)
                if game_data is None:
                    print(f"JSON 파싱 실패. 재시도 중... ({attempt}/{max_retries})")
                    continue
                
                # 성공적으로 파싱되면 반복 종료
                break
                
            except Exception as e:
                print(f"데이터 생성 중 오류 발생: {e}")
                print(f"재시도 중... ({attempt}/{max_retries})")
        
        # 모든 시도 후에도 데이터 생성에 실패한 경우
        if game_data is None:
            print("\n모든 시도 후에도 데이터 생성에 실패했습니다.")
            use_sample = input("샘플 데이터를 사용하시겠습니까? (y/n): ")
            if use_sample.lower() == 'y':
                from src.data.data_handler import create_sample_game_data
                game_data = create_sample_game_data()
            else:
                print("프로그램을 종료합니다.")
                return
        
        # 데이터 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.output_file:
            output_file = args.output_file
        else:
            output_file = f"game_scenario_{scenario_type}_{timestamp}.json"  # 시나리오 타입 포함
        
        save_path = save_game_data(game_data, data_dir, output_file)
    
    # 데이터 시각화
    if args.visualize:
        print("\n게임 데이터 시각화 중...")
        visualize_stock_values(game_data)
        
        # 시각화 저장
        if args.save_viz:
            viz_dir = os.path.join(project_dir, "visualization_results")
            create_directory_if_not_exists(viz_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            viz_path = os.path.join(viz_dir, f"stock_values_{timestamp}.png")
            save_visualization(game_data, viz_path)
    
    # 시뮬레이션 실행
    if args.simulate:
        if args.auto_sim:
            print("\n자동화된 시뮬레이션 실행 중...")
            # 여러 전략으로 시뮬레이션 실행 및 결과 비교
            strategies = ["random", "conservative", "aggressive", "trend"]
            results = {}
            
            for strategy in strategies:
                print(f"\n{strategy} 전략으로 시뮬레이션 실행...")
                result = run_automated_simulation(game_data, strategy)
                results[strategy] = result
            
            # 결과 비교
            print("\n===== 전략별 시뮬레이션 결과 비교 =====")
            valid_results = {}
            for strategy, result in results.items():
                if result:
                    print(f"{strategy}: 최종 자본금 {result['final_capital']:.1f}원, 수익률 {result['profit_rate']:.1f}%")
                    valid_results[strategy] = result
            
            # 최고 수익률 전략 확인
            if valid_results:
                best_strategy = max(valid_results.keys(), key=lambda k: valid_results[k]['profit_rate'])
                print(f"\n가장 좋은 결과를 보인 전략: {best_strategy}, 수익률: {valid_results[best_strategy]['profit_rate']:.1f}%")
            else:
                print("\n유효한 시뮬레이션 결과가 없습니다.")
        else:
            print("\n인터랙티브 시뮬레이션 실행 중...")
            result = run_simulation(game_data)
    
    print("\n파이프라인 실행 완료!")

if __name__ == "__main__":
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description="스토리텔링 주식 투자 시뮬레이션")
    
    parser.add_argument("--use-existing", action="store_true", 
                        help="기존 JSON 파일 사용")
    parser.add_argument("--input-file", type=str, 
                        help="사용할 기존 JSON 파일 경로")
    parser.add_argument("--output-file", type=str, 
                        help="생성된 데이터를 저장할 파일 이름")
    parser.add_argument("--visualize", action="store_true", 
                        help="데이터 시각화 수행")
    parser.add_argument("--save-viz", action="store_true", 
                        help="시각화 결과 저장")
    parser.add_argument("--simulate", action="store_true", 
                        help="시뮬레이션 실행")
    parser.add_argument("--auto-sim", action="store_true", 
                        help="자동화된 시뮬레이션 실행")
    parser.add_argument("--scenario-type", type=str, choices=["magic_kingdom", "foodtruck_kingdom", "moonlight_thief"], 
                        help="시나리오 타입 선택 (magic_kingdom, foodtruck_kingdom, 또는 moonlight_thief)")
    
    args = parser.parse_args()
    
    generate_pipeline(args)
