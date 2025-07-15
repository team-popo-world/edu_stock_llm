# CLAUDE.md

이 파일은 이 저장소에서 코드 작업을 할 때 Claude Code (claude.ai/code)를 위한 가이드를 제공합니다.

## 프로젝트 개요

10세 이하 아동을 위한 교육용 주식 투자 시뮬레이션 게임입니다. Google Gemini AI를 사용하여 아이들이 동화같은 테마를 통해 기본적인 투자 개념을 배울 수 있는 스토리 기반 시나리오를 생성합니다.

## 개발 명령어

### 환경 설정
```bash
# 가상환경 생성 및 활성화
uv venv
source .venv/bin/activate

# 의존성 설치
uv sync
# 또는
uv pip install -r requirements.txt
```

### 애플리케이션 실행
```bash
# 주요 실행 방법 (하나를 선택하세요):

# 1. 편의 스크립트로 빠른 시작
chmod +x run_game.sh
./run_game.sh

# 2. Streamlit 웹 앱 (사용자에게 권장)
streamlit run src/streamlit_app.py

# 3. 기존 데이터로 CLI 실행 (API 키 불필요)
python src/main.py --use-existing --input-file data/game_scenario_magic_kingdom_20250610_164018.json --simulate

# 4. 새로운 시나리오 생성으로 CLI 실행 (Google API 키 필요)
python src/main.py --scenario-type magic_kingdom --visualize --simulate --save-viz

# 5. 개발자용 API 서버
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### 개발 도구
```bash
# 개발/실험용 Jupyter notebook
jupyter lab
# 또는
jupyter notebook

# LLM 테스트를 위해 notebook/langchain.ipynb 열기
```

## API 키 설정

이 프로젝트는 Google Gemini API 키가 필요합니다. 다음 방법 중 하나로 설정하세요:

1. **로컬 개발**: `.env` 파일에 `GOOGLE_API_KEY=your-key` 작성
2. **Streamlit Cloud**: 앱 시크릿에 `GOOGLE_API_KEY = "your-key"` 설정
3. **환경 변수**: `export GOOGLE_API_KEY="your-key"`

API 키 발급: https://aistudio.google.com/

## 코드 아키텍처

### 핵심 구성요소

- **src/main.py**: CLI 진입점 및 메인 파이프라인 관리
- **src/streamlit_app.py**: Streamlit으로 구축된 웹 UI
- **src/api.py**: 외부 통합을 위한 FastAPI REST 서버

### 주요 모듈

- **src/models/llm_handler.py**: Google Gemini AI 통합 및 스토리 생성
- **src/game/game_logic.py**: 핵심 게임 메커니즘 및 투자 시뮬레이션
- **src/game/session_manager.py**: 게임 상태 관리 및 턴 진행
- **src/simulation/simulator.py**: 투자 전략 시뮬레이션 (4가지 전략: random, conservative, aggressive, trend)
- **src/data/data_handler.py**: JSON 데이터 파싱, 저장, 불러오기
- **src/visualization/visualize.py**: Matplotlib 및 Plotly를 이용한 차트 생성
- **src/ui/**: Streamlit UI 구성요소 및 스타일링

### 게임 테마

프로젝트는 4가지 다른 스토리라인 테마를 지원합니다:
- **magic_kingdom**: 빵집, 서커스, 마법연구소가 있는 동화 속 마법 세계
- **foodtruck_kingdom**: 샌드위치, 아이스크림, 퓨전 타코 트럭이 있는 푸드트럭 세계
- **moonlight_thief**: 달빛 가루, 목걸이, 방패가 있는 신비로운 달빛 도시
- **three_little_pigs**: 지푸라기집, 나무집, 벽돌집이 있는 건설 세계

### 데이터 흐름

1. **스토리 생성**: LLM이 일일 뉴스/이벤트가 포함된 7일간의 투자 시나리오 생성
2. **게임 시뮬레이션**: 플레이어가 3가지 위험 수준에 걸쳐 투자 결정 내리기
3. **결과 분석**: 포트폴리오 성과 추적 및 교육적 피드백
4. **시각화**: 투자 결과를 보여주는 인터랙티브 차트

### 파일 구조

- **data/**: 생성된 게임 시나리오 JSON 파일
- **src/ai/**: AI 에이전트 및 플레이어 프로필 관리
- **src/utils/**: 설정, 프롬프트, 유틸리티 함수
- **visualization_results/**: 생성된 차트 이미지
- **notebook/**: 개발 및 실험용 노트북

## 개발 노트

- 프로젝트는 UV 패키지 매니저와 함께 Python 3.9+ 사용
- 공식적인 테스트 스위트 없음 - 수동 테스트 및 데이터 검증에 의존
- 게임 데이터는 타임스탬프 기반 이름으로 JSON 형식으로 저장
- Streamlit Cloud 배포 지원
- 모든 AI 상호작용은 Google Gemini 2.5 Flash Preview 모델 사용
- 교육적 초점: 스토리텔링을 통한 위험/수익 개념 교육

## 일반적인 작업

- **새로운 테마 추가**: `src/utils/prompts.py`와 시나리오 타입 선택 옵션 업데이트
- **AI 동작 수정**: `src/utils/prompts.py`의 프롬프트 편집
- **UI 스타일 변경**: `src/ui/styles.py`와 `src/streamlit_app.py`의 CSS 업데이트
- **투자 전략 추가**: `src/simulation/simulator.py` 확장
- **LLM 문제 디버깅**: 테스트용 `notebook/langchain.ipynb` 사용