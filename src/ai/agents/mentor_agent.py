"""
개인맞춤형 투자 멘토 AI Agent
플레이어의 투자 패턴을 분석하고 맞춤형 조언을 제공
"""
import streamlit as st
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from src.ai.player_profile import PlayerProfile, PlayerAction, LearningStyle, RiskTolerance
from src.models.llm_handler import initialize_llm, create_prompt_template
from src.utils.config import load_api_key


class InvestmentMentorAgent:
    """개인맞춤형 투자 멘토 AI Agent"""
    
    def __init__(self, player_profile: PlayerProfile):
        self.player_profile = player_profile
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """LLM 초기화"""
        try:
            self.llm = initialize_llm()
        except Exception as e:
            st.error(f"AI 멘토 초기화 실패: {e}")
            self.llm = None
    
    def analyze_current_situation(self, 
                                current_turn_data: Dict[str, Any],
                                player_investments: Dict[str, int],
                                player_balance: float,
                                turn_number: int) -> Dict[str, Any]:
        """현재 상황 분석"""
        
        # 포트폴리오 분석
        portfolio_analysis = self._analyze_portfolio(current_turn_data, player_investments, player_balance)
        
        # 위험도 분석
        risk_analysis = self._analyze_risk_level(current_turn_data, player_investments)
        
        # 다양성 분석
        diversification_analysis = self._analyze_diversification(player_investments)
        
        # 시장 정보 활용도 분석
        market_info_usage = self._analyze_market_info_usage(current_turn_data, turn_number)
        
        return {
            "portfolio": portfolio_analysis,
            "risk": risk_analysis,
            "diversification": diversification_analysis,
            "market_info_usage": market_info_usage,
            "turn_number": turn_number
        }
    
    def _analyze_portfolio(self, current_turn_data: Dict[str, Any], 
                          player_investments: Dict[str, int], 
                          player_balance: float) -> Dict[str, Any]:
        """포트폴리오 분석"""
        total_investment_value = 0
        stock_values = {}
        
        for stock_name, shares in player_investments.items():
            if shares > 0:
                stock_info = next((s for s in current_turn_data['stocks'] if s['name'] == stock_name), None)
                if stock_info:
                    value = shares * stock_info['current_value']
                    total_investment_value += value
                    stock_values[stock_name] = {
                        "shares": shares,
                        "current_price": stock_info['current_value'],
                        "total_value": value,
                        "percentage": 0  # 나중에 계산
                    }
        
        # 각 주식의 포트폴리오 비중 계산
        if total_investment_value > 0:
            for stock_name in stock_values:
                stock_values[stock_name]["percentage"] = (
                    stock_values[stock_name]["total_value"] / total_investment_value * 100
                )
        
        total_assets = total_investment_value + player_balance
        investment_ratio = (total_investment_value / total_assets * 100) if total_assets > 0 else 0
        
        return {
            "total_assets": total_assets,
            "investment_value": total_investment_value,
            "cash_balance": player_balance,
            "investment_ratio": investment_ratio,
            "stock_values": stock_values
        }
    
    def _analyze_risk_level(self, current_turn_data: Dict[str, Any], 
                           player_investments: Dict[str, int]) -> Dict[str, Any]:
        """위험도 분석"""
        if not player_investments:
            return {"level": "무투자", "score": 0, "description": "아직 투자를 시작하지 않았어요"}
        
        total_shares = sum(shares for shares in player_investments.values() if shares > 0)
        if total_shares == 0:
            return {"level": "무투자", "score": 0, "description": "현재 보유 주식이 없어요"}
        
        # 단일 주식 집중도 계산
        max_concentration = max(shares for shares in player_investments.values() if shares > 0) / total_shares
        
        # 위험도 점수 계산 (0-100)
        risk_score = 0
        risk_factors = []
        
        if max_concentration > 0.8:
            risk_score += 40
            risk_factors.append("한 주식에 너무 집중되어 있어요")
        elif max_concentration > 0.6:
            risk_score += 20
            risk_factors.append("특정 주식 비중이 높아요")
        
        if total_shares > 10:
            risk_score += 30
            risk_factors.append("많은 주식을 보유하고 있어요")
        elif total_shares > 7:
            risk_score += 15
        
        # 주식 수에 따른 다양성 보너스
        unique_stocks = len([shares for shares in player_investments.values() if shares > 0])
        if unique_stocks >= 3:
            risk_score -= 10
            risk_factors.append("좋은 분산투자를 하고 있어요")
        
        risk_score = max(0, min(100, risk_score))
        
        if risk_score > 70:
            level = "고위험"
        elif risk_score > 40:
            level = "중위험"
        elif risk_score > 20:
            level = "저위험"
        else:
            level = "안전"
        
        return {
            "level": level,
            "score": risk_score,
            "max_concentration": max_concentration * 100,
            "factors": risk_factors
        }
    
    def _analyze_diversification(self, player_investments: Dict[str, int]) -> Dict[str, Any]:
        """다양성 분석"""
        active_investments = {k: v for k, v in player_investments.items() if v > 0}
        
        if len(active_investments) == 0:
            return {"score": 0, "level": "없음", "advice": "다양한 주식에 투자해보세요!"}
        elif len(active_investments) == 1:
            return {"score": 25, "level": "낮음", "advice": "다른 주식도 함께 투자해보세요!"}
        elif len(active_investments) == 2:
            return {"score": 60, "level": "보통", "advice": "한 종목 더 추가하면 더 안전해져요!"}
        elif len(active_investments) >= 3:
            return {"score": 90, "level": "우수", "advice": "훌륭한 분산투자에요!"}
        
        return {"score": 0, "level": "분석불가", "advice": ""}
    
    def _analyze_market_info_usage(self, current_turn_data: Dict[str, Any], turn_number: int) -> Dict[str, Any]:
        """시장 정보 활용도 분석"""
        news_count = len(current_turn_data.get('news', []))
        
        # 간단한 휴리스틱: 뉴스가 많을수록 정보가 풍부
        if news_count >= 3:
            info_richness = "풍부"
            advice = "뉴스를 잘 활용해서 투자 결정을 해보세요!"
        elif news_count >= 2:
            info_richness = "보통"
            advice = "제공된 정보를 꼼꼼히 읽어보세요!"
        else:
            info_richness = "부족"
            advice = "더 많은 정보를 수집해보세요!"
        
        return {
            "news_count": news_count,
            "info_richness": info_richness,
            "advice": advice
        }
    
    def update_player_action(self, action_type: str, stock_name: str, shares: int, price: float, turn_number: int):
        """플레이어 행동 업데이트"""
        from src.ai.player_profile import PlayerAction
        from datetime import datetime
        
        action = PlayerAction(
            turn=turn_number,
            action_type=action_type,
            stock_name=stock_name,
            shares=shares,
            price=price,
            timestamp=datetime.now()
        )
        
        self.player_profile.add_action(action)
        
        # 학습 스타일과 위험 성향 업데이트
        self._update_learning_insights()
    
    def _update_learning_insights(self):
        """학습 인사이트 업데이트"""
        if not self.player_profile.actions_history:
            return
        
        # 최근 행동 패턴 분석
        recent_actions = self.player_profile.actions_history[-5:]  # 최근 5개 행동
        
        # 위험 성향 업데이트
        risk_actions = sum(1 for action in recent_actions if action.action_type == "buy" and action.shares > 3)
        if risk_actions >= 3:
            self.player_profile.risk_tolerance = RiskTolerance.AGGRESSIVE
        elif risk_actions >= 1:
            self.player_profile.risk_tolerance = RiskTolerance.MODERATE
        else:
            self.player_profile.risk_tolerance = RiskTolerance.CONSERVATIVE
        
        # 강점과 개선점 업데이트
        self._update_strengths_and_improvements()
    
    def _update_strengths_and_improvements(self):
        """강점과 개선점 업데이트"""
        patterns = self.player_profile.decision_patterns
        strengths = []
        improvements = []
        
        # 다양성 평가
        buy_frequency = patterns.get("buy_frequency", 0)
        hold_frequency = patterns.get("hold_frequency", 0)
        risk_taking = patterns.get("risk_taking", 0)
        
        if 0.2 <= buy_frequency <= 0.7:
            strengths.append("적절한 투자 활동성")
        elif buy_frequency > 0.7:
            improvements.append("너무 자주 투자하고 있어요. 신중하게 생각해봐요")
        elif buy_frequency < 0.2:
            improvements.append("더 적극적으로 투자 기회를 찾아보세요")
        
        if 0.2 <= hold_frequency <= 0.4:
            strengths.append("적절한 보유 전략")
        elif hold_frequency > 0.6:
            improvements.append("가끔은 적극적인 투자도 해보세요")
        
        if 0.3 <= risk_taking <= 0.6:
            strengths.append("균형 잡힌 위험 관리")
        elif risk_taking > 0.6:
            improvements.append("위험한 투자보다는 안전한 투자도 고려해보세요")
        elif risk_taking < 0.3:
            improvements.append("때로는 도전적인 투자도 좋은 학습이 될 수 있어요")
        
        self.player_profile.strengths = strengths
        self.player_profile.areas_for_improvement = improvements

    def generate_personalized_advice(self, 
                                   situation_analysis: Dict[str, Any],
                                   current_turn_data: Dict[str, Any]) -> Dict[str, Any]:
        """개인맞춤형 조언 생성"""
        
        if not self.llm:
            return self._generate_rule_based_advice(situation_analysis)
        
        try:
            return self._generate_ai_advice(situation_analysis, current_turn_data)
        except Exception as e:
            st.warning(f"AI 조언 생성 실패, 기본 조언을 제공합니다: {e}")
            return self._generate_rule_based_advice(situation_analysis)
    
    def _generate_rule_based_advice(self, situation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """규칙 기반 조언 생성"""
        advice_parts = []
        tips = []
        
        # 포트폴리오 조언
        portfolio = situation_analysis["portfolio"]
        if portfolio["investment_ratio"] < 30:
            advice_parts.append("💰 현금이 많아요! 좋은 기회를 찾아 투자해보세요.")
            tips.append("전체 돈의 50-70% 정도 투자하는 것이 좋아요")
        elif portfolio["investment_ratio"] > 90:
            advice_parts.append("⚠️ 거의 모든 돈을 투자했어요. 조금은 현금으로 남겨두는 게 좋아요.")
            tips.append("예상치 못한 기회를 위해 현금을 20-30% 남겨두세요")
        
        # 위험도 조언
        risk = situation_analysis["risk"]
        if risk["level"] == "고위험":
            advice_parts.append("🚨 위험도가 높아요! 투자를 좀 더 안전하게 분산해보세요.")
            tips.append("한 종목에만 너무 많이 투자하지 마세요")
        elif risk["level"] == "안전":
            advice_parts.append("✅ 안전한 투자를 하고 있어요! 가끔은 조금 더 도전해봐도 좋을 것 같아요.")
            tips.append("가끔은 새로운 주식에 소량 투자해보세요")
        
        # 다양성 조언
        diversification = situation_analysis["diversification"]
        if diversification['score'] < 50:
            tips.append("여러 종류의 주식에 나누어 투자해보세요")
        
        # 개인 성향에 따른 조언
        learning_insights = self.player_profile.get_learning_insights()
        if learning_insights:
            for key, insight in learning_insights.items():
                tips.append(insight)
        
        if not advice_parts:
            advice_parts.append("🎯 현재 잘 하고 있어요! 계속 신중하게 투자해보세요.")
        
        main_message = " ".join(advice_parts)
        
        return {
            "main_message": main_message,
            "tips": tips,
            "diversification_score": diversification['score'],
            "risk_level": risk.get("level", "보통")
        }
    
    def _generate_ai_advice(self, situation_analysis: Dict[str, Any], 
                           current_turn_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI 기반 조언 생성"""
        
        # 프롬프트 템플릿 생성
        system_prompt = f"""
당신은 어린이를 위한 친근하고 교육적인 투자 멘토 AI입니다.

플레이어 프로필:
- 학습 스타일: {self.player_profile.learning_style.value}
- 위험 성향: {self.player_profile.risk_tolerance.value}
- 게임 경험: {self.player_profile.games_played}회
- 플레이어의 강점: {', '.join(self.player_profile.strengths) if self.player_profile.strengths else '아직 파악 중'}
- 개선할 점: {', '.join(self.player_profile.areas_for_improvement) if self.player_profile.areas_for_improvement else '아직 파악 중'}

지침:
1. 어린이 친화적인 언어 사용 (이모지 활용)
2. 교육적이면서도 격려하는 톤
3. 구체적이고 실행 가능한 조언
4. 투자의 기본 원칙을 자연스럽게 설명
5. 2-3문장으로 간결한 메인 메시지와 3-4개의 구체적인 팁 제공

응답은 다음 형식으로만 답변하세요:
MAIN: [메인 조언 메시지]
TIP1: [첫 번째 팁]
TIP2: [두 번째 팁]
TIP3: [세 번째 팁]
"""

        user_prompt = f"""
현재 상황 분석:
포트폴리오: 투자비율 {situation_analysis['portfolio'].get('investment_ratio', 0):.1f}%
위험도: {situation_analysis['risk'].get('level', '보통')}
분산투자 점수: {situation_analysis['diversification'].get('score', 0)}/100

현재 턴 정보:
- 턴 번호: {current_turn_data.get('turn', 'N/A')}
- 이벤트: {current_turn_data.get('event', 'N/A')}
- 뉴스 개수: {len(current_turn_data.get('news', []))}개

이 정보를 바탕으로 플레이어에게 개인맞춤형 투자 조언을 해주세요.
"""

        try:
            prompt_template = create_prompt_template(system_prompt)
            chain = prompt_template | self.llm
            response = chain.invoke({"question": user_prompt})
            content = response.content.strip()
            
            # 응답 파싱
            lines = content.split('\n')
            main_message = "계속해서 좋은 투자를 해보세요!"
            tips = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('MAIN:'):
                    main_message = line[5:].strip()
                elif line.startswith('TIP'):
                    tip_content = line.split(':', 1)[1].strip() if ':' in line else line
                    if tip_content:
                        tips.append(tip_content)
            
            return {
                "main_message": main_message,
                "tips": tips,
                "diversification_score": situation_analysis['diversification'].get('score', 0),
                "risk_level": situation_analysis['risk'].get("level", "보통")
            }
            
        except Exception as e:
            raise e
    
    def save_profile(self, filepath: str = None):
        """플레이어 프로필 저장"""
        if filepath is None:
            filepath = f"data/player_profile_{self.player_profile.player_id}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.player_profile.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"프로필 저장 실패: {e}")
    
    @classmethod
    def load_profile(cls, filepath: str = None, player_id: str = "default_player"):
        """플레이어 프로필 로드"""
        if filepath is None:
            filepath = f"data/player_profile_{player_id}.json"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profile = PlayerProfile.from_dict(data)
                return cls(profile)
        except FileNotFoundError:
            # 새 프로필 생성
            profile = PlayerProfile(player_id=player_id)
            return cls(profile)
        except Exception as e:
            st.error(f"프로필 로드 실패: {e}")
            profile = PlayerProfile(player_id=player_id)
            return cls(profile)
