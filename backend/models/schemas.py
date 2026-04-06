from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    cognitive_mode = Column(String, default="visual")
    created_at = Column(DateTime, default=datetime.utcnow)


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)

    level = Column(String)  # beginner / intermediate / advanced
    progress = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)

    chroma_collection = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    questions = Column(JSON)
    responses = Column(JSON)

    score = Column(Float)
    level_assigned = Column(String)
    shap_values = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    messages = Column(JSON)
    cognitive_mode = Column(String)

    attention_scores = Column(JSON)
    drift_events = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)