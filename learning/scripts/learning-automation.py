#!/usr/bin/env python3
"""
Arduino IoT DevOps 학습 자동화 시스템

이 스크립트는 학습자의 진도를 추적하고, 개인화된 학습 경험을 제공하며,
AI 기반 피드백과 자동화된 평가를 수행합니다.

Author: Arduino DevOps Education Team
Version: 2.0.0
License: MIT
"""

import os
import json
import sqlite3
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import openai
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import smtplib
import schedule
import time
import subprocess
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/learning_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LearningSession:
    """학습 세션 데이터 클래스"""
    user_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    module: str
    week: int
    day: int
    tasks_completed: List[str]
    time_spent: int  # 분 단위
    score: Optional[float]
    difficulty_rating: Optional[int]
    feedback: Optional[str]

@dataclass
class UserProfile:
    """사용자 프로필 데이터 클래스"""
    user_id: str
    name: str
    email: str
    start_date: datetime
    current_level: int
    current_week: int
    current_day: int
    total_hours: float
    completed_modules: List[str]
    skill_scores: Dict[str, float]
    learning_style: str
    preferred_pace: str
    last_active: datetime

class LearningDatabase:
    """학습 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "data/learning.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 사용자 프로필 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                start_date TIMESTAMP,
                current_level INTEGER DEFAULT 1,
                current_week INTEGER DEFAULT 1,
                current_day INTEGER DEFAULT 1,
                total_hours REAL DEFAULT 0.0,
                completed_modules TEXT DEFAULT '[]',
                skill_scores TEXT DEFAULT '{}',
                learning_style TEXT DEFAULT 'balanced',
                preferred_pace TEXT DEFAULT 'normal',
                last_active TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 학습 세션 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                module TEXT,
                week INTEGER,
                day INTEGER,
                tasks_completed TEXT DEFAULT '[]',
                time_spent INTEGER DEFAULT 0,
                score REAL,
                difficulty_rating INTEGER,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # 평가 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                assessment_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                module TEXT,
                assessment_type TEXT,
                score REAL,
                max_score REAL,
                time_taken INTEGER,
                answers TEXT,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # AI 추천 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                recommendation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                recommendation_type TEXT,
                content TEXT,
                priority INTEGER DEFAULT 1,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("데이터베이스 초기화 완료")

class AITutor:
    """AI 기반 개인 튜터 시스템"""
    
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.client = openai.OpenAI()
        
    async def analyze_learning_pattern(self, user_profile: UserProfile, sessions: List[LearningSession]) -> Dict:
        """학습 패턴 분석"""
        try:
            # 세션 데이터 분석
            if not sessions:
                return {"analysis": "충분한 학습 데이터가 없습니다."}
                
            total_time = sum(session.time_spent for session in sessions)
            avg_score = np.mean([s.score for s in sessions if s.score is not None])
            difficulty_ratings = [s.difficulty_rating for s in sessions if s.difficulty_rating is not None]
            
            # GPT-4를 사용한 학습 패턴 분석
            prompt = f"""
            Arduino IoT DevOps 학습자의 데이터를 분석해주세요:
            
            사용자 정보:
            - 이름: {user_profile.name}
            - 현재 레벨: {user_profile.current_level}
            - 총 학습 시간: {user_profile.total_hours}시간
            - 학습 스타일: {user_profile.learning_style}
            
            최근 학습 세션 분석:
            - 총 세션 수: {len(sessions)}
            - 총 학습 시간: {total_time}분
            - 평균 점수: {avg_score:.1f}/10
            - 평균 어려움 정도: {np.mean(difficulty_ratings) if difficulty_ratings else 'N/A'}
            
            다음 항목들을 JSON 형식으로 분석해주세요:
            1. 강점 영역 (strengths)
            2. 개선 필요 영역 (areas_for_improvement)  
            3. 학습 패턴 특징 (learning_patterns)
            4. 개인화된 추천사항 (recommendations)
            5. 다음 주 학습 목표 (next_week_goals)
            """
            
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 Arduino IoT DevOps 전문 교육자입니다. 학습자의 데이터를 분석하여 개인화된 피드백을 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"학습 패턴 분석 오류: {e}")
            return {"error": str(e)}
    
    async def generate_personalized_content(self, user_profile: UserProfile, topic: str) -> str:
        """개인화된 학습 콘텐츠 생성"""
        try:
            prompt = f"""
            {user_profile.name}님을 위한 개인화된 {topic} 학습 콘텐츠를 생성해주세요.
            
            사용자 특성:
            - 현재 레벨: Level {user_profile.current_level}
            - 학습 스타일: {user_profile.learning_style}
            - 선호 페이스: {user_profile.preferred_pace}
            - 현재 스킬 수준: {user_profile.skill_scores}
            
            다음 형식으로 생성해주세요:
            1. 학습 목표 (3-5개 bullet points)
            2. 핵심 개념 설명 (사용자 레벨에 맞게)
            3. 실습 예제 (단계별 가이드)
            4. 체크포인트 질문 (이해도 확인용)
            5. 추가 리소스 (심화 학습용)
            
            Markdown 형식으로 작성해주세요.
            """
            
            response = await self.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 Arduino IoT DevOps 전문 강사입니다. 학습자의 수준에 맞는 맞춤형 콘텐츠를 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"개인화 콘텐츠 생성 오류: {e}")
            return f"콘텐츠 생성 중 오류가 발생했습니다: {e}"

class LearningAnalytics:
    """학습 분석 및 인사이트 생성"""
    
    def __init__(self, db: LearningDatabase):
        self.db = db
        
    def generate_progress_report(self, user_id: str) -> Dict:
        """진행률 리포트 생성"""
        conn = sqlite3.connect(self.db.db_path)
        
        # 사용자 프로필 조회
        profile_df = pd.read_sql_query(
            "SELECT * FROM user_profiles WHERE user_id = ?", 
            conn, params=[user_id]
        )
        
        if profile_df.empty:
            return {"error": "사용자를 찾을 수 없습니다."}
            
        # 학습 세션 데이터 조회
        sessions_df = pd.read_sql_query(
            "SELECT * FROM learning_sessions WHERE user_id = ? ORDER BY created_at", 
            conn, params=[user_id]
        )
        
        # 평가 결과 조회
        assessments_df = pd.read_sql_query(
            "SELECT * FROM assessments WHERE user_id = ? ORDER BY created_at", 
            conn, params=[user_id]
        )
        
        conn.close()
        
        if sessions_df.empty:
            return {"message": "아직 학습 세션이 없습니다."}
            
        profile = profile_df.iloc[0]
        
        # 진행률 계산
        total_weeks = 12
        current_week = profile['current_week']
        progress_percentage = (current_week / total_weeks) * 100
        
        # 학습 시간 분석
        daily_hours = sessions_df.groupby(sessions_df['created_at'].str[:10])['time_spent'].sum() / 60
        avg_daily_hours = daily_hours.mean()
        
        # 점수 트렌드 분석
        score_trend = sessions_df['score'].rolling(window=5, min_periods=1).mean()
        
        # 모듈별 성과
        module_performance = sessions_df.groupby('module').agg({
            'score': 'mean',
            'time_spent': 'sum'
        }).round(2)
        
        # 예측 완료 날짜
        remaining_weeks = total_weeks - current_week
        if avg_daily_hours > 0:
            estimated_days = (remaining_weeks * 7 * 2) / avg_daily_hours  # 주당 14시간 예상
            estimated_completion = datetime.now() + timedelta(days=estimated_days)
        else:
            estimated_completion = None
            
        report = {
            "user_name": profile['name'],
            "current_level": profile['current_level'],
            "progress_percentage": round(progress_percentage, 1),
            "current_week": current_week,
            "total_hours": round(profile['total_hours'], 1),
            "avg_daily_hours": round(avg_daily_hours, 1),
            "latest_score": sessions_df['score'].iloc[-1] if not sessions_df.empty else None,
            "score_trend": "상승" if len(score_trend) > 1 and score_trend.iloc[-1] > score_trend.iloc[-2] else "하락",
            "module_performance": module_performance.to_dict(),
            "estimated_completion": estimated_completion.strftime("%Y-%m-%d") if estimated_completion else None,
            "sessions_count": len(sessions_df),
            "assessments_count": len(assessments_df)
        }
        
        return report
    
    def create_skill_radar_data(self, user_id: str) -> Dict:
        """스킬 레이더 차트 데이터 생성"""
        conn = sqlite3.connect(self.db.db_path)
        
        profile_df = pd.read_sql_query(
            "SELECT skill_scores FROM user_profiles WHERE user_id = ?", 
            conn, params=[user_id]
        )
        
        conn.close()
        
        if profile_df.empty:
            return {"error": "사용자를 찾을 수 없습니다."}
            
        skill_scores = json.loads(profile_df.iloc[0]['skill_scores'] or '{}')
        
        # 기본 스킬 카테고리
        default_skills = {
            "Arduino": 0,
            "Linux": 0, 
            "Git": 0,
            "VSCode": 0,
            "SSH": 0,
            "Docker": 0,
            "Jenkins": 0,
            "Jira": 0
        }
        
        # 기존 점수와 병합
        default_skills.update(skill_scores)
        
        return {
            "skills": list(default_skills.keys()),
            "current_levels": list(default_skills.values()),
            "target_levels": [9, 8, 9, 9, 8, 8, 8, 7]  # 목표 레벨
        }

class AutomatedAssessment:
    """자동화된 평가 시스템"""
    
    def __init__(self, db: LearningDatabase, ai_tutor: AITutor):
        self.db = db
        self.ai_tutor = ai_tutor
        
    async def run_code_assessment(self, user_id: str, code: str, expected_output: str) -> Dict:
        """코드 평가 실행"""
        try:
            # 임시 파일에 코드 저장
            temp_file = f"temp/{user_id}_assessment.ino"
            os.makedirs("temp", exist_ok=True)
            
            with open(temp_file, 'w') as f:
                f.write(code)
                
            # Arduino CLI로 컴파일 테스트
            result = subprocess.run(
                ["arduino-cli", "compile", "--fqbn", "arduino:avr:uno", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            compile_success = result.returncode == 0
            
            # AI를 통한 코드 품질 분석
            code_analysis = await self.ai_tutor.client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 Arduino 코드 리뷰 전문가입니다. 코드의 품질, 효율성, 베스트 프랙티스 준수 여부를 평가해주세요."},
                    {"role": "user", "content": f"다음 Arduino 코드를 평가해주세요:\n\n{code}\n\n평가 기준: 문법, 로직, 효율성, 가독성, 베스트 프랙티스"}
                ],
                temperature=0.2
            )
            
            # 점수 계산
            base_score = 70 if compile_success else 0
            
            # AI 분석 결과에 따른 점수 조정 (간단한 키워드 기반)
            analysis_text = code_analysis.choices[0].message.content.lower()
            if "excellent" in analysis_text or "훌륭" in analysis_text:
                base_score += 30
            elif "good" in analysis_text or "좋" in analysis_text:
                base_score += 20
            elif "fair" in analysis_text or "보통" in analysis_text:
                base_score += 10
                
            final_score = min(100, base_score)
            
            # 결과 저장
            assessment_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO assessments (
                    assessment_id, user_id, module, assessment_type, 
                    score, max_score, answers, feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                assessment_id, user_id, "arduino_coding", "code_review",
                final_score, 100, json.dumps({"code": code}),
                code_analysis.choices[0].message.content
            ))
            
            conn.commit()
            conn.close()
            
            # 임시 파일 정리
            os.remove(temp_file)
            
            return {
                "assessment_id": assessment_id,
                "score": final_score,
                "compile_success": compile_success,
                "feedback": code_analysis.choices[0].message.content,
                "compile_output": result.stderr if not compile_success else "컴파일 성공"
            }
            
        except Exception as e:
            logger.error(f"코드 평가 오류: {e}")
            return {"error": str(e)}

class NotificationSystem:
    """알림 및 커뮤니케이션 시스템"""
    
    def __init__(self, smtp_config: Dict):
        self.smtp_config = smtp_config
        
    def send_progress_email(self, user_email: str, user_name: str, report: Dict):
        """진행률 리포트 이메일 발송"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = user_email
            msg['Subject'] = f"📊 {user_name}님의 주간 학습 리포트"
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; }}
                    .stat {{ background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; }}
                    .progress-bar {{ background: #e0e6ed; height: 20px; border-radius: 10px; overflow: hidden; }}
                    .progress-fill {{ background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 10px; }}
                    .footer {{ background: #333; color: white; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎓 Arduino IoT DevOps 학습 리포트</h1>
                        <p>안녕하세요, {user_name}님! 이번 주 학습 현황을 알려드립니다.</p>
                    </div>
                    
                    <div class="content">
                        <div class="stat">
                            <h3>📈 전체 진행률</h3>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {report['progress_percentage']}%"></div>
                            </div>
                            <p>{report['progress_percentage']}% 완료 (Week {report['current_week']}/12)</p>
                        </div>
                        
                        <div class="stat">
                            <h3>⏱️ 학습 시간</h3>
                            <p><strong>총 학습 시간:</strong> {report['total_hours']}시간</p>
                            <p><strong>일평균 학습:</strong> {report['avg_daily_hours']}시간</p>
                        </div>
                        
                        <div class="stat">
                            <h3>📊 최근 성과</h3>
                            <p><strong>최근 점수:</strong> {report.get('latest_score', 'N/A')}/10</p>
                            <p><strong>점수 트렌드:</strong> {report['score_trend']}</p>
                            <p><strong>완료 세션:</strong> {report['sessions_count']}개</p>
                        </div>
                        
                        {f'''
                        <div class="stat">
                            <h3>🎯 예상 완료일</h3>
                            <p>{report['estimated_completion']}</p>
                        </div>
                        ''' if report.get('estimated_completion') else ''}
                    </div>
                    
                    <div class="footer">
                        <p>계속 화이팅하세요! 💪</p>
                        <p><a href="http://localhost:8000/dashboard" style="color: #667eea;">학습 대시보드 보기</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MimeText(html_body, 'html'))
            
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
                
            logger.info(f"진행률 리포트 이메일 발송 완료: {user_email}")
            
        except Exception as e:
            logger.error(f"이메일 발송 오류: {e}")

class LearningAutomationSystem:
    """통합 학습 자동화 시스템"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db = LearningDatabase(config.get('db_path', 'data/learning.db'))
        self.ai_tutor = AITutor(config['openai_api_key'])
        self.analytics = LearningAnalytics(self.db)
        self.assessment = AutomatedAssessment(self.db, self.ai_tutor)
        self.notification = NotificationSystem(config['smtp'])
        
    async def daily_tasks(self):
        """일일 실행 작업"""
        logger.info("일일 자동화 작업 시작")
        
        try:
            # 활성 사용자 목록 조회
            conn = sqlite3.connect(self.db.db_path)
            active_users = pd.read_sql_query(
                "SELECT user_id, name, email FROM user_profiles WHERE last_active >= date('now', '-7 days')",
                conn
            )
            conn.close()
            
            for _, user in active_users.iterrows():
                try:
                    # 진행률 리포트 생성
                    report = self.analytics.generate_progress_report(user['user_id'])
                    
                    if 'error' not in report:
                        # 이메일 발송 (주 1회)
                        today = datetime.now().weekday()
                        if today == 0:  # 월요일
                            self.notification.send_progress_email(user['email'], user['name'], report)
                            
                        # AI 추천사항 생성
                        await self.generate_ai_recommendations(user['user_id'])
                        
                except Exception as e:
                    logger.error(f"사용자 {user['user_id']} 처리 오류: {e}")
                    
            logger.info("일일 자동화 작업 완료")
            
        except Exception as e:
            logger.error(f"일일 작업 오류: {e}")
    
    async def generate_ai_recommendations(self, user_id: str):
        """AI 기반 추천사항 생성"""
        try:
            # 사용자 프로필 및 세션 데이터 조회
            conn = sqlite3.connect(self.db.db_path)
            
            profile_df = pd.read_sql_query(
                "SELECT * FROM user_profiles WHERE user_id = ?",
                conn, params=[user_id]
            )
            
            sessions_df = pd.read_sql_query(
                "SELECT * FROM learning_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
                conn, params=[user_id]
            )
            
            if profile_df.empty:
                return
                
            profile_data = profile_df.iloc[0]
            user_profile = UserProfile(
                user_id=profile_data['user_id'],
                name=profile_data['name'],
                email=profile_data['email'],
                start_date=datetime.fromisoformat(profile_data['start_date']),
                current_level=profile_data['current_level'],
                current_week=profile_data['current_week'],
                current_day=profile_data['current_day'],
                total_hours=profile_data['total_hours'],
                completed_modules=json.loads(profile_data['completed_modules']),
                skill_scores=json.loads(profile_data['skill_scores'] or '{}'),
                learning_style=profile_data['learning_style'],
                preferred_pace=profile_data['preferred_pace'],
                last_active=datetime.fromisoformat(profile_data['last_active'])
            )
            
            # 세션 데이터 변환
            sessions = []
            for _, session_data in sessions_df.iterrows():
                session = LearningSession(
                    user_id=session_data['user_id'],
                    session_id=session_data['session_id'],
                    start_time=datetime.fromisoformat(session_data['start_time']),
                    end_time=datetime.fromisoformat(session_data['end_time']) if session_data['end_time'] else None,
                    module=session_data['module'],
                    week=session_data['week'],
                    day=session_data['day'],
                    tasks_completed=json.loads(session_data['tasks_completed']),
                    time_spent=session_data['time_spent'],
                    score=session_data['score'],
                    difficulty_rating=session_data['difficulty_rating'],
                    feedback=session_data['feedback']
                )
                sessions.append(session)
            
            # AI 분석 실행
            analysis = await self.ai_tutor.analyze_learning_pattern(user_profile, sessions)
            
            if 'recommendations' in analysis:
                # 추천사항을 데이터베이스에 저장
                cursor = conn.cursor()
                
                for i, recommendation in enumerate(analysis['recommendations']):
                    rec_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                    
                    cursor.execute('''
                        INSERT INTO ai_recommendations (
                            recommendation_id, user_id, recommendation_type,
                            content, priority
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        rec_id, user_id, "daily_recommendation",
                        recommendation, 1
                    ))
                
                conn.commit()
                logger.info(f"사용자 {user_id}에 대한 AI 추천사항 {len(analysis['recommendations'])}개 생성")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"AI 추천사항 생성 오류: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        logger.info("학습 자동화 스케줄러 시작")
        
        # 일일 작업 스케줄링
        schedule.every().day.at("09:00").do(lambda: asyncio.run(self.daily_tasks()))
        
        # 주간 리포트
        schedule.every().monday.at("10:00").do(lambda: asyncio.run(self.weekly_report()))
        
        # 실시간 모니터링
        schedule.every(30).minutes.do(self.health_check)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    async def weekly_report(self):
        """주간 리포트 생성"""
        logger.info("주간 리포트 생성 시작")
        # 구현 내용...
        
    def health_check(self):
        """시스템 상태 확인"""
        logger.info("시스템 상태 확인")
        # 구현 내용...

# 설정 로딩
def load_config() -> Dict:
    """설정 파일 로딩"""
    config_path = Path("config/learning_config.json")
    
    if not config_path.exists():
        # 기본 설정 생성
        default_config = {
            "openai_api_key": "your-openai-api-key",
            "db_path": "data/learning.db",
            "smtp": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password",
                "from_email": "Arduino DevOps Education <noreply@arduino-devops.com>"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/learning_automation.log"
            }
        }
        
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        logger.warning(f"기본 설정 파일이 생성되었습니다: {config_path}")
        logger.warning("설정을 수정한 후 다시 실행해주세요.")
        sys.exit(1)
    
    with open(config_path) as f:
        return json.load(f)

# CLI 인터페이스
async def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Arduino IoT DevOps 학습 자동화 시스템")
    parser.add_argument('--mode', choices=['scheduler', 'report', 'init'], default='scheduler',
                       help='실행 모드 선택')
    parser.add_argument('--user-id', help='특정 사용자에 대한 작업 실행')
    
    args = parser.parse_args()
    
    # 필요한 디렉토리 생성
    for directory in ['data', 'logs', 'config', 'temp']:
        Path(directory).mkdir(exist_ok=True)
    
    config = load_config()
    system = LearningAutomationSystem(config)
    
    if args.mode == 'init':
        logger.info("데이터베이스 초기화 완료")
        
    elif args.mode == 'report' and args.user_id:
        report = system.analytics.generate_progress_report(args.user_id)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
    elif args.mode == 'scheduler':
        logger.info("스케줄러 모드로 시작합니다...")
        try:
            system.start_scheduler()
        except KeyboardInterrupt:
            logger.info("사용자에 의해 중단되었습니다.")
    
    else:
        await system.daily_tasks()

if __name__ == "__main__":
    asyncio.run(main())