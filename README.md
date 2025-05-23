# 🎭 마법 왕국 투자 게임 (10세 이하 아동용)

10세 이하 아동을 위한 마법 왕국 테마의 투자 교육 게임입니다. LLM을 활용하여 아이들이 이해하기 쉬운 동화적 상황을 만들고, 재미있는 이야기를 통해 돈과 투자의 기본 개념을 배울 수 있는 교육용 프로젝트입니다.

## 🌟 게임 소개

마법 왕국의 작은 마을에는 세 개의 특별한 상점이 있어요:
- 🍞 **빵집**: 마을 사람들이 매일 필요로 하는 빵을 만드는 곳 (저위험 - 안전한 투자)
- 🎪 **서커스단**: 가끔 마을에 와서 공연하는 유명한 서커스단 (중위험 - 적당한 투자)  
- 🔮 **마법연구소**: 새로운 마법을 개발하는 신비한 연구소 (고위험 - 모험 투자)

어린 투자 마법사가 되어 10일 동안 이 상점들에 마법 코인을 투자하며, 재미있는 이야기와 함께 투자의 기본 원리를 배워보세요!

## ✨ 주요 기능

### 🎮 게임 기능
*   **동화적 스토리텔링**: 아이들이 친숙한 마법 왕국 배경의 재미있는 이야기
*   **단순화된 투자 개념**: 복잡한 금융 용어 대신 이해하기 쉬운 표현 사용
*   **3개 상점 투자**: 빵집, 서커스단, 마법연구소에만 투자하는 단순한 구조
*   **10일 게임 진행**: 짧은 기간으로 집중력 유지 및 완주 가능
*   **위험과 수익 학습**: 안전한 투자부터 모험 투자까지 단계별 경험

### 🛠 기술적 기능
*   **LLM 기반 시나리오 생성**: OpenAI GPT를 활용한 동적 게임 스토리 생성
*   **자동 투자 시뮬레이션**: 다양한 투자 전략 시뮬레이션
*   **인터랙티브 CLI**: 명령줄을 통한 게임 진행
*   **웹 API 제공**: FastAPI를 통한 RESTful API
*   **시각화**: 투자 결과를 그래프로 확인
*   **개발 환경**: Jupyter Notebook을 통한 테스트 및 개발

## 🎯 교육적 목표

### 투자 기본 개념 학습
- **위험과 수익의 관계**: 안전한 투자 vs 모험적 투자
- **분산 투자**: 여러 상점에 나누어 투자하는 중요성
- **시장 변화 이해**: 뉴스와 상황에 따른 가격 변동
- **장기적 사고**: 단기 변동에 흔들리지 않는 투자 철학

### 아동 발달 지원
- **의사결정 능력**: 정보를 바탕으로 한 선택의 중요성
- **수학적 사고**: 숫자와 변화에 대한 기본 이해
- **경제 개념**: 돈의 가치와 투자의 의미
- **스토리텔링**: 재미있는 이야기를 통한 자연스러운 학습

## 🛠 사용 기술

*   **Python 3.x**: 프로젝트 기반 언어
*   **FastAPI**: 웹 API 개발 프레임워크
*   **Uvicorn**: ASGI 웹 서버
*   **LangChain & LangChain-OpenAI**: LLM 연동 및 프롬프트 관리
*   **OpenAI API**: GPT 모델을 활용한 스토리 생성
*   **Pydantic**: 데이터 유효성 검사 및 설정 관리
*   **Matplotlib**: 투자 결과 시각화
*   **python-dotenv**: 환경 변수 관리

## 📁 프로젝트 구조

```
edu_stock_llm/
├── .env                  # 환경 변수 파일 (OpenAI API 키) - 직접 생성 필요
├── .gitignore            # Git 무시 파일 목록
├── README.md             # 프로젝트 설명 파일 (이 파일)
├── requirements.txt      # 프로젝트 의존성 패키지 목록
├── data/                 # 🎮 생성된 마법 왕국 게임 시나리오 JSON 파일들
│   ├── game_scenario_20250523_110347.json  # 게임 데이터 예시
│   └── ...               # 기타 게임 시나리오 파일들
├── notebook/
│   └── langchain.ipynb   # 📓 LLM 테스트 및 개발용 노트북
├── src/                  # 🎯 주요 소스 코드
│   ├── __init__.py
│   ├── api.py            # 🌐 FastAPI 웹 API 정의
│   ├── main.py           # 🎮 CLI 게임 실행 로직
│   ├── data/
│   │   └── data_handler.py # 📊 게임 데이터 처리
│   ├── models/
│   │   └── llm_handler.py  # 🤖 LLM 연동 및 스토리 생성
│   ├── simulation/
│   │   └── simulator.py    # 🎲 투자 시뮬레이션 로직
│   ├── utils/
│   │   ├── config.py     # ⚙️ 설정 및 API 키 관리
│   │   └── prompts.py    # 📝 마법 왕국 스토리 프롬프트
│   └── visualization/
│       └── visualize.py    # 📈 투자 결과 시각화
└── visualization_results/  # 📊 시각화 결과 이미지 저장 (자동 생성)
```

## 🎲 게임 데이터 구조

각 턴별로 다음과 같은 정보가 생성됩니다:

```json
{
  "turn_number": 1,
  "result": "화창한 날씨 덕분에 서커스단이 인기를 끌었어요!",
  "news": "마법 왕국에 맑은 날씨가 계속되고 있어서 서커스 공연을 보러 오는 사람들이 많아졌어요!",
  "news_hint": "맑은 날에는 서커스 관객이 많아져요!",
  "stocks": [
    {
      "name": "빵집",
      "description": "마을 사람들이 매일 필요로 하는 빵을 만드는 곳",
      "initial_value": 100,
      "current_value": 102,
      "risk_level": "저위험 - 안전한 투자"
    },
    {
      "name": "서커스단",
      "description": "가끔 마을에 와서 공연하는 유명한 서커스단",
      "initial_value": 100,
      "current_value": 108,
      "risk_level": "중위험 - 적당한 투자"
    },
    {
      "name": "마법연구소",
      "description": "새로운 마법을 개발하는 신비한 연구소",
      "initial_value": 100,
      "current_value": 95,
      "risk_level": "고위험 - 모험 투자"
    }
  ]
}
```

## 🚀 설치 및 실행 방법

### 1. 📥 프로젝트 클론

```bash
git clone <레포지토리_URL>
cd edu_stock_llm
```

### 2. 🐍 가상 환경 생성 및 활성화 (권장)

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. 📦 의존성 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 🔑 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, OpenAI API 키를 입력합니다.

```env
OPENAI_API_KEY="sk-your-actual-openai-api-key-here"
```

> ⚠️ **주의**: 실제 OpenAI API 키를 사용하세요. 위 키는 예시입니다.

### 5. 🎮 게임 실행 방법

#### A. 🖥 명령줄 인터페이스 (CLI) - 추천!

프로젝트 루트 디렉토리에서 다음 명령어로 마법 왕국 투자 게임을 실행할 수 있습니다.

*   **🆘 도움말 확인**:
    ```bash
    python -m src.main --help
    ```

*   **🎯 새 마법 왕국 이야기 생성 + 시각화 + 자동 투자**:
    ```bash
    python -m src.main --visualize --simulate --auto-sim
    ```
    - 🎭 새로운 마법 왕국 스토리가 생성됩니다
    - 📊 투자 결과를 그래프로 볼 수 있습니다  
    - 🤖 자동으로 투자 시뮬레이션이 실행됩니다
    - 📁 데이터는 `data/` 폴더에 `game_scenario_YYYYMMDD_HHMMSS.json` 형식으로 저장

*   **📂 기존 게임 데이터 사용하기**:
    ```bash
    python -m src.main --use-existing --input-file data/game_scenario_20250523_110347.json --visualize --simulate
    ```

*   **💾 시각화 결과 저장하기**:
    ```bash
    python -m src.main --visualize --save-viz
    ```

#### B. 🌐 웹 API (FastAPI)

개발자나 다른 애플리케이션에서 사용할 수 있는 웹 API를 제공합니다.

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

서버 실행 후 브라우저에서 접속:
*   📚 **API 문서 (Swagger)**: `http://localhost:8000/docs`
*   📖 **API 문서 (ReDoc)**: `http://localhost:8000/redoc`

**🔗 주요 API 엔드포인트**:
*   `POST /scenario/generate`: 새로운 마법 왕국 게임 시나리오 생성
*   `GET /scenario/{scenario_id}`: 특정 게임 시나리오 조회
*   `POST /simulation/run_automated`: 자동 투자 시뮬레이션 실행
*   `GET /scenarios`: 저장된 모든 게임 시나리오 목록 조회

#### C. 📓 Jupyter Notebook (개발자용)

LLM 연동 테스트, 프롬프트 실험, 데이터 분석 등 개발 작업용입니다.

```bash
jupyter notebook
# 또는
jupyter lab
```

`notebook/langchain.ipynb` 파일을 열고 셀을 순차적으로 실행하세요.

## 🎯 게임 진행 예시

### 1턴 예시:
```
📰 뉴스: "마법 왕국에 맑은 날씨가 계속되고 있어요!"
💡 힌트: "맑은 날에는 서커스 관객이 많아져요!"

💰 투자 결과:
🍞 빵집: 100 → 102 (안정적!)
🎪 서커스단: 100 → 108 (날씨 덕분에 인기!)  
🔮 마법연구소: 100 → 95 (실험 실패...)
```

### 게임 특징:
- 📚 **교육적**: 아이들이 투자 원리를 자연스럽게 학습
- 🎨 **재미있음**: 마법 왕국의 흥미진진한 이야기
- 🎯 **단순함**: 복잡하지 않은 3개 상점만 투자 대상
- ⏰ **적절한 길이**: 10턴으로 지루하지 않게 구성

## 기여

버그 수정이나 기능 개선에 대한 기여를 환영합니다. 이슈를 생성하거나 풀 리퀘스트를 보내주세요.