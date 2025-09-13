"""
FastAPI主应用程序
高血压患者医嘱智能体平台后端API
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv

from app.models import (
    create_tables, get_db,
    PatientCreate, PatientUpdate, PatientResponse, PatientSummary,
    BloodPressureRecordCreate, BloodPressureRecordResponse,
    MedicalAdviceCreate, MedicalAdviceResponse
)
from app.services.patient_service import PatientService, BloodPressureService, MedicalAdviceService
from app.services.ai_agent import get_hypertension_agent
from app.utils.helpers import validate_blood_pressure, format_medical_advice

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="高血压患者医嘱智能体平台",
    description="基于LangChain的智能医疗咨询平台API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库初始化
@app.on_event("startup")
async def startup_event():
    """应用启动时创建数据库表"""
    create_tables()
    print("数据库表创建完成")

# 健康检查接口
@app.get("/", tags=["健康检查"])
async def health_check():
    """健康检查"""
    return {"message": "高血压患者医嘱智能体平台API正常运行", "status": "healthy"}

# 患者管理接口
@app.post("/patients/", response_model=PatientResponse, tags=["患者管理"])
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """创建新患者"""
    try:
        service = PatientService(db)
        new_patient = service.create_patient(patient)
        return PatientResponse.model_validate(new_patient)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patients/{patient_id}", response_model=PatientResponse, tags=["患者管理"])
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """获取患者信息"""
    service = PatientService(db)
    patient = service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return PatientResponse.model_validate(patient)

@app.get("/patients/", response_model=List[PatientResponse], tags=["患者管理"])
async def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取患者列表"""
    service = PatientService(db)
    patients = service.get_patients(skip=skip, limit=limit)
    return [PatientResponse.model_validate(p) for p in patients]

@app.put("/patients/{patient_id}", response_model=PatientResponse, tags=["患者管理"])
async def update_patient(patient_id: int, patient_update: PatientUpdate, db: Session = Depends(get_db)):
    """更新患者信息"""
    service = PatientService(db)
    updated_patient = service.update_patient(patient_id, patient_update)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return PatientResponse.model_validate(updated_patient)

@app.delete("/patients/{patient_id}", tags=["患者管理"])
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """删除患者"""
    service = PatientService(db)
    success = service.delete_patient(patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="患者不存在")
    return {"message": "患者删除成功"}

@app.get("/patients/{patient_id}/summary", response_model=PatientSummary, tags=["患者管理"])
async def get_patient_summary(patient_id: int, db: Session = Depends(get_db)):
    """获取患者摘要信息"""
    service = PatientService(db)
    summary = service.get_patient_summary(patient_id)
    if not summary:
        raise HTTPException(status_code=404, detail="患者不存在")
    return summary

# 血压记录接口
@app.post("/blood-pressure/", response_model=BloodPressureRecordResponse, tags=["血压管理"])
async def create_blood_pressure_record(record: BloodPressureRecordCreate, db: Session = Depends(get_db)):
    """创建血压记录"""
    try:
        # 验证血压值
        if not validate_blood_pressure(record.systolic_bp, record.diastolic_bp):
            raise HTTPException(status_code=400, detail="血压值不合理")
        
        service = BloodPressureService(db)
        new_record = service.create_record(record)
        return BloodPressureRecordResponse.model_validate(new_record)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/blood-pressure/patient/{patient_id}", response_model=List[BloodPressureRecordResponse], tags=["血压管理"])
async def get_patient_blood_pressure_records(patient_id: int, days: int = 30, db: Session = Depends(get_db)):
    """获取患者血压记录"""
    service = BloodPressureService(db)
    records = service.get_patient_records(patient_id, days)
    return [BloodPressureRecordResponse.model_validate(r) for r in records]

@app.get("/blood-pressure/patient/{patient_id}/statistics", tags=["血压管理"])
async def get_blood_pressure_statistics(patient_id: int, days: int = 30, db: Session = Depends(get_db)):
    """获取血压统计信息"""
    service = BloodPressureService(db)
    stats = service.get_bp_statistics(patient_id, days)
    return stats

# 医疗建议接口
@app.post("/medical-advice/", response_model=MedicalAdviceResponse, tags=["医疗建议"])
async def create_medical_advice(advice: MedicalAdviceCreate, db: Session = Depends(get_db)):
    """创建医疗建议"""
    try:
        service = MedicalAdviceService(db)
        new_advice = service.create_advice(advice)
        return MedicalAdviceResponse.model_validate(new_advice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/medical-advice/patient/{patient_id}", response_model=List[MedicalAdviceResponse], tags=["医疗建议"])
async def get_patient_medical_advice(patient_id: int, active_only: bool = True, db: Session = Depends(get_db)):
    """获取患者医疗建议"""
    service = MedicalAdviceService(db)
    advice_list = service.get_patient_advice(patient_id, active_only)
    return [MedicalAdviceResponse.model_validate(a) for a in advice_list]

# AI智能体接口
@app.get("/ai/model-info", tags=["AI智能体"])
async def get_model_info():
    """获取当前使用的AI模型信息"""
    try:
        agent = get_hypertension_agent()
        model_info = agent.get_model_info()
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/analyze-blood-pressure", tags=["AI智能体"])
async def analyze_blood_pressure(systolic: float, diastolic: float):
    """分析血压"""
    if not validate_blood_pressure(systolic, diastolic):
        raise HTTPException(status_code=400, detail="血压值不合理")
    
    try:
        result = get_hypertension_agent().analyze_blood_pressure(systolic, diastolic)
        
        # 检查是否为急症
        emergency = get_hypertension_agent().emergency_check(systolic, diastolic)
        result.update(emergency)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate-advice", tags=["AI智能体"])
async def generate_medical_advice(patient_data: dict, db: Session = Depends(get_db)):
    """生成医疗建议"""
    try:
        # 生成AI建议
        advice_text = get_hypertension_agent().generate_medical_advice(patient_data)
        
        # 如果有patient_id，保存建议到数据库
        if "patient_id" in patient_data:
            service = MedicalAdviceService(db)
            advice_create = MedicalAdviceCreate(
                patient_id=patient_data["patient_id"],
                advice_type="AI生成医疗建议",
                content=advice_text,
                ai_confidence=0.85
            )
            service.create_advice(advice_create)
        
        return {"advice": advice_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/chat", tags=["AI智能体"])
async def chat_with_ai(message: str, patient_context: Optional[dict] = None):
    """与AI对话"""
    try:
        response = get_hypertension_agent().chat(message, patient_context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/medication-advice", tags=["AI智能体"])
async def get_medication_advice(patient_data: dict):
    """获取药物建议"""
    try:
        advice = get_hypertension_agent().get_medication_advice(patient_data)
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/conversation-history", tags=["AI智能体"])
async def get_conversation_history():
    """获取对话历史"""
    try:
        history = get_hypertension_agent().get_conversation_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/clear-memory", tags=["AI智能体"])
async def clear_ai_memory():
    """清除AI对话记忆"""
    try:
        get_hypertension_agent().clear_memory()
        return {"message": "对话记忆已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 知识库接口
@app.get("/knowledge/search", tags=["知识库"])
async def search_knowledge(query: str):
    """搜索医学知识"""
    try:
        from app.services.knowledge_service import knowledge_base
        result = knowledge_base.search_knowledge(query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/blood-pressure-classification", tags=["知识库"])
async def get_bp_classification():
    """获取血压分类信息"""
    try:
        from app.services.knowledge_service import knowledge_base
        info = knowledge_base.get_bp_classification_info()
        return {"info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/medication/{drug_type}", tags=["知识库"])
async def get_medication_info(drug_type: str):
    """获取药物信息"""
    try:
        from app.services.knowledge_service import knowledge_base
        info = knowledge_base.get_medication_info(drug_type)
        return {"info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"message": f"服务器内部错误: {str(exc)}"}
    )

if __name__ == "__main__":
    # 运行应用
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )