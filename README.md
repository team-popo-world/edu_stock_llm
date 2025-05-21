# 아기돼지 삼형제 주식회사 투자 시뮬레이션

LLM을 활용한 주식 투자 시나리오 생성 및 시뮬레이션 교육용 프로젝트입니다. OpenAI의 GPT 모델과 LangChain을 사용하여 동적으로 게임 시나리오를 만들고, 다양한 투자 전략을 시뮬레이션하며, FastAPI를 통해 API를 제공합니다.

## 주요 기능

*   LLM (OpenAI GPT 모델) 기반 동적 게임 시나리오 생성
*   다양한 자동 투자 전략 시뮬레이션 (랜덤, 보수적, 공격적, 추세 추종)
*   인터랙티브 투자 시뮬레이션 모드 (CLI)
*   FastAPI를 이용한 웹 API 제공 (시나리오 생성, 조회, 시뮬레이션 실행)
*   명령줄 인터페이스 (CLI) 제공
*   Matplotlib을 이용한 주가 변동 및 시뮬레이션 결과 시각화 (CLI)
*   Jupyter Notebook (`notebook/langchain.ipynb`)을 통한 개발 및 테스트 환경 제공

## 사용 기술

*   Python 3.x
*   FastAPI: API 개발
*   Uvicorn: ASGI 서버
*   LangChain & LangChain-OpenAI: LLM 연동 및 프롬프트 관리
*   OpenAI API (gpt-4o-mini 또는 유사 모델)
*   Pydantic: 데이터 유효성 검사 및 설정 관리
*   Matplotlib: 데이터 시각화
*   python-dotenv: 환경 변수 관리

## 프로젝트 구조

```
edu_stock_llm/
├── .env                  # 환경 변수 파일 (OpenAI API 키 등) - 직접 생성 필요
├── .gitignore            # Git 무시 파일 목록
├── README.md             # 프로젝트 설명 파일
├── requirements.txt      # 프로젝트 의존성 패키지 목록
├── data/                 # 생성된 게임 시나리오 JSON 파일 저장 (자동 생성)
├── notebook/
│   └── langchain.ipynb   # LLM 테스트 및 개발용 Jupyter Notebook
├── src/                  # 주요 소스 코드
│   ├── __init__.py
│   ├── api.py            # FastAPI 웹 API 정의
│   ├── main.py           # CLI 애플리케이션 실행 로직
│   ├── data/
│   │   └── data_handler.py # 데이터 파싱, 저장, 로드
│   ├── models/
│   │   └── llm_handler.py  # LLM 연동 및 게임 데이터 생성
│   ├── simulation/
│   │   └── simulator.py    # 투자 시뮬레이션 로직
│   ├── utils/
│   │   ├── config.py     # API 키 로드, 모델 설정
│   │   └── prompts.py    # LLM 프롬프트 정의
│   └── visualization/
│       └── visualize.py    # 데이터 시각화
└── visualization_results/  # 시각화 결과 이미지 저장 (자동 생성)
```

## 설치 및 실행 방법

### 1. 프로젝트 클론

```bash
git clone <레포지토리_URL>
cd edu_stock_llm
```

### 2. 가상 환경 생성 및 활성화 (권장)

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate
```

### 3. 의존성 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. `.env` 파일 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, OpenAI API 키를 입력합니다.

```env
// filepath: /edu_stock_llm/.env
OPENAI_API_KEY="sk-your-openai-api-key"
```
**주의**: 실제 API 키를 사용하세요. 위 키는 예시입니다.

### 5. 실행 방법

#### A. 명령줄 인터페이스 (CLI)

프로젝트 루트 디렉토리에서 다음 명령어를 사용하여 CLI 애플리케이션을 실행할 수 있습니다.

*   **도움말 확인**:
    ```bash
    python -m src.main --help
    ```
*   **새 시나리오 생성, 시각화, 자동 시뮬레이션 실행**:
    ```bash
    python -m src.main --visualize --simulate --auto-sim
    ```
    *   데이터는 `data/` 폴더에 `game_scenario_YYYYMMDD_HHMMSS.json` 형식으로 저장됩니다.
    *   시각화 결과는 `visualization_results/` 폴더에 저장될 수 있습니다 (`--save-viz` 옵션 사용 시).
*   **기존 시나리오 파일 사용**:
    ```bash
    python -m src.main --use-existing --input-file data/your_scenario_file.json --visualize --simulate
    ```

#### B. 웹 API (FastAPI)

프로젝트 루트 디렉토리에서 다음 명령어를 사용하여 FastAPI 서버를 실행합니다.

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 주소로 접속하여 API 문서를 확인할 수 있습니다:

*   Swagger UI: `http://localhost:8000/docs`
*   ReDoc: `http://localhost:8000/redoc`

**주요 API 엔드포인트**:

*   `POST /scenario/generate`: 새로운 게임 시나리오를 생성합니다.
*   `GET /scenario/{scenario_id}`: 특정 ID의 게임 시나리오를 조회합니다.
*   `POST /simulation/run_automated`: 주어진 시나리오와 전략으로 자동 투자 시뮬레이션을 실행합니다.
*   `GET /scenarios`: 저장된 모든 시나리오 파일 목록을 조회합니다.

#### C. Jupyter Notebook

LLM 연동, 프롬프트 테스트, 데이터 생성 및 기본 시각화 로직을 실험해볼 수 있습니다.

1.  Jupyter Notebook 또는 JupyterLab을 실행합니다.
    ```bash
    jupyter notebook
    # 또는
    jupyter lab
    ```
2.  `notebook/langchain.ipynb` 파일을 열고 셀을 순차적으로 실행합니다.

## 기여

버그 수정이나 기능 개선에 대한 기여를 환영합니다. 이슈를 생성하거나 풀 리퀘스트를 보내주세요.