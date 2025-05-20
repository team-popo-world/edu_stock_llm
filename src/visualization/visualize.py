"""
시각화 모듈: 아기돼지 삼형제 주식회사의 게임 데이터를 시각적으로 표현하는 기능을 제공합니다.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from datetime import datetime

def _prepare_stock_data(game_data):
    """
    게임 데이터에서 주식 가치 정보를 추출하여 시각화에 필요한 데이터를 준비합니다.
    
    Args:
        game_data (list): 시각화할 게임 데이터
        
    Returns:
        tuple: (턴 리스트, 각 주식별 가치 리스트, 데이터프레임)
    """
    if not game_data:
        raise ValueError("유효한 게임 데이터가 없습니다.")
    
    # 데이터 준비
    turns = []
    first_house_values = []
    second_house_values = []
    third_house_values = []
    
    for turn in game_data:
        turns.append(turn.get('turn_number', 0))
        
        # 각 집의 값을 찾아 저장
        stock_found = {'첫째집': False, '둘째집': False, '셋째집': False}
        
        # 'stocks' 키가 있는지 확인
        if 'stocks' not in turn:
            print(f"경고: 턴 {turn.get('turn_number', '알 수 없음')}에 'stocks' 정보가 없습니다.")
            # 데이터가 없는 경우 이전 값 유지 또는 기본값 사용
            first_house_values.append(first_house_values[-1] if first_house_values else 100)
            second_house_values.append(second_house_values[-1] if second_house_values else 100)
            third_house_values.append(third_house_values[-1] if third_house_values else 100)
            continue
        
        for stock in turn['stocks']:
            if 'name' not in stock or 'current_value' not in stock:
                print(f"경고: 턴 {turn.get('turn_number', '알 수 없음')}의 주식 정보가 불완전합니다.")
                continue
                
            if stock['name'] == "첫째집":
                first_house_values.append(stock['current_value'])
                stock_found['첫째집'] = True
            elif stock['name'] == "둘째집":
                second_house_values.append(stock['current_value'])
                stock_found['둘째집'] = True
            elif stock['name'] == "셋째집":
                third_house_values.append(stock['current_value'])
                stock_found['셋째집'] = True
        
        # 누락된 주식이 있는지 확인하고 이전 값 또는 기본값으로 채우기
        if not stock_found['첫째집']:
            first_house_values.append(first_house_values[-1] if first_house_values else 100)
        if not stock_found['둘째집']:
            second_house_values.append(second_house_values[-1] if second_house_values else 100)
        if not stock_found['셋째집']:
            third_house_values.append(third_house_values[-1] if third_house_values else 100)
    
    # 데이터프레임으로 변환
    df = pd.DataFrame({
        'Turn': turns,
        'First House (Straw)': first_house_values,
        'Second House (Wood)': second_house_values,
        'Third House (Brick)': third_house_values
    })
    
    return turns, (first_house_values, second_house_values, third_house_values), df

def _create_stock_plot(turns, house_values, df, game_data):
    """
    주식 가치 변동 시각화를 위한 그래프를 생성합니다.
    
    Args:
        turns (list): 턴 번호 목록
        house_values (tuple): 각 주식별 가치 목록의 튜플
        df (DataFrame): 시각화에 사용할 데이터프레임
        game_data (list): 이벤트 표시를 위한 원본 게임 데이터
        
    Returns:
        matplotlib.figure.Figure: 생성된 그래프 객체
    """
    # 폰트 설정 - 한글 표시 문제 회피
    plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
    
    # 시각화
    fig = plt.figure(figsize=(12, 6))
    plt.plot(df['Turn'], df['First House (Straw)'], 'o-', color='gold', label='First House (Straw)')
    plt.plot(df['Turn'], df['Second House (Wood)'], 'o-', color='brown', label='Second House (Wood)')
    plt.plot(df['Turn'], df['Third House (Brick)'], 'o-', color='firebrick', label='Third House (Brick)')
    
    # 초기 가치 기준선 추가
    plt.axhline(y=100, color='gray', linestyle='--', alpha=0.7, label='Initial Value')
    
    # 그래프 꾸미기
    plt.title('Three Little Pigs Corporation - Stock Value Changes by Turn', fontsize=16)
    plt.xlabel('Turn', fontsize=12)
    plt.ylabel('Stock Value', fontsize=12)
    plt.xticks(turns)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 중요 이벤트 표시
    for turn in game_data:
        if 'event_description' in turn and turn.get('event_description') != "없음":
            plt.annotate(f"Event: Turn {turn.get('turn_number', 0)}", 
                         xy=(turn.get('turn_number', 0), 50),
                         xytext=(turn.get('turn_number', 0), 20),
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                         fontsize=9,
                         horizontalalignment='center')
    
    plt.tight_layout()
    return fig

def visualize_stock_values(game_data):
    """
    게임 데이터에서 턴별 주식 가치 변동을 시각화합니다.
    
    Args:
        game_data (list): 시각화할 게임 데이터
        
    Returns:
        bool: 시각화 성공 여부
    """
    if game_data is None or len(game_data) == 0:
        print("시각화할 데이터가 없습니다.")
        return False
    
    try:
        # 데이터 준비
        turns, house_values, df = _prepare_stock_data(game_data)
        
        # 그래프 생성
        _create_stock_plot(turns, house_values, df, game_data)
        
        # 그래프 표시
        plt.show()
        
        # 턴별 뉴스와 이벤트 정보 출력
        print("\n턴별 뉴스 및 이벤트 정보:")
        for turn in game_data:
            print(f"\n[턴 {turn.get('turn_number', 'N/A')}]")
            
            # 뉴스 정보 출력
            if 'news' in turn:
                print(f"뉴스: {turn['news']}")
            else:
                print("뉴스: 정보 없음")
            
            # 이벤트 정보 출력    
            event_desc = turn.get('event_description', '정보 없음')
            if event_desc != "없음":
                print(f"이벤트: {event_desc}")
            else:
                print("이벤트: 이벤트 없음")
        
        return True
            
    except Exception as e:
        print(f"시각화 중 오류 발생: {e}")
        return False

def save_visualization(game_data, save_path):
    """
    게임 데이터 시각화를 파일로 저장합니다.
    
    Args:
        game_data (list): 시각화할 게임 데이터
        save_path (str): 저장할 파일 경로
        
    Returns:
        bool: 저장 성공 여부
    """
    if game_data is None or len(game_data) == 0:
        print("시각화할 데이터가 없습니다.")
        return False
    
    try:
        # 저장 경로의 디렉토리가 존재하는지 확인
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"디렉토리 생성: {save_dir}")
            
        # 데이터 준비
        turns, house_values, df = _prepare_stock_data(game_data)
        
        # 그래프 생성
        fig = _create_stock_plot(turns, house_values, df, game_data)
        
        # 파일 저장
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"시각화가 {save_path}에 저장되었습니다.")
        return True
        
    except Exception as e:
        print(f"시각화 저장 중 오류 발생: {e}")
        return False

def create_investment_summary(simulation_results, save_path=None):
    """
    시뮬레이션 결과를 시각화하여 투자 성과를 요약합니다.
    
    Args:
        simulation_results (dict): 시뮬레이션 결과 딕셔너리
        save_path (str, optional): 저장할 파일 경로. 없으면, 저장하지 않고 화면에 표시
        
    Returns:
        bool: 시각화 성공 여부
    """
    if not simulation_results or 'investment_history' not in simulation_results:
        print("시각화할 시뮬레이션 결과가 없습니다.")
        return False
    
    try:
        history = simulation_results['investment_history']
        initial_capital = simulation_results.get('initial_capital', 1000)
        final_capital = simulation_results.get('final_capital', 0)
        
        # 데이터 준비
        turns = []
        capitals = []
        investments = []
        
        current_capital = initial_capital
        for turn_data in history:
            turn_num = turn_data.get('turn', 0)
            turns.append(turn_num)
            capitals.append(turn_data.get('capital_after', current_capital))
            current_capital = turn_data.get('capital_after', current_capital)
            investments.append(turn_data.get('investment', '패스'))
        
        # 그래프 생성
        plt.figure(figsize=(12, 8))
        
        # 자본금 변화 그래프
        plt.subplot(2, 1, 1)
        plt.plot(turns, capitals, 'o-', color='blue', linewidth=2)
        plt.axhline(y=initial_capital, color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        plt.title('Capital Changes Throughout the Simulation', fontsize=14)
        plt.xlabel('Turn', fontsize=12)
        plt.ylabel('Capital', fontsize=12)
        plt.xticks(turns)
        plt.grid(True, alpha=0.3)
        
        # 투자 선택 표시
        for i, inv in enumerate(investments):
            if inv != '패스':
                color = 'gold' if inv == '첫째집' else 'brown' if inv == '둘째집' else 'firebrick'
                plt.scatter(turns[i], capitals[i], s=100, color=color, zorder=5, 
                           label=f'{inv}' if inv not in plt.gca().get_legend_handles_labels()[1] else "")
        
        plt.legend()
        
        # 최종 결과 요약
        plt.subplot(2, 1, 2)
        plt.axis('off')
        profit_rate = ((final_capital - initial_capital) / initial_capital) * 100
        
        summary_text = (
            f"Investment Summary\n"
            f"------------------------------------------\n"
            f"Strategy: {simulation_results.get('strategy', 'Interactive')}\n"
            f"Initial Capital: {initial_capital:.1f}\n"
            f"Final Capital: {final_capital:.1f}\n"
            f"Profit/Loss: {final_capital - initial_capital:.1f}\n"
            f"Profit Rate: {profit_rate:.1f}%\n"
            f"\nResult: {simulation_results.get('result_message', '')}"
        )
        
        plt.text(0.1, 0.7, summary_text, fontsize=12, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 투자 분포 표시
        investment_counts = {}
        for inv in investments:
            if inv in investment_counts:
                investment_counts[inv] += 1
            else:
                investment_counts[inv] = 1
        
        labels = list(investment_counts.keys())
        sizes = list(investment_counts.values())
        colors = ['gold', 'brown', 'firebrick', 'lightgray']
        
        # 파이 차트 추가
        if labels:  # 투자 정보가 있는 경우에만 파이 차트 생성
            plt.axes([0.65, 0.2, 0.3, 0.3])  # [left, bottom, width, height]
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('Investment Distribution', fontsize=10)
        
        plt.tight_layout()
        
        # 파일 저장 또는 화면 표시
        if save_path:
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"투자 결과 시각화가 {save_path}에 저장되었습니다.")
        else:
            plt.show()
        
        return True
            
    except Exception as e:
        print(f"투자 결과 시각화 중 오류 발생: {e}")
        return False
