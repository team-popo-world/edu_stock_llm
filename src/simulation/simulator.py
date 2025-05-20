"""
게임 시뮬레이션 모듈
"""
import random

def run_simulation(game_data):
    """
    게임 데이터를 기반으로 간단한 투자 시뮬레이션을 실행합니다.
    
    Args:
        game_data (list): 시뮬레이션에 사용할 게임 데이터
        
    Returns:
        dict: 시뮬레이션 결과 (시작 자본금, 최종 자본금, 수익률 등)
    """
    if game_data is None:
        print("시뮬레이션을 실행할 데이터가 없습니다.")
        return None
    
    try:
        print("\n===== 아기돼지 삼형제 주식회사 투자 시뮬레이션 =====\n")
        print("각 턴마다 세 종목('첫째집', '둘째집', '셋째집') 중 하나에 투자할 수 있습니다.")
        print("시작 자본금은 1000원이며, 턴이 끝날 때마다 투자한 종목의 수익률에 따라 자본금이 변동됩니다.\n")
        
        initial_capital = 1000  # 초기 자본금
        capital = initial_capital
        investment_history = []
        
        for turn in game_data:
            print(f"\n===== 턴 {turn['turn_number']} =====")
            print(f"현재 자본금: {capital}원")
            
            # 뉴스 출력 (있는 경우에만)
            if 'news' in turn:
                print(f"\n뉴스: {turn['news']}")
            
            # 종목 정보 출력
            print("\n현재 종목 정보:")
            for stock in turn['stocks']:
                print(f"- {stock['name']}: {stock['current_value']} (위험도: {stock['risk_level']})")
            
            # 사용자 입력 받기
            valid_stocks = [stock['name'] for stock in turn['stocks']]
            while True:
                choice = input(f"\n어떤 종목에 투자하시겠습니까? ({', '.join(valid_stocks)}, 또는 '패스'): ")
                if choice in valid_stocks or choice == '패스':
                    break
                print("잘못된 입력입니다. 다시 시도해주세요.")
            
            # 투자 결과 계산
            turn_result = {
                "turn": turn['turn_number'],
                "investment": choice,
                "capital_before": capital
            }
            
            # 기록할 수 있는 필드 추가
            if 'news' in turn:
                turn_result["news"] = turn['news']
            if 'event_description' in turn:
                turn_result["event"] = turn['event_description']
            
            if choice == '패스':
                print("이번 턴은 투자를 패스합니다.")
                turn_result["profit"] = 0
                turn_result["capital_after"] = capital
            else:
                # 다음 턴의 해당 종목 가치 찾기 (마지막 턴이면 현재 턴 사용)
                next_turn_index = turn['turn_number'] if turn['turn_number'] == len(game_data) else turn['turn_number']
                current_value = next(stock['current_value'] for stock in turn['stocks'] if stock['name'] == choice)
                
                # 다음 턴의 가치 찾기
                if next_turn_index < len(game_data):
                    next_turn = game_data[next_turn_index]
                    next_value = next(stock['current_value'] for stock in next_turn['stocks'] if stock['name'] == choice)
                else:
                    # 마지막 턴이면 현재 가치의 ±10% 랜덤 변동
                    next_value = current_value * (1 + random.uniform(-0.1, 0.1))
                
                # 수익률 계산
                profit_rate = (next_value - current_value) / current_value
                profit = capital * profit_rate
                capital = capital + profit
                
                turn_result["profit"] = profit
                turn_result["profit_rate"] = profit_rate
                turn_result["capital_after"] = capital
                
                print(f"\n투자 결과: {choice}에 투자하여 {profit:.1f}원의 {'수익' if profit >= 0 else '손실'}이 발생했습니다.")
                print(f"새로운 자본금: {capital:.1f}원")
            
            investment_history.append(turn_result)
            
            # 이벤트 표시
            if 'event_description' in turn and turn['event_description'] != "없음":
                print(f"\n[이벤트 발생] {turn['event_description']}")
            
            # 다음 턴으로 넘어가기 전에 대기
            if turn['turn_number'] < len(game_data):
                input("\n엔터 키를 눌러 다음 턴으로 진행하세요...")
        
        # 시뮬레이션 종료
        print("\n===== 시뮬레이션 종료 =====")
        print(f"최종 자본금: {capital:.1f}원")
        profit_rate = (capital - initial_capital) / initial_capital * 100
        print(f"최종 수익률: {profit_rate:.1f}%")
        
        result_message = ""
        if profit_rate > 50:
            result_message = "대단합니다! 투자의 귀재군요! 😃"
            print(result_message)
        elif profit_rate > 0:
            result_message = "성공적인 투자였습니다! 👍"
            print(result_message)
        elif profit_rate > -20:
            result_message = "아쉽게도 약간의 손실이 발생했습니다. 다음에 더 좋은 결과가 있을 거예요. 🙂"
            print(result_message)
        else:
            result_message = "큰 손실이 발생했네요. 다음에는 더 신중하게 투자해보세요. 😢"
            print(result_message)
        
        # 결과 반환
        return {
            "initial_capital": initial_capital,
            "final_capital": capital,
            "profit_rate": profit_rate,
            "result_message": result_message,
            "investment_history": investment_history
        }
        
    except Exception as e:
        print(f"시뮬레이션 중 오류 발생: {e}")
        return None

def run_automated_simulation(game_data, strategy="random"):
    """
    자동화된 시뮬레이션을 실행합니다.
    
    Args:
        game_data (list): 시뮬레이션에 사용할 게임 데이터
        strategy (str, optional): 투자 전략. 기본값은 "random"
            - "random": 랜덤 투자
            - "conservative": 보수적 투자 (위험도가 낮은 종목 선호)
            - "aggressive": 공격적 투자 (위험도가 높은 종목 선호)
            - "trend": 추세 투자 (상승 중인 종목 선호)
        
    Returns:
        dict: 시뮬레이션 결과 (시작 자본금, 최종 자본금, 수익률 등)
    """
    if game_data is None:
        print("시뮬레이션을 실행할 데이터가 없습니다.")
        return None
    
    try:
        print(f"\n===== 자동화된 투자 시뮬레이션 (전략: {strategy}) =====\n")
        
        initial_capital = 1000  # 초기 자본금
        capital = initial_capital
        investment_history = []
        
        for turn_idx, turn in enumerate(game_data):
            # 투자할 종목 선택 (전략에 따라)
            stocks = turn['stocks']
            
            if strategy == "random":
                # 랜덤 투자 (패스 포함)
                choices = [stock['name'] for stock in stocks] + ['패스']
                choice = random.choice(choices)
            
            elif strategy == "conservative":
                # 보수적 투자 (안정적인 셋째집 선호)
                weights = {"첫째집": 0.1, "둘째집": 0.3, "셋째집": 0.5, "패스": 0.1}
                choices = list(weights.keys())
                weights_values = list(weights.values())
                choice = random.choices(choices, weights=weights_values, k=1)[0]
            
            elif strategy == "aggressive":
                # 공격적 투자 (고위험 고수익 첫째집 선호)
                weights = {"첫째집": 0.6, "둘째집": 0.2, "셋째집": 0.1, "패스": 0.1}
                choices = list(weights.keys())
                weights_values = list(weights.values())
                choice = random.choices(choices, weights=weights_values, k=1)[0]
            
            elif strategy == "trend":
                # 추세 투자 (이전 턴 대비 가치 상승 종목 선호)
                if turn_idx > 0:
                    prev_turn = game_data[turn_idx - 1]
                    trend_weights = {}
                    
                    for stock in stocks:
                        name = stock['name']
                        current_value = stock['current_value']
                        
                        # 이전 턴의 같은 이름 종목 찾기
                        prev_value = next((s['current_value'] for s in prev_turn['stocks'] if s['name'] == name), current_value)
                        
                        # 상승률
                        growth_rate = (current_value - prev_value) / prev_value if prev_value > 0 else 0
                        
                        # 상승 중인 종목에 가중치 부여
                        if growth_rate > 0.1:  # 10% 이상 상승
                            trend_weights[name] = 0.7
                        elif growth_rate > 0:  # 상승
                            trend_weights[name] = 0.5
                        elif growth_rate > -0.1:  # 소폭 하락
                            trend_weights[name] = 0.2
                        else:  # 큰 하락
                            trend_weights[name] = 0.05
                    
                    trend_weights["패스"] = 0.1
                    
                    choices = list(trend_weights.keys())
                    weights_values = list(trend_weights.values())
                    choice = random.choices(choices, weights=weights_values, k=1)[0]
                else:
                    # 첫 턴에는 랜덤 선택
                    choices = [stock['name'] for stock in stocks] + ['패스']
                    choice = random.choice(choices)
            
            else:
                # 알 수 없는 전략은 랜덤 사용
                choices = [stock['name'] for stock in stocks] + ['패스']
                choice = random.choice(choices)
            
            # 투자 결과 기록
            turn_result = {
                "turn": turn['turn_number'],
                "investment": choice,
                "capital_before": capital
            }
            
            # 기록할 수 있는 필드 추가
            if 'news' in turn:
                turn_result["news"] = turn['news']
            if 'event_description' in turn:
                turn_result["event"] = turn['event_description']
            
            # 투자 결과 계산
            if choice == '패스':
                turn_result["profit"] = 0
                turn_result["capital_after"] = capital
            else:
                # 현재 턴의 종목 가치
                current_value = next((stock['current_value'] for stock in stocks if stock['name'] == choice), 0)
                
                # 다음 턴의 가치 찾기
                if turn_idx < len(game_data) - 1:  # 마지막 턴이 아닌지 확인
                    next_turn = game_data[turn_idx + 1]  # 다음 턴 데이터 가져오기
                    try:
                        next_value = next((stock['current_value'] for stock in next_turn['stocks'] if stock['name'] == choice), current_value)
                    except (KeyError, StopIteration):
                        # 다음 턴에 해당 종목이 없거나 stocks 키가 없는 경우
                        next_value = current_value * (1 + random.uniform(-0.1, 0.1))
                else:
                    # 마지막 턴이면 현재 가치의 ±10% 랜덤 변동
                    next_value = current_value * (1 + random.uniform(-0.1, 0.1))
                
                # 수익률 계산
                profit_rate = (next_value - current_value) / current_value if current_value > 0 else 0
                profit = capital * profit_rate
                capital = capital + profit
                
                turn_result["profit"] = profit
                turn_result["profit_rate"] = profit_rate
                turn_result["capital_after"] = capital
            
            investment_history.append(turn_result)
            
            # 간략한 결과 출력
            print(f"턴 {turn['turn_number']}: {choice}에 투자, 자본금 {capital:.1f}원")
        
        # 최종 결과
        profit_rate = (capital - initial_capital) / initial_capital * 100
        print(f"\n===== 시뮬레이션 결과 ({strategy} 전략) =====")
        print(f"최종 자본금: {capital:.1f}원")
        print(f"최종 수익률: {profit_rate:.1f}%")
        
        # 결과 메시지
        result_message = ""
        if profit_rate > 50:
            result_message = "대단한 투자 결과! 투자의 귀재!"
            print(result_message)
        elif profit_rate > 0:
            result_message = "성공적인 투자 결과!"
            print(result_message)
        elif profit_rate > -20:
            result_message = "약간의 손실이 발생했습니다."
            print(result_message)
        else:
            result_message = "큰 손실이 발생했습니다."
            print(result_message)
        
        # 결과 반환
        return {
            "strategy": strategy,
            "initial_capital": initial_capital,
            "final_capital": capital,
            "profit_rate": profit_rate,
            "result_message": result_message,
            "investment_history": investment_history
        }
        
    except Exception as e:
        print(f"자동화 시뮬레이션 중 오류 발생: {e}")
        return None
