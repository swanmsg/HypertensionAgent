from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "男"
    FEMALE = "女"

class RiskLevelEnum(str, Enum):
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    VERY_HIGH = "极高风险"

class ExerciseFrequencyEnum(str, Enum):
    NEVER = "从不运动"
    RARELY = "偶尔运动"
    SOMETIMES = "有时运动"
    OFTEN = "经常运动"
    DAILY = "每日运动"

class PatientCreate(BaseModel):
    """创建患者的请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    age: int = Field(..., ge=0, le=150, description="年龄")
    gender: GenderEnum = Field(..., description="性别")
    height: Optional[float] = Field(None, ge=50, le=250, description="身高(cm)")
    weight: Optional[float] = Field(None, ge=20, le=300, description="体重(kg)")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    
    # 高血压相关信息
    systolic_bp: Optional[float] = Field(None, ge=60, le=300, description="收缩压")
    diastolic_bp: Optional[float] = Field(None, ge=40, le=200, description="舒张压")
    
    # 病史信息
    hypertension_duration: Optional[int] = Field(None, ge=0, description="高血压病程(年)")
    family_history: bool = Field(False, description="家族史")
    smoking: bool = Field(False, description="吸烟")
    drinking: bool = Field(False, description="饮酒")
    exercise_frequency: Optional[ExerciseFrequencyEnum] = Field(None, description="运动频率")
    
    # 并发症和其他疾病
    diabetes: bool = Field(False, description="糖尿病")
    heart_disease: bool = Field(False, description="心脏病")
    kidney_disease: bool = Field(False, description="肾脏疾病")
    stroke_history: bool = Field(False, description="脑卒中史")
    
    # 当前用药和过敏史
    current_medications: Optional[str] = Field(None, description="当前用药")
    allergies: Optional[str] = Field(None, description="过敏史")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('diastolic_bp')
    @classmethod
    def validate_blood_pressure(cls, v, info):
        if v is not None and info.data.get('systolic_bp') is not None:
            systolic = info.data.get('systolic_bp')
            if v >= systolic:
                raise ValueError('舒张压不能大于等于收缩压')
        return v

class PatientUpdate(BaseModel):
    """更新患者信息的请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    height: Optional[float] = Field(None, ge=50, le=250)
    weight: Optional[float] = Field(None, ge=20, le=300)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    
    systolic_bp: Optional[float] = Field(None, ge=60, le=300)
    diastolic_bp: Optional[float] = Field(None, ge=40, le=200)
    
    hypertension_duration: Optional[int] = Field(None, ge=0)
    family_history: Optional[bool] = None
    smoking: Optional[bool] = None
    drinking: Optional[bool] = None
    exercise_frequency: Optional[ExerciseFrequencyEnum] = None
    
    diabetes: Optional[bool] = None
    heart_disease: Optional[bool] = None
    kidney_disease: Optional[bool] = None
    stroke_history: Optional[bool] = None
    
    current_medications: Optional[str] = None
    allergies: Optional[str] = None

class PatientResponse(BaseModel):
    """患者信息响应模型"""
    id: int
    name: str
    age: int
    gender: str
    height: Optional[float]
    weight: Optional[float]
    phone: Optional[str]
    email: Optional[str]
    
    systolic_bp: Optional[float]
    diastolic_bp: Optional[float]
    bp_measurement_time: Optional[datetime]
    
    hypertension_duration: Optional[int]
    family_history: bool
    smoking: bool
    drinking: bool
    exercise_frequency: Optional[str]
    
    diabetes: bool
    heart_disease: bool
    kidney_disease: bool
    stroke_history: bool
    
    current_medications: Optional[str]
    allergies: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class BloodPressureRecordCreate(BaseModel):
    """血压记录创建模型"""
    patient_id: int = Field(..., description="患者ID")
    systolic_bp: float = Field(..., ge=60, le=300, description="收缩压")
    diastolic_bp: float = Field(..., ge=40, le=200, description="舒张压")
    heart_rate: Optional[int] = Field(None, ge=30, le=200, description="心率")
    measurement_time: datetime = Field(..., description="测量时间")
    measurement_location: Optional[str] = Field(None, max_length=50, description="测量位置")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator('diastolic_bp')
    @classmethod
    def validate_diastolic_bp(cls, v, info):
        if info.data.get('systolic_bp') is not None and v >= info.data.get('systolic_bp'):
            raise ValueError('舒张压不能大于等于收缩压')
        return v

class BloodPressureRecordResponse(BaseModel):
    """血压记录响应模型"""
    id: int
    patient_id: int
    systolic_bp: float
    diastolic_bp: float
    heart_rate: Optional[int]
    measurement_time: datetime
    measurement_location: Optional[str]
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MedicalAdviceCreate(BaseModel):
    """医疗建议创建模型"""
    patient_id: int = Field(..., description="患者ID")
    advice_type: str = Field(..., max_length=50, description="建议类型")
    content: str = Field(..., description="建议内容")
    risk_level: Optional[RiskLevelEnum] = Field(None, description="风险等级")
    ai_confidence: Optional[float] = Field(None, ge=0, le=1, description="AI置信度")

class MedicalAdviceResponse(BaseModel):
    """医疗建议响应模型"""
    id: int
    patient_id: int
    advice_type: str
    content: str
    risk_level: Optional[str]
    ai_confidence: Optional[float]
    doctor_review: bool
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class PatientSummary(BaseModel):
    """患者摘要信息"""
    basic_info: PatientResponse
    latest_bp: Optional[BloodPressureRecordResponse]
    recent_advice: List[MedicalAdviceResponse]
    bmi: Optional[float]
    risk_level: Optional[str]