#!/bin/bash

# 스토리텔링 투자 시뮬레이션 실행 스크립트

set -e

echo "🎭 투자 시뮬레이션 게임에 오신 것을 환영합니다!"
echo "================================================"

# 가상환경 활성화
if [ ! -d ".venv" ]; then
    echo "❌ 가상환경이 없습니다. 먼저 'uv venv'를 실행하세요."
    exit 1
fi

source .venv/bin/activate

# 시나리오 선택 함수
select_scenario() {
    echo ""
    echo "🎭 게임 시나리오를 선택하세요:"
    echo "1) 🏰 마법 왕국 (magic_kingdom)"
    echo "   - 빵집, 서커스단, 마법연구소"
    echo "   - 마법사가 되어 마법 코인으로 투자하는 이야기"
    echo ""
    echo "2) 🚚 푸드트럭 왕국 (foodtruck_kingdom)"
    echo "   - 샌드위치 트럭, 아이스크림 트럭, 퓨전 타코 트럭"
    echo "   - 요리사가 되어 미식 코인으로 투자하는 이야기"
    echo ""
    echo "3) 🌙 달빛 도둑 (moonlight_thief)"
    echo "   - 달빛 가루 수집, 달조각 목걸이, 달빛 방패"
    echo "   - 달빛 도둑이 되어 달빛 코인으로 투자하는 이야기"
    echo ""
    echo "4) 🐷 아기돼지 삼형제 (three_little_pigs)"
    echo "   - 첫째 돼지(지푸라기집), 둘째 돼지(나무집), 셋째 돼지(벽돌집)"
    echo "   - 투자 고문이 되어 건설 코인으로 투자하는 이야기"
    echo ""
    
    while true; do
        read -p "시나리오를 선택하세요 (1, 2, 3, 또는 4): " scenario_choice
        case $scenario_choice in
            1)
                SCENARIO_TYPE="magic_kingdom"
                DEFAULT_DATA="data/game_scenario_magic_kingdom_20250525_133010.json"
                break
                ;;
            2)
                SCENARIO_TYPE="foodtruck_kingdom"
                DEFAULT_DATA="data/game_scenario_foodtruck_kingdom_20250525_132903.json"
                break
                ;;
            3)
                SCENARIO_TYPE="moonlight_thief"
                DEFAULT_DATA="data/game_scenario_moonlight_thief_sample.json"
                break
                ;;
            4)
                SCENARIO_TYPE="three_little_pigs"
                DEFAULT_DATA="data/game_scenario_three_little_pigs_20250609_162517.json"
                break
                ;;
            *)
                echo "❌ 잘못된 선택입니다. 1, 2, 3, 또는 4를 입력해주세요."
                ;;
        esac
    done
    
    echo "✅ 선택된 시나리오: $SCENARIO_TYPE"
}

echo ""
echo "게임 모드를 선택하세요:"
echo "1) 인터랙티브 게임 (직접 투자 결정)"
echo "2) 자동화된 전략 비교"
echo "3) 시각화만 보기"
echo "4) API 서버 실행"
echo "5) 새로운 시나리오 생성 (OpenAI API 키 필요)"

read -p "선택 (1-5): " choice

case $choice in
    1)
        select_scenario
        if [ ! -f "$DEFAULT_DATA" ]; then
            echo "❌ 데이터 파일이 없습니다: $DEFAULT_DATA"
            echo "새로운 시나리오를 생성하겠습니다..."
            python src/main.py --scenario-type "$SCENARIO_TYPE" --simulate
        else
            echo "🎮 인터랙티브 게임을 시작합니다..."
            python src/main.py --use-existing --input-file "$DEFAULT_DATA" --simulate
        fi
        ;;
    2)
        select_scenario
        if [ ! -f "$DEFAULT_DATA" ]; then
            echo "❌ 데이터 파일이 없습니다: $DEFAULT_DATA"
            echo "새로운 시나리오를 생성하겠습니다..."
            python src/main.py --scenario-type "$SCENARIO_TYPE" --simulate --auto-sim
        else
            echo "🤖 자동화된 전략 비교를 시작합니다..."
            python src/main.py --use-existing --input-file "$DEFAULT_DATA" --simulate --auto-sim
        fi
        ;;
    3)
        select_scenario
        if [ ! -f "$DEFAULT_DATA" ]; then
            echo "❌ 데이터 파일이 없습니다: $DEFAULT_DATA"
            echo "새로운 시나리오를 생성하겠습니다..."
            python src/main.py --scenario-type "$SCENARIO_TYPE" --visualize --save-viz
        else
            echo "📊 시각화를 생성합니다..."
            python src/main.py --use-existing --input-file "$DEFAULT_DATA" --visualize --save-viz
        fi
        ;;
    4)
        echo "🚀 API 서버를 시작합니다..."
        echo "API 문서: http://localhost:8000/docs"
        echo "시나리오 타입 목록: http://localhost:8000/scenario-types"
        python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
        ;;
    5)
        select_scenario
        echo "🎨 새로운 $SCENARIO_TYPE 시나리오를 생성합니다..."
        if [ ! -f ".env" ]; then
            echo "❌ .env 파일이 없습니다. .env.example을 복사하여 .env를 만들고 OpenAI API 키를 설정하세요."
            exit 1
        fi
        python src/main.py --scenario-type "$SCENARIO_TYPE" --visualize --simulate --save-viz
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "🎉 게임이 완료되었습니다! 감사합니다!"
