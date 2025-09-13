from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Patient(Base):
    """患者信息模型"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="姓名")
    age = Column(Integer, nullable=False, comment="年龄")
    gender = Column(String(10), nullable=False, comment="性别")
    height = Column(Float, comment="身高(cm)")
    weight = Column(Float, comment="体重(kg)")
    phone = Column(String(20), comment="电话")
    email = Column(String(100), comment="邮箱")
    
    # 高血压相关信息
    systolic_bp = Column(Float, comment="收缩压")
    diastolic_bp = Column(Float, comment="舒张压")
    bp_measurement_time = Column(DateTime, comment="血压测量时间")
    
    # 病史信息
    hypertension_duration = Column(Integer, comment="高血压病程(年)")
    family_history = Column(Boolean, default=False, comment="家族史")
    smoking = Column(Boolean, default=False, comment="吸烟")
    drinking = Column(Boolean, default=False, comment="饮酒")
    exercise_frequency = Column(String(50), comment="运动频率")
    
    # 并发症和其他疾病
    diabetes = Column(Boolean, default=False, comment="糖尿病")
    heart_disease = Column(Boolean, default=False, comment="心脏病")
    kidney_disease = Column(Boolean, default=False, comment="肾脏疾病")
    stroke_history = Column(Boolean, default=False, comment="脑卒中史")
    
    # 当前用药
    current_medications = Column(Text, comment="当前用药")
    allergies = Column(Text, comment="过敏史")
    
    # 系统字段
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), comment="更新时间")
    is_active = Column(Boolean, default=True, comment="是否活跃")

class BloodPressureRecord(Base):
    """血压记录模型"""
    __tablename__ = "blood_pressure_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, comment="患者ID")
    systolic_bp = Column(Float, nullable=False, comment="收缩压")
    diastolic_bp = Column(Float, nullable=False, comment="舒张压")
    heart_rate = Column(Integer, comment="心率")
    measurement_time = Column(DateTime, nullable=False, comment="测量时间")
    measurement_location = Column(String(50), comment="测量位置")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")

class MedicalAdvice(Base):
    """医疗建议模型"""
    __tablename__ = "medical_advice"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, comment="患者ID")
    advice_type = Column(String(50), nullable=False, comment="建议类型")
    content = Column(Text, nullable=False, comment="建议内容")
    risk_level = Column(String(20), comment="风险等级")
    ai_confidence = Column(Float, comment="AI置信度")
    doctor_review = Column(Boolean, default=False, comment="医生审核")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), comment="创建时间")
    is_active = Column(Boolean, default=True, comment="是否有效")

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hypertension_agent.db")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()