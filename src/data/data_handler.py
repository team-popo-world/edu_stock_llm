"""
데이터 처리 및 저장 모듈
"""
import os
import json
import pprint
from typing import Optional, Dict, Any, List
from ..utils.logger import log_error, log_warning, log_info

def parse_json_data(json_content):
    """
    JSON 문자열을 파싱하여 Python 객체로 변환합니다.
    
    Args:
        json_content (str): 파싱할 JSON 문자열
        
    Returns:
        dict or None: 파싱된 Python 객체 또는 파싱 실패 시 None
    """
    if json_content is None or not json_content.strip():
        print("파싱할 JSON 내용이 없습니다.")
        return None
        
    try:
        # JSON 문자열의 앞뒤 공백 제거
        json_content = json_content.strip()
        
        # 마크다운 코드 블록 처리 (LLM 핸들러에서 이미 처리했을 수 있지만 확실히 하기 위해)
        if json_content.startswith("```"):
            # 코드 블록 제거
            lines = json_content.split("\n")
            if len(lines) > 2:  # 코드 블록이 최소 3줄을 가짐 (시작, 내용, 종료)
                json_content = "\n".join(lines[1:-1])
            
        # 유효한 JSON인지 확인
        game_data = json.loads(json_content)
        
        # 기본 구조 확인
        if not isinstance(game_data, list):
            print("경고: 반환된 데이터가 리스트 형식이 아닙니다.")
            
            # 데이터가 리스트가 아닌 경우 리스트로 변환 시도
            if isinstance(game_data, dict) and 'stocks' in game_data:
                # 단일 턴 데이터로 보임
                print("단일 턴 데이터를 감지했습니다. 리스트로 변환합니다.")
                game_data = [game_data]
            else:
                print("데이터 구조가 예상과 다릅니다. 기본 구조로 변환을 시도합니다.")
                # 여기서 더 복잡한 변환 로직을 추가할 수 있음
                # 현재는 단순 패스
        
        # 턴 번호 확인 및 수정
        for i, turn in enumerate(game_data):
            if 'turn_number' not in turn or not isinstance(turn['turn_number'], int):
                print(f"경고: 턴 {i+1}의 turn_number가 올바르지 않습니다. 수정합니다.")
                turn['turn_number'] = i+1
                
            # 각 턴의 'stocks' 데이터가 리스트인지 확인
            if 'stocks' not in turn or not isinstance(turn['stocks'], list):
                print(f"경고: 턴 {i+1}의 stocks 데이터가 없거나 리스트가 아닙니다.")
                
                # 기본 stocks 구조 생성
                turn['stocks'] = [
                    {
                        "name": "첫째집",
                        "description": "지푸라기로 만든 집",
                        "initial_value": 100,
                        "current_value": 100 + (i * 2),
                        "risk_level": "고위험 고수익"
                    },
                    {
                        "name": "둘째집",
                        "description": "나무로 만든 집",
                        "initial_value": 100,
                        "current_value": 100 + (i * 1),
                        "risk_level": "균형형"
                    },
                    {
                        "name": "셋째집",
                        "description": "벽돌로 만든 집",
                        "initial_value": 100,
                        "current_value": 100 + (i * 3),
                        "risk_level": "장기 투자 적합"
                    }
                ]
        
        # 정렬
        game_data.sort(key=lambda x: x['turn_number'])
        
        print("\n파싱된 데이터 구조 (첫 번째 턴 샘플):")
        if game_data and len(game_data) > 0:
            pprint.pprint(game_data[0], indent=2)
            print(f"\n총 {len(game_data)}개의 턴 데이터가 성공적으로 파싱되었습니다.")
        return game_data
        
    except json.JSONDecodeError as e:
        print(f"\nJSON 파싱 오류: {e}")
        print("LLM의 원본 응답 내용을 확인하세요. 완전한 JSON 형식이 아닐 수 있습니다.")
        print("\n원본 응답 (처음 300자):")
        print(json_content[:300] + "..." if len(json_content) > 300 else json_content)
        
        # JSON 문자열 수정 시도
        try:
            print("\nJSON 문자열 수정 시도...")
            
            # 1. 잘못된 문자 제거 시도 (제어 문자, 이스케이프 문자 등)
            import re
            cleaned_content = re.sub(r'[\x00-\x1F\x7F]', '', json_content)
            
            # 2. 주석 및 후행 쉼표 제거 시도
            cleaned_content = re.sub(r'//.*?\n|/\*.*?\*/', '', cleaned_content, flags=re.DOTALL)
            cleaned_content = re.sub(r',\s*([}\]])', r'\1', cleaned_content)
            
            # 3. 추가 키 값 쌍이 없는데도 있는 쉼표 제거
            cleaned_content = re.sub(r',\s*([}\]])', r'\1', cleaned_content)
            
            # 4. 올바른 JSON 추출 시도
            json_pattern = r'(\[.*?\]|\{.*?\})'
            matches = re.findall(json_pattern, cleaned_content, re.DOTALL)
            
            if matches:
                # 가장 긴 매치 사용
                potential_json = max(matches, key=len)
                print(f"잠재적 JSON 구조 찾음 (길이: {len(potential_json)})")
                
                # 파싱 시도
                game_data = json.loads(potential_json)
                print("수정된 JSON 파싱 성공!")
                
                # 기본 구조 확인
                if not isinstance(game_data, list):
                    if isinstance(game_data, dict) and 'stocks' in game_data:
                        game_data = [game_data]
                    else:
                        raise ValueError("JSON 구조가 예상과 다릅니다.")
                
                # 데이터 검증
                for i, turn in enumerate(game_data):
                    if 'turn_number' not in turn:
                        turn['turn_number'] = i+1
                
                return game_data
        except Exception as repair_error:
            print(f"JSON 수정 실패: {repair_error}")
            
        # 자동으로 샘플 데이터 사용 (비대화형 환경 지원)
        log_error("JSON 파싱에 실패했습니다. 샘플 데이터를 사용합니다.")
        return create_sample_game_data()
        
    except Exception as e:
        log_error("데이터 처리 중 예기치 않은 오류 발생", e)
        log_warning("예기치 않은 오류가 발생했습니다. 샘플 데이터를 사용합니다.")
        return create_sample_game_data()

def save_game_data(data, base_dir=None, filename="game_scenario.json"):
    """
    게임 데이터를 JSON 파일로 저장합니다.
    
    Args:
        data: 저장할 게임 데이터
        base_dir (str, optional): 저장할 기본 디렉토리. 기본값은 None (현재 디렉토리 사용)
        filename (str, optional): 저장할 파일 이름. 기본값은 "game_scenario.json"
        
    Returns:
        str: 성공 여부 메시지
    """
    if data is None:
        return "저장할 데이터가 없습니다. JSON 파싱 오류를 확인하세요."
    
    try:
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 상위 디렉토리의 data 폴더로 이동
            base_dir = os.path.join(os.path.dirname(os.path.dirname(base_dir)), "data")
            
            # 디렉토리가 없으면 생성
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
                
        save_path = os.path.join(base_dir, filename)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"데이터가 성공적으로 {save_path}에 저장되었습니다.")
        return save_path
    except Exception as e:
        error_msg = f"데이터 저장 중 오류 발생: {e}"
        print(error_msg)
        return error_msg

def load_game_data(file_path):
    """
    저장된 게임 데이터를 불러옵니다.
    
    Args:
        file_path (str): 불러올 파일의 경로
        
    Returns:
        dict or None: 불러온 게임 데이터 또는 실패 시 None
    """
    try:
        if not os.path.exists(file_path):
            print(f"파일이 존재하지 않습니다: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"데이터를 성공적으로 불러왔습니다: {file_path}")
        return data
    except Exception as e:
        print(f"데이터 불러오기 중 오류 발생: {e}")
        return None

def create_sample_game_data():
    """
    샘플 게임 데이터를 생성합니다. LLM 호출 실패 시 사용됩니다.
    
    Returns:
        list: 샘플 게임 데이터
    """
    print("샘플 게임 데이터를 생성합니다...")
    
    sample_data = [
        {
            "turn_number": 1,
            "news": "이번 주 날씨는 맑음! 첫째 돼지의 지푸라기 집이 빠르게 완성되어 인기가 치솟고 있어요!",
            "event_description": "없음",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 110,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 100,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 100,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 2,
            "news": "일기예보: 2턴 뒤에 강력한 태풍이 몰려올 수 있다는 소식입니다! 투자에 유의하세요.",
            "event_description": "없음",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 105,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 98,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 102,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 3,
            "news": "긴급 속보: 태풍이 예상보다 빠르게 북상 중! 특히 둘째 돼지의 나무 집이 강풍에 취약할 수 있다는 분석이 나왔습니다.",
            "event_description": "없음",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 95,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 90,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 105,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 4,
            "news": "태풍이 드디어 상륙했습니다! 거센 비바람이 몰아치고 있습니다.",
            "event_description": "초대형 태풍 발생! 둘째 돼지의 나무 집이 심각한 피해를 입어 가치가 폭락했습니다! 첫째 돼지의 지푸라기 집도 일부 손상되었습니다.",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 65,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 15,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 110,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 5,
            "news": "태풍이 지나갔습니다. 셋째 돼지의 벽돌 집은 튼튼함을 증명하며 가치가 더욱 상승했습니다! 반면, 다른 집들은 피해 복구에 시간이 걸릴 것 같습니다.",
            "event_description": "셋째집 안전성 재평가.",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 68,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 20,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 135,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 6,
            "news": "첫째 돼지가 빠른 복구 작업을 시작했습니다. 민첩한 대응으로 투자자들의 신뢰를 회복하고 있습니다.",
            "event_description": "첫째집 복구 작업 시작",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 80,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 25,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 140,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 7,
            "news": "둘째 돼지가 혁신적인 나무 보강 기술을 도입했다는 소식입니다. 이것이 둘째집의 가치를 회복시킬 수 있을까요?",
            "event_description": "둘째집 기술 혁신",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 90,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 45,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 138,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 8,
            "news": "셋째 돼지가 주택 안전 협회로부터 최고 등급 인증을 받았습니다! 이로써 셋째집의 가치는 더욱 상승할 전망입니다.",
            "event_description": "셋째집 안전 인증 획득",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 95,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 60,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 150,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 9,
            "news": "여름 휴가철이 다가오면서 가벼운 첫째집에 대한 수요가 늘고 있습니다. 빠른 건축 속도로 인기를 끌고 있습니다.",
            "event_description": "첫째집 계절적 수요 증가",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 110,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 70,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 145,
                    "risk_level": "장기 투자 적합"
                }
            ]
        },
        {
            "turn_number": 10,
            "news": "아기돼지 삼형제의 집들이 모두 안정적인 모습을 보이고 있습니다. 각자의 특성에 맞는 시장에서 자리를 잡아가고 있습니다.",
            "event_description": "시장 안정화",
            "stocks": [
                {
                    "name": "첫째집",
                    "description": "지푸라기로 만든 집, 빠른 완공이 특징이지만 내구성이 약함",
                    "initial_value": 100,
                    "current_value": 115,
                    "risk_level": "고위험 고수익"
                },
                {
                    "name": "둘째집",
                    "description": "나무로 만든 집, 적당한 완공 속도와 내구성을 갖춤",
                    "initial_value": 100,
                    "current_value": 85,
                    "risk_level": "균형형"
                },
                {
                    "name": "셋째집",
                    "description": "벽돌로 만든 집, 완공은 느리지만 내구성이 뛰어남",
                    "initial_value": 100,
                    "current_value": 155,
                    "risk_level": "장기 투자 적합"
                }
            ]
        }
    ]
    
    return sample_data
