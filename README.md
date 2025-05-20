# 아기돼지 삼형제 주식회사 투자 시뮬레이션

## 프로젝트 소개

이 프로젝트는 '아기돼지 삼형제 주식회사' 투자 시뮬레이션 게임입니다. OpenAI의 LLM(Large Language Model)을 활용하여 게임 시나리오를 생성하고, 투자 시뮬레이션을 수행합니다. 게임은 아기돼지 삼형제의 집(첫째집-지푸라기, 둘째집-나무, 셋째집-벽돌)을 주식으로 간주하고, 다양한 사건(태풍 등)에 따른 가치 변동을 시뮬레이션합니다.

## 개선사항 (2025년 5월 21일)

### 버그 수정 및 안정성 향상
- **JSON 파싱 오류 개선**
  - LLM 응답에서 코드 블록 마크다운 자동 제거 기능 개선
  - 여러 정규표현식 패턴을 사용한 고급 JSON 추출 로직 구현
  - 상세한 오류 메시지로 디버깅 용이성 향상

- **누락된 데이터 필드 대응**
  - 모든 모듈에서 불완전한 데이터 구조를 안전하게 처리
  - 필드 존재 여부 검사 (`dict.get()` 메소드 활용)
  - 누락된 데이터에 대한 적절한 기본값 제공

- **시각화 모듈 전체 개선**
  - 코드 중복 제거 및 모듈화 (`_prepare_stock_data`, `_create_stock_plot` 등)
  - 한글 폰트 문제 해결 (영어 라벨로 일관성 있게 대체)
  - 새로운 투자 결과 시각화 기능 (`create_investment_summary`) 추가
  - 데이터 비일관성 안전하게 처리 (누락된 주식 정보 등)

- **시뮬레이션 모듈 안정성 향상**
  - 다음 턴 접근 로직 개선 (인덱스 오류 방지)
  - 결과 기록 시 안전한 필드 처리

- **결과 처리 개선**
  - 유효한 시뮬레이션 결과만 처리하는 필터링 단계 추가
  - 전략 비교 로직 안전성 향상

## 설치 및 실행 방법

1. 필요한 패키지 설치:
```bash
pip install python-dotenv langchain-openai langchain matplotlib pandas numpy
```

2. 환경 변수 설정:
- 프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API 키 추가:
```
OPENAI_API_KEY=your_api_key_here
```

3. 실행:
```bash
# 기본 실행 (데이터 생성, 시각화, 시뮬레이션)
python -m src.main --visualize --simulate

# 시각화 결과 저장
python -m src.main --visualize --save-viz

# 기존 데이터 사용
python -m src.main --use-existing --input-file ./data/game_scenario.json --visualize --simulate

# 자동화된 시뮬레이션 실행
python -m src.main --use-existing --input-file ./data/game_scenario.json --simulate --auto-sim
```

## 명령행 인자

| 인자 | 설명 |
|------|------|
| `--use-existing` | 기존 JSON 파일 사용 |
| `--input-file PATH` | 사용할 기존 JSON 파일 경로 |
| `--output-file NAME` | 생성된 데이터를 저장할 파일 이름 |
| `--visualize` | 데이터 시각화 수행 |
| `--save-viz` | 시각화 결과 저장 |
| `--simulate` | 시뮬레이션 실행 |
| `--auto-sim` | 자동화된 시뮬레이션 실행 |

## 프로젝트 구조

```
/src
  ├── __init__.py
  ├── main.py            # 메인 실행 파일
  ├── data/              # 데이터 처리 관련
  │   ├── __init__.py
  │   └── data_handler.py
  ├── models/            # LLM 모델 관련
  │   ├── __init__.py
  │   └── llm_handler.py
  ├── utils/             # 유틸리티 함수
  │   ├── __init__.py
  │   ├── config.py
  │   └── prompts.py
  ├── visualization/     # 시각화 기능
  │   ├── __init__.py
  │   └── visualize.py
  └── simulation/        # 시뮬레이션 기능
      ├── __init__.py
      └── simulator.py
```

## 데이터 구조

아래는 이 프로젝트에서 사용하는 기본 데이터 구조입니다:

```json
[
  {
    "turn_number": 1,
    "news": "이번 주 날씨는 맑음! 첫째 돼지의 지푸라기 집이 빠르게 완성되어 인기가 치솟고 있어요!",
    "event_description": "없음",
    "stocks": [
      {
        "name": "첫째집",
        "description": "지푸라기 집, 빠른 완공, 인기도 높으나 리스크 큼.",
        "initial_value": 100,
        "current_value": 108,
        "risk_level": "고위험 고수익"
      },
      {
        "name": "둘째집",
        "description": "나무 집, 중간 정도의 안정성과 속도.",
        "initial_value": 100,
        "current_value": 100,
        "risk_level": "균형형"
      },
      {
        "name": "셋째집",
        "description": "벽돌 집, 느리지만 안정성 최고.",
        "initial_value": 100,
        "current_value": 100,
        "risk_level": "장기 투자 적합"
      }
    ]
  }
]
```

## 오류 처리 전략

이 프로젝트는 다음과 같은 오류 처리 전략을 구현합니다:

- **데이터 누락 보호**: 모든 딕셔너리 접근은 `dict.get()` 메소드를 사용하여 KeyError 방지
- **JSON 파싱 복원력**: 여러 정규표현식 패턴을 통한 JSON 추출 시도
- **로버스트 시각화**: 누락된 데이터에 대해 자동으로 이전 값이나 기본값 사용
- **점진적 재시도**: LLM 응답 실패 시 최대 3회 재시도
- **폴백 메커니즘**: 모든 생성 시도 실패 시 샘플 데이터 사용 옵션 제공
- **사용자 친화적 오류**: 상세한 오류 메시지로 원인 파악 용이

## 문제해결

- **JSON 파싱 오류**: LLM이 완전한 JSON 형식으로 응답하지 않을 경우 최대 3회 재시도합니다. 그래도 실패할 경우 샘플 데이터 사용 여부를 묻습니다.
- **한글 폰트 오류**: 시각화에서 한글 폰트 관련 오류가 발생할 경우 영어 라벨이 자동으로 사용됩니다.
- **API 키 오류**: `.env` 파일이 없거나 API 키가 잘못된 경우 적절한 오류 메시지가 표시됩니다.
- **불완전한 데이터**: 필수 필드가 누락된 경우에도 프로그램이 안전하게 실행됩니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
