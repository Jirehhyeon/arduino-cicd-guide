#!/usr/bin/env python3
"""
Arduino IoT DevOps AI 기반 개인화 학습 시스템

이 시스템은 OpenAI GPT-4와 머신러닝 알고리즘을 활용하여
학습자의 개별 특성에 맞는 맞춤형 학습 경험을 제공합니다.

Features:
- 학습 스타일 자동 분석
- 실시간 적응형 콘텐츠 생성
- 개인화된 학습 경로 추천
- 지능형 피드백 및 멘토링
- 예측 기반 학습 성과 분석

Author: Arduino DevOps AI Team
Version: 3.0.0
License: MIT
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import openai
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import sqlite3
import aiohttp
from bs4 import BeautifulSoup
import requests
from textblob import TextBlob
import spacy
from wordcloud import WordCloud
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from streamlit_chat import message
import streamlit_authenticator as stauth

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class LearningPreference:
    """학습 선호도 데이터 클래스"""
    visual_learner: float  # 시각적 학습 선호도 (0-1)
    auditory_learner: float  # 청각적 학습 선호도 (0-1)
    kinesthetic_learner: float  # 체험적 학습 선호도 (0-1)
    reading_learner: float  # 읽기/쓰기 학습 선호도 (0-1)
    pace_preference: str  # 'slow', 'normal', 'fast'
    difficulty_tolerance: float  # 난이도 허용도 (0-1)
    interaction_preference: str  # 'individual', 'collaborative'
    feedback_frequency: str  # 'immediate', 'periodic', 'minimal'

@dataclass
class LearningSession:
    """학습 세션 분석 데이터"""
    session_id: str
    user_id: str
    start_time: datetime
    duration_minutes: int
    module: str
    completion_rate: float
    difficulty_rating: int
    satisfaction_score: int
    mistakes_count: int
    help_requests: int
    interaction_patterns: Dict[str, Any]

@dataclass
class KnowledgeState:
    """지식 상태 모델"""
    user_id: str
    skill_areas: Dict[str, float]  # 스킬 영역별 숙련도 (0-1)
    knowledge_gaps: List[str]  # 부족한 지식 영역
    learning_velocity: float  # 학습 속도
    retention_rate: float  # 지식 보존율
    last_updated: datetime

class PersonalizedAITutor:
    """AI 기반 개인화 튜터 시스템"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.openai_client = openai.OpenAI(api_key=config['openai_api_key'])
        
        # NLP 모델 초기화
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.summarizer = pipeline("summarization")
        
        # 스타일 분석을 위한 언어 모델
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy 영어 모델이 설치되지 않음. 기본 기능만 사용합니다.")
            self.nlp = None
            
        # 학습 성과 예측 모델
        self.performance_predictor = None
        self.scaler = StandardScaler()
        
        # 개인화 매개변수
        self.learning_styles = ['visual', 'auditory', 'kinesthetic', 'reading']
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        
    async def analyze_learning_style(self, user_interactions: List[Dict]) -> LearningPreference:
        """학습 스타일 자동 분석"""
        try:
            # 상호작용 패턴 분석
            visual_indicators = 0
            auditory_indicators = 0  
            kinesthetic_indicators = 0
            reading_indicators = 0
            
            total_interactions = len(user_interactions)
            
            for interaction in user_interactions:
                interaction_type = interaction.get('type', '')
                duration = interaction.get('duration', 0)
                success_rate = interaction.get('success_rate', 0.5)
                
                # 시각적 학습 지표
                if interaction_type in ['diagram_view', 'video_watch', 'image_interaction']:
                    visual_indicators += success_rate * (duration / 60)  # 분 단위로 정규화
                    
                # 청각적 학습 지표
                elif interaction_type in ['audio_listen', 'podcast_play', 'voice_command']:
                    auditory_indicators += success_rate * (duration / 60)
                    
                # 체험적 학습 지표
                elif interaction_type in ['hands_on_lab', 'simulation', 'code_practice']:
                    kinesthetic_indicators += success_rate * (duration / 60)
                    
                # 읽기/쓰기 학습 지표
                elif interaction_type in ['text_read', 'note_taking', 'documentation']:
                    reading_indicators += success_rate * (duration / 60)
            
            # 정규화
            total_score = visual_indicators + auditory_indicators + kinesthetic_indicators + reading_indicators
            
            if total_score > 0:
                visual_pref = visual_indicators / total_score
                auditory_pref = auditory_indicators / total_score
                kinesthetic_pref = kinesthetic_indicators / total_score
                reading_pref = reading_indicators / total_score
            else:
                # 기본값
                visual_pref = auditory_pref = kinesthetic_pref = reading_pref = 0.25
            
            # 학습 페이스 분석
            avg_session_duration = np.mean([i.get('duration', 0) for i in user_interactions])
            completion_rates = [i.get('completion_rate', 0.5) for i in user_interactions]
            
            if avg_session_duration < 15:  # 15분 미만
                pace = 'fast'
            elif avg_session_duration > 45:  # 45분 초과
                pace = 'slow'
            else:
                pace = 'normal'
                
            # 난이도 허용도 분석
            difficulty_tolerance = np.mean([i.get('difficulty_rating', 3) for i in user_interactions]) / 5.0
            
            return LearningPreference(
                visual_learner=visual_pref,
                auditory_learner=auditory_pref,
                kinesthetic_learner=kinesthetic_pref,
                reading_learner=reading_pref,
                pace_preference=pace,
                difficulty_tolerance=difficulty_tolerance,
                interaction_preference='individual',  # 기본값
                feedback_frequency='immediate'  # 기본값
            )
            
        except Exception as e:
            logger.error(f"학습 스타일 분석 오류: {e}")
            # 기본 학습 선호도 반환
            return LearningPreference(0.25, 0.25, 0.25, 0.25, 'normal', 0.5, 'individual', 'immediate')
    
    async def generate_personalized_content(
        self, 
        user_id: str, 
        topic: str, 
        learning_preference: LearningPreference,
        knowledge_state: KnowledgeState
    ) -> Dict[str, Any]:
        """개인화된 학습 콘텐츠 생성"""
        try:
            # 학습자 프로필 분석
            dominant_style = max(
                ('visual', learning_preference.visual_learner),
                ('auditory', learning_preference.auditory_learner),
                ('kinesthetic', learning_preference.kinesthetic_learner),
                ('reading', learning_preference.reading_learner)
            )[0]
            
            # 현재 지식 수준 평가
            topic_skill_level = knowledge_state.skill_areas.get(topic, 0.0)
            
            if topic_skill_level < 0.3:
                difficulty = 'beginner'
            elif topic_skill_level < 0.6:
                difficulty = 'intermediate'
            elif topic_skill_level < 0.8:
                difficulty = 'advanced'
            else:
                difficulty = 'expert'
            
            # GPT-4를 사용한 개인화된 콘텐츠 생성
            prompt = f"""
            Arduino IoT DevOps 학습자를 위한 개인화된 {topic} 학습 콘텐츠를 생성해주세요.

            학습자 특성:
            - 주요 학습 스타일: {dominant_style}
            - 현재 스킬 레벨: {difficulty}
            - 학습 페이스: {learning_preference.pace_preference}
            - 난이도 허용도: {learning_preference.difficulty_tolerance:.1f}/1.0
            - 피드백 선호: {learning_preference.feedback_frequency}

            현재 지식 상태:
            - {topic} 숙련도: {topic_skill_level:.1f}/1.0
            - 부족한 영역: {', '.join(knowledge_state.knowledge_gaps[:3])}
            - 학습 속도: {knowledge_state.learning_velocity:.1f}

            다음 형식으로 JSON 응답을 생성해주세요:
            {{
                "learning_objectives": ["목표1", "목표2", "목표3"],
                "content_structure": {{
                    "introduction": "소개 내용",
                    "core_concepts": ["개념1", "개념2", "개념3"],
                    "practical_examples": ["예제1", "예제2"],
                    "hands_on_activities": ["실습1", "실습2"],
                    "assessment_questions": ["질문1", "질문2"]
                }},
                "learning_path": ["단계1", "단계2", "단계3"],
                "estimated_duration": "예상 소요 시간",
                "difficulty_progression": ["easy", "medium", "hard"],
                "multimedia_suggestions": {{
                    "videos": ["비디오 추천"],
                    "diagrams": ["다이어그램 추천"],
                    "interactive_demos": ["인터랙티브 데모"]
                }},
                "personalized_tips": ["개인화된 팁1", "팁2", "팁3"]
            }}
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 Arduino IoT DevOps 전문 교육자이며, 개인의 학습 스타일에 맞는 맞춤형 콘텐츠를 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = json.loads(response.choices[0].message.content)
            
            # 학습 스타일에 따른 콘텐츠 조정
            if dominant_style == 'visual':
                content['emphasis'] = 'diagrams_and_visuals'
                content['content_type'] = 'infographic'
            elif dominant_style == 'auditory':
                content['emphasis'] = 'explanations_and_discussions'
                content['content_type'] = 'podcast'
            elif dominant_style == 'kinesthetic':
                content['emphasis'] = 'hands_on_practice'
                content['content_type'] = 'lab_exercise'
            else:  # reading
                content['emphasis'] = 'detailed_documentation'
                content['content_type'] = 'comprehensive_guide'
                
            content['generated_for'] = user_id
            content['generation_time'] = datetime.now().isoformat()
            
            return content
            
        except Exception as e:
            logger.error(f"개인화 콘텐츠 생성 오류: {e}")
            return {"error": str(e)}
    
    async def adaptive_difficulty_adjustment(
        self, 
        user_id: str, 
        current_performance: Dict,
        learning_history: List[Dict]
    ) -> Dict[str, Any]:
        """적응형 난이도 조정"""
        try:
            # 최근 성과 분석
            recent_scores = [session.get('score', 0) for session in learning_history[-10:]]
            recent_completion_rates = [session.get('completion_rate', 0) for session in learning_history[-10:]]
            recent_time_taken = [session.get('duration', 0) for session in learning_history[-10:]]
            
            avg_score = np.mean(recent_scores) if recent_scores else 0.5
            avg_completion = np.mean(recent_completion_rates) if recent_completion_rates else 0.5
            avg_time = np.mean(recent_time_taken) if recent_time_taken else 30
            
            # 현재 난이도 레벨
            current_difficulty = current_performance.get('difficulty_level', 'intermediate')
            difficulty_index = self.difficulty_levels.index(current_difficulty)
            
            # 조정 알고리즘
            adjustment = 0
            
            # 성과가 너무 좋으면 난이도 증가
            if avg_score > 0.9 and avg_completion > 0.95:
                adjustment = 1
                reason = "성과가 우수하여 난이도를 높입니다."
                
            # 성과가 좋지 않으면 난이도 감소  
            elif avg_score < 0.6 or avg_completion < 0.7:
                adjustment = -1
                reason = "학습 효과를 위해 난이도를 낮춥니다."
                
            # 시간이 너무 오래 걸리면 난이도 감소
            elif avg_time > 60:  # 60분 초과
                adjustment = -1
                reason = "학습 시간이 길어 난이도를 조정합니다."
                
            else:
                adjustment = 0
                reason = "현재 난이도가 적절합니다."
            
            # 새로운 난이도 계산
            new_difficulty_index = max(0, min(len(self.difficulty_levels) - 1, difficulty_index + adjustment))
            new_difficulty = self.difficulty_levels[new_difficulty_index]
            
            # 개인화된 학습 제안 생성
            suggestions = await self._generate_learning_suggestions(
                avg_score, avg_completion, avg_time, new_difficulty
            )
            
            return {
                'current_difficulty': current_difficulty,
                'recommended_difficulty': new_difficulty,
                'adjustment_reason': reason,
                'performance_analysis': {
                    'average_score': round(avg_score, 2),
                    'average_completion': round(avg_completion, 2),
                    'average_time_minutes': round(avg_time, 1)
                },
                'learning_suggestions': suggestions,
                'confidence_score': self._calculate_confidence_score(recent_scores)
            }
            
        except Exception as e:
            logger.error(f"적응형 난이도 조정 오류: {e}")
            return {"error": str(e)}
    
    async def _generate_learning_suggestions(
        self, avg_score: float, avg_completion: float, avg_time: float, new_difficulty: str
    ) -> List[str]:
        """학습 제안 생성"""
        suggestions = []
        
        if avg_score < 0.7:
            suggestions.append("기초 개념 복습을 통해 이해도를 높이세요.")
            suggestions.append("더 많은 예제와 실습을 통해 연습하세요.")
            
        if avg_completion < 0.8:
            suggestions.append("학습 세션을 더 짧게 나누어 집중도를 높이세요.")
            suggestions.append("중간중간 휴식을 취하며 학습하세요.")
            
        if avg_time > 45:
            suggestions.append("학습 내용을 세분화하여 단계별로 접근하세요.")
            suggestions.append("우선순위가 높은 핵심 개념부터 학습하세요.")
            
        if new_difficulty == 'advanced':
            suggestions.append("실제 프로젝트에 적용해보며 실무 경험을 쌓으세요.")
            suggestions.append("동료들과 함께 협업 프로젝트에 도전해보세요.")
            
        return suggestions
    
    def _calculate_confidence_score(self, recent_scores: List[float]) -> float:
        """학습 자신감 점수 계산"""
        if not recent_scores:
            return 0.5
            
        # 점수의 일관성과 트렌드 분석
        consistency = 1.0 - np.std(recent_scores)  # 표준편차가 낮을수록 일관성 높음
        trend = np.mean(np.diff(recent_scores)) if len(recent_scores) > 1 else 0  # 상승 트렌드
        average = np.mean(recent_scores)
        
        confidence = (consistency * 0.3 + (trend + 1) * 0.3 + average * 0.4)
        return max(0.0, min(1.0, confidence))

class LearningAnalyticsEngine:
    """학습 분석 엔진"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def predict_learning_outcome(self, user_features: Dict) -> Dict[str, float]:
        """학습 성과 예측"""
        try:
            # 특성 벡터 생성
            features = [
                user_features.get('current_skill_level', 0.5),
                user_features.get('learning_time_per_week', 10),
                user_features.get('previous_programming_experience', 0.5),
                user_features.get('motivation_score', 0.7),
                user_features.get('consistency_score', 0.6),
                user_features.get('age', 25) / 100,  # 정규화
                user_features.get('education_level', 3) / 5,  # 정규화
            ]
            
            # 간단한 휴리스틱 기반 예측 (실제로는 훈련된 ML 모델 사용)
            base_success_rate = np.mean(features)
            
            # 가중치 적용
            weights = [0.25, 0.2, 0.15, 0.15, 0.15, 0.05, 0.05]
            weighted_score = sum(f * w for f, w in zip(features, weights))
            
            # 예측 결과
            predictions = {
                'completion_probability': min(1.0, weighted_score + 0.1),
                'expected_final_score': min(10.0, weighted_score * 10),
                'estimated_completion_weeks': max(8, 12 - weighted_score * 4),
                'risk_level': 'low' if weighted_score > 0.7 else 'medium' if weighted_score > 0.5 else 'high'
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"학습 성과 예측 오류: {e}")
            return {
                'completion_probability': 0.7,
                'expected_final_score': 7.0,
                'estimated_completion_weeks': 10,
                'risk_level': 'medium'
            }
    
    def generate_learning_insights(self, user_data: Dict) -> Dict[str, Any]:
        """학습 인사이트 생성"""
        try:
            insights = {
                'learning_pattern': self._analyze_learning_pattern(user_data),
                'strengths': self._identify_strengths(user_data),
                'improvement_areas': self._identify_improvement_areas(user_data),
                'optimal_study_time': self._recommend_study_time(user_data),
                'peer_comparison': self._compare_with_peers(user_data)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"학습 인사이트 생성 오류: {e}")
            return {}
    
    def _analyze_learning_pattern(self, user_data: Dict) -> Dict[str, Any]:
        """학습 패턴 분석"""
        sessions = user_data.get('sessions', [])
        
        if not sessions:
            return {"pattern": "insufficient_data"}
        
        # 시간대별 학습 패턴
        hours = [datetime.fromisoformat(s['start_time']).hour for s in sessions]
        peak_hour = max(set(hours), key=hours.count) if hours else 9
        
        # 요일별 학습 패턴
        weekdays = [datetime.fromisoformat(s['start_time']).weekday() for s in sessions]
        most_active_day = max(set(weekdays), key=weekdays.count) if weekdays else 1
        
        # 학습 지속성
        session_gaps = []
        for i in range(1, len(sessions)):
            prev_time = datetime.fromisoformat(sessions[i-1]['start_time'])
            curr_time = datetime.fromisoformat(sessions[i]['start_time'])
            gap_days = (curr_time - prev_time).days
            session_gaps.append(gap_days)
        
        consistency = 1.0 / (np.std(session_gaps) + 1) if session_gaps else 0.5
        
        return {
            'pattern': 'consistent' if consistency > 0.7 else 'irregular',
            'peak_learning_hour': peak_hour,
            'most_active_day': ['월', '화', '수', '목', '금', '토', '일'][most_active_day],
            'consistency_score': round(consistency, 2),
            'average_session_gap_days': round(np.mean(session_gaps), 1) if session_gaps else 0
        }
    
    def _identify_strengths(self, user_data: Dict) -> List[str]:
        """강점 영역 식별"""
        strengths = []
        sessions = user_data.get('sessions', [])
        
        if not sessions:
            return strengths
        
        # 모듈별 성과 분석
        module_scores = {}
        for session in sessions:
            module = session.get('module', 'unknown')
            score = session.get('score', 0)
            
            if module not in module_scores:
                module_scores[module] = []
            module_scores[module].append(score)
        
        # 평균 점수가 높은 모듈들
        for module, scores in module_scores.items():
            avg_score = np.mean(scores)
            if avg_score > 8.0:
                strengths.append(f"{module} 영역에서 우수한 성과")
        
        # 학습 속도 분석
        completion_rates = [s.get('completion_rate', 0) for s in sessions]
        if np.mean(completion_rates) > 0.9:
            strengths.append("빠른 학습 진도와 높은 완주율")
        
        # 일관성 분석
        consistency = self._analyze_learning_pattern(user_data)['consistency_score']
        if consistency > 0.8:
            strengths.append("꾸준한 학습 습관과 높은 지속성")
            
        return strengths
    
    def _identify_improvement_areas(self, user_data: Dict) -> List[str]:
        """개선 영역 식별"""
        improvements = []
        sessions = user_data.get('sessions', [])
        
        if not sessions:
            return ["충분한 학습 데이터가 없어 분석이 어렵습니다"]
        
        # 모듈별 취약점 분석
        module_scores = {}
        for session in sessions:
            module = session.get('module', 'unknown')
            score = session.get('score', 0)
            
            if module not in module_scores:
                module_scores[module] = []
            module_scores[module].append(score)
        
        # 평균 점수가 낮은 모듈들
        for module, scores in module_scores.items():
            avg_score = np.mean(scores)
            if avg_score < 6.0:
                improvements.append(f"{module} 영역의 기초 개념 보강 필요")
        
        # 완료율 분석
        completion_rates = [s.get('completion_rate', 0) for s in sessions]
        if np.mean(completion_rates) < 0.7:
            improvements.append("학습 완료율 향상을 위한 시간 관리 개선")
        
        # 학습 시간 분석
        durations = [s.get('duration', 0) for s in sessions]
        if np.mean(durations) > 60:  # 60분 초과
            improvements.append("학습 세션을 더 짧게 나누어 집중도 향상")
            
        return improvements
    
    def _recommend_study_time(self, user_data: Dict) -> Dict[str, Any]:
        """최적 학습 시간 추천"""
        sessions = user_data.get('sessions', [])
        
        if not sessions:
            return {
                "recommended_duration": 30,
                "recommended_frequency": "daily",
                "best_time": "09:00"
            }
        
        # 성과가 좋았던 세션들의 패턴 분석
        high_performance_sessions = [
            s for s in sessions 
            if s.get('score', 0) > 7.5 and s.get('completion_rate', 0) > 0.8
        ]
        
        if high_performance_sessions:
            avg_duration = np.mean([s.get('duration', 30) for s in high_performance_sessions])
            peak_hours = [datetime.fromisoformat(s['start_time']).hour for s in high_performance_sessions]
            best_hour = max(set(peak_hours), key=peak_hours.count)
        else:
            avg_duration = 30
            best_hour = 9
        
        return {
            "recommended_duration": int(avg_duration),
            "recommended_frequency": "daily" if len(sessions) > 20 else "3-4 times/week",
            "best_time": f"{best_hour:02d}:00"
        }
    
    def _compare_with_peers(self, user_data: Dict) -> Dict[str, Any]:
        """동료와의 비교 분석"""
        # 실제로는 데이터베이스에서 동료 데이터를 가져와 비교
        # 여기서는 시뮬레이션 데이터 사용
        
        user_avg_score = np.mean([s.get('score', 0) for s in user_data.get('sessions', [])])
        user_completion_rate = np.mean([s.get('completion_rate', 0) for s in user_data.get('sessions', [])])
        
        # 가상의 동료 평균 (실제로는 DB에서 계산)
        peer_avg_score = 7.2
        peer_completion_rate = 0.78
        
        return {
            "score_percentile": min(100, max(0, int((user_avg_score / peer_avg_score) * 50 + 25))),
            "completion_percentile": min(100, max(0, int((user_completion_rate / peer_completion_rate) * 50 + 25))),
            "peer_avg_score": peer_avg_score,
            "peer_completion_rate": peer_completion_rate,
            "performance_status": "above_average" if user_avg_score > peer_avg_score else "below_average"
        }

class StreamlitChatInterface:
    """Streamlit 기반 채팅 인터페이스"""
    
    def __init__(self, ai_tutor: PersonalizedAITutor):
        self.ai_tutor = ai_tutor
        
    def run_chat_interface(self):
        """채팅 인터페이스 실행"""
        st.title("🤖 Arduino IoT DevOps AI 튜터")
        st.markdown("개인화된 학습 지원을 위한 AI 어시스턴트입니다.")
        
        # 사이드바 - 사용자 설정
        with st.sidebar:
            st.header("🎯 학습 설정")
            
            user_level = st.selectbox(
                "현재 수준",
                ["초급자", "중급자", "고급자", "전문가"],
                index=1
            )
            
            learning_goal = st.selectbox(
                "학습 목표",
                ["기초 이해", "실무 적용", "전문가 되기", "인증 취득"],
                index=1
            )
            
            preferred_style = st.selectbox(
                "선호 학습 방식",
                ["시각적", "청각적", "실습 중심", "읽기/쓰기"],
                index=2
            )
            
            st.markdown("---")
            st.markdown("### 📊 학습 진도")
            progress = st.progress(0.65)
            st.markdown("전체 진도: 65%")
        
        # 메인 채팅 영역
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"안녕하세요! Arduino IoT DevOps AI 튜터입니다. 현재 {user_level} 수준으로 설정되어 있고, '{learning_goal}' 을 목표로 학습하시는군요. 어떤 도움이 필요하신가요?"
                }
            ]
        
        # 채팅 메시지 표시
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                message(message["content"], is_user=True, key=f"user_{i}")
            else:
                message(message["content"], key=f"assistant_{i}")
        
        # 사용자 입력
        user_input = st.chat_input("질문이나 도움이 필요한 내용을 입력하세요...")
        
        if user_input:
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # AI 응답 생성
            with st.spinner("답변을 생성하고 있습니다..."):
                response = asyncio.run(self._generate_ai_response(
                    user_input, user_level, learning_goal, preferred_style
                ))
            
            # AI 응답 추가
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # 새로운 메시지 표시
            message(user_input, is_user=True, key=f"user_{len(st.session_state.messages)-2}")
            message(response, key=f"assistant_{len(st.session_state.messages)-1}")
        
        # 빠른 질문 버튼들
        st.markdown("### 💡 빠른 질문")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("환경 설정 도움"):
                self._add_quick_question("개발 환경 설정에서 문제가 있어요")
        
        with col2:
            if st.button("코드 리뷰 요청"):
                self._add_quick_question("제 Arduino 코드를 리뷰해주세요")
                
        with col3:
            if st.button("학습 계획 추천"):
                self._add_quick_question("다음에 무엇을 학습하면 좋을까요?")
    
    async def _generate_ai_response(self, user_input: str, level: str, goal: str, style: str) -> str:
        """AI 응답 생성"""
        try:
            context = f"""
            사용자 정보:
            - 수준: {level}
            - 목표: {goal}  
            - 선호 방식: {style}
            
            이전 대화: {st.session_state.messages[-3:] if len(st.session_state.messages) > 3 else []}
            """
            
            response = await self.ai_tutor.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""당신은 Arduino IoT DevOps 전문 AI 튜터입니다. 
                        사용자의 수준({level})과 목표({goal})에 맞는 맞춤형 답변을 제공하세요.
                        {style} 학습 방식을 선호하는 점을 고려하여 응답하세요.
                        친근하고 격려하는 톤으로 답변하며, 구체적인 예시와 실습 방법을 포함하세요."""
                    },
                    {"role": "user", "content": f"{context}\n\n질문: {user_input}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI 응답 생성 오류: {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _add_quick_question(self, question: str):
        """빠른 질문 추가"""
        st.session_state.messages.append({"role": "user", "content": question})
        st.experimental_rerun()

def create_learning_visualization(user_data: Dict) -> Dict[str, Any]:
    """학습 시각화 생성"""
    try:
        # 진도 차트
        weeks = list(range(1, 13))
        progress = user_data.get('weekly_progress', [10*i + np.random.randint(-5, 5) for i in weeks])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weeks,
            y=progress,
            mode='lines+markers',
            name='학습 진도',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='주간 학습 진도',
            xaxis_title='주차',
            yaxis_title='진도 (%)',
            template='plotly_white'
        )
        
        # 스킬 레이더 차트
        skills = ['Arduino', 'Linux', 'Git', 'VSCode', 'SSH', 'Docker', 'Jenkins', 'Jira']
        values = user_data.get('skill_levels', [7, 6, 8, 9, 7, 5, 4, 3])
        
        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # 닫힌 도형을 위해 첫 값 반복
            theta=skills + [skills[0]],
            fill='toself',
            name='현재 스킬 레벨',
            line_color='#667eea'
        ))
        
        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10])
            ),
            title='스킬 레이더 차트'
        )
        
        return {
            'progress_chart': fig,
            'skill_radar': radar_fig,
            'summary_stats': {
                'total_hours': user_data.get('total_hours', 87),
                'modules_completed': user_data.get('modules_completed', 24),
                'current_streak': user_data.get('current_streak', 12),
                'overall_score': user_data.get('overall_score', 7.8)
            }
        }
        
    except Exception as e:
        logger.error(f"학습 시각화 생성 오류: {e}")
        return {}

# 메인 실행 함수
async def main():
    """메인 실행 함수"""
    # 설정 로드
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY', 'your-api-key'),
        'db_path': 'data/learning.db'
    }
    
    # AI 튜터 초기화
    ai_tutor = PersonalizedAITutor(config)
    analytics_engine = LearningAnalyticsEngine(config['db_path'])
    
    # Streamlit 인터페이스 실행
    if len(sys.argv) > 1 and sys.argv[1] == '--streamlit':
        chat_interface = StreamlitChatInterface(ai_tutor)
        chat_interface.run_chat_interface()
    else:
        # CLI 모드에서 테스트 실행
        print("🤖 Arduino IoT DevOps AI 개인화 학습 시스템")
        print("=" * 50)
        
        # 샘플 사용자 데이터
        sample_user_data = {
            'user_id': 'test_user_001',
            'sessions': [
                {
                    'start_time': '2024-01-15T09:00:00',
                    'duration': 45,
                    'module': 'arduino_basics',
                    'score': 8.5,
                    'completion_rate': 0.95,
                    'difficulty_rating': 3
                },
                {
                    'start_time': '2024-01-16T14:00:00', 
                    'duration': 30,
                    'module': 'git_workflow',
                    'score': 7.2,
                    'completion_rate': 0.80,
                    'difficulty_rating': 4
                }
            ],
            'interactions': [
                {'type': 'hands_on_lab', 'duration': 1800, 'success_rate': 0.9},
                {'type': 'video_watch', 'duration': 900, 'success_rate': 0.8},
                {'type': 'text_read', 'duration': 600, 'success_rate': 0.7}
            ]
        }
        
        # 학습 스타일 분석
        learning_pref = await ai_tutor.analyze_learning_style(sample_user_data['interactions'])
        print(f"📊 학습 스타일 분석:")
        print(f"  - 시각적: {learning_pref.visual_learner:.2f}")
        print(f"  - 청각적: {learning_pref.auditory_learner:.2f}")
        print(f"  - 체험적: {learning_pref.kinesthetic_learner:.2f}")
        print(f"  - 읽기/쓰기: {learning_pref.reading_learner:.2f}")
        print(f"  - 선호 페이스: {learning_pref.pace_preference}")
        
        # 학습 인사이트 생성
        insights = analytics_engine.generate_learning_insights(sample_user_data)
        print(f"\n💡 학습 인사이트:")
        print(f"  - 학습 패턴: {insights.get('learning_pattern', {}).get('pattern', 'N/A')}")
        print(f"  - 강점: {', '.join(insights.get('strengths', ['분석 중...']))}")
        print(f"  - 개선 영역: {', '.join(insights.get('improvement_areas', ['분석 중...']))}")
        
        print("\n✅ AI 개인화 학습 시스템 테스트 완료!")

if __name__ == "__main__":
    import sys
    if '--streamlit' in sys.argv:
        # Streamlit 앱 실행: streamlit run personalized-learning-ai.py -- --streamlit
        pass
    else:
        asyncio.run(main())