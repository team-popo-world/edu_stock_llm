"""
플레이어 프로필 관리 클래스
아이의 학습 패턴과 투자 성향을 추적하고 분석
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
import json
from datetime import datetime


class LearningStyle(Enum):
    """학습 스타일 유형"""
    VISUAL = "visual"      # 시각적 학습자
    AUDITORY = "auditory"  # 청각적 학습자
    HANDS_ON = "hands_on"  # 체험적 학습자
    ANALYTICAL = "analytical"  # 분석적 학습자
    EXPLORING = "exploring"    # 탐색중


class RiskTolerance(Enum):
    """위험 감수 성향"""
    CONSERVATIVE = "conservative"  # 보수적
    MODERATE = "moderate"          # 보통
    AGGRESSIVE = "aggressive"      # 적극적
    EXPLORING = "exploring"        # 탐색중


@dataclass
class PlayerAction:
    """플레이어의 개별 행동 기록"""
    turn: int
    action_type: str  # "buy", "sell", "hold"
    stock_name: str
    shares: int
    price: float
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PlayerProfile:
    """플레이어 프로필"""
    player_id: str = "default_player"
    learning_style: LearningStyle = LearningStyle.EXPLORING
    risk_tolerance: RiskTolerance = RiskTolerance.EXPLORING
    
    # 게임 진행 기록
    games_played: int = 0
    total_turns_played: int = 0
    actions_history: List[PlayerAction] = field(default_factory=list)
    
    # 학습 패턴 분석
    decision_patterns: Dict[str, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)
    
    # 성과 기록
    best_return: float = 0.0
    average_return: float = 0.0
    consistency_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "player_id": self.player_id,
            "learning_style": self.learning_style.value,
            "risk_tolerance": self.risk_tolerance.value,
            "games_played": self.games_played,
            "total_turns_played": self.total_turns_played,
            "decision_patterns": self.decision_patterns,
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "best_return": self.best_return,
            "average_return": self.average_return,
            "consistency_score": self.consistency_score,
            "actions_history": [
                {
                    "turn": action.turn,
                    "action_type": action.action_type,
                    "stock_name": action.stock_name,
                    "shares": action.shares,
                    "price": action.price,
                    "reasoning": action.reasoning,
                    "timestamp": action.timestamp.isoformat()
                }
                for action in self.actions_history
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerProfile':
        """딕셔너리에서 복원"""
        profile = cls(
            player_id=data.get("player_id", "default_player"),
            learning_style=LearningStyle(data.get("learning_style", "exploring")),
            risk_tolerance=RiskTolerance(data.get("risk_tolerance", "exploring")),
            games_played=data.get("games_played", 0),
            total_turns_played=data.get("total_turns_played", 0),
            decision_patterns=data.get("decision_patterns", {}),
            strengths=data.get("strengths", []),
            areas_for_improvement=data.get("areas_for_improvement", []),
            best_return=data.get("best_return", 0.0),
            average_return=data.get("average_return", 0.0),
            consistency_score=data.get("consistency_score", 0.0)
        )
        
        # 행동 기록 복원
        for action_data in data.get("actions_history", []):
            action = PlayerAction(
                turn=action_data["turn"],
                action_type=action_data["action_type"],
                stock_name=action_data["stock_name"],
                shares=action_data["shares"],
                price=action_data["price"],
                reasoning=action_data.get("reasoning", ""),
                timestamp=datetime.fromisoformat(action_data["timestamp"])
            )
            profile.actions_history.append(action)
        
        return profile
    
    def add_action(self, action: PlayerAction):
        """새로운 행동 기록 추가"""
        self.actions_history.append(action)
        self.total_turns_played += 1
        self._update_patterns()
    
    def _update_patterns(self):
        """행동 패턴 업데이트"""
        if not self.actions_history:
            return
        
        # 행동 유형별 빈도 계산
        action_counts = {}
        for action in self.actions_history:
            action_counts[action.action_type] = action_counts.get(action.action_type, 0) + 1
        
        total_actions = len(self.actions_history)
        for action_type, count in action_counts.items():
            self.decision_patterns[f"{action_type}_frequency"] = count / total_actions
        
        # 위험 성향 분석
        risky_actions = sum(1 for action in self.actions_history 
                           if action.action_type == "buy" and action.shares > 3)
        self.decision_patterns["risk_taking"] = risky_actions / total_actions
        
        # 일관성 점수 계산
        recent_actions = self.actions_history[-10:] if len(self.actions_history) > 10 else self.actions_history
        if len(recent_actions) > 3:
            hold_ratio = sum(1 for action in recent_actions if action.action_type == "hold") / len(recent_actions)
            self.consistency_score = 1.0 - abs(hold_ratio - 0.3)  # 적절한 hold 비율(30%) 기준
    
    def get_learning_insights(self) -> Dict[str, str]:
        """학습 인사이트 생성"""
        insights = {}
        
        if self.decision_patterns.get("risk_taking", 0) > 0.7:
            insights["risk_advice"] = "조금 더 신중하게 투자해보는 것은 어떨까요?"
        elif self.decision_patterns.get("risk_taking", 0) < 0.2:
            insights["risk_advice"] = "가끔은 도전적인 투자도 해보세요!"
        
        if self.decision_patterns.get("hold_frequency", 0) > 0.6:
            insights["activity_advice"] = "더 적극적으로 투자 기회를 찾아보세요!"
        elif self.decision_patterns.get("hold_frequency", 0) < 0.2:
            insights["activity_advice"] = "때로는 기다리는 것도 좋은 전략이에요!"
        
        return insights
