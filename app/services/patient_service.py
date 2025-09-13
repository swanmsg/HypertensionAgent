from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, UTC
from app.models.database import Patient, BloodPressureRecord, MedicalAdvice
from app.models.schemas import (
    PatientCreate, PatientUpdate, PatientResponse, PatientSummary,
    BloodPressureRecordCreate, MedicalAdviceCreate
)

class PatientService:
    """患者信息管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: PatientCreate) -> Patient:
        """创建新患者"""
        patient = Patient(**patient_data.model_dump())
        if patient_data.systolic_bp and patient_data.diastolic_bp:
            patient.bp_measurement_time = datetime.now(UTC)
        
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def get_patient(self, patient_id: int) -> Optional[Patient]:
        """获取患者信息"""
        return self.db.query(Patient).filter(
            Patient.id == patient_id, 
            Patient.is_active == True
        ).first()
    
    def get_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """获取患者列表"""
        return self.db.query(Patient).filter(
            Patient.is_active == True
        ).offset(skip).limit(limit).all()
    
    def update_patient(self, patient_id: int, patient_data: PatientUpdate) -> Optional[Patient]:
        """更新患者信息"""
        patient = self.get_patient(patient_id)
        if not patient:
            return None
        
        update_data = patient_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        # 如果更新了血压信息，更新测量时间
        if 'systolic_bp' in update_data or 'diastolic_bp' in update_data:
            patient.bp_measurement_time = datetime.now(UTC)
        
        patient.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def delete_patient(self, patient_id: int) -> bool:
        """删除患者（软删除）"""
        patient = self.get_patient(patient_id)
        if not patient:
            return False
        
        patient.is_active = False
        patient.updated_at = datetime.now(UTC)
        self.db.commit()
        return True
    
    def search_patients(self, query: str) -> List[Patient]:
        """搜索患者"""
        return self.db.query(Patient).filter(
            Patient.is_active == True,
            Patient.name.contains(query)
        ).all()
    
    def calculate_bmi(self, patient: Patient) -> Optional[float]:
        """计算BMI"""
        if patient.height and patient.weight:
            height_m = patient.height / 100
            return round(patient.weight / (height_m ** 2), 2)
        return None
    
    def assess_bp_risk(self, systolic: float, diastolic: float) -> str:
        """评估血压风险等级"""
        if systolic < 120 and diastolic < 80:
            return "正常"
        elif systolic < 130 and diastolic < 80:
            return "正常高值"
        elif (130 <= systolic < 140) or (80 <= diastolic < 90):
            return "正常高值"
        elif (140 <= systolic < 160) or (90 <= diastolic < 100):
            return "1级高血压"
        elif (160 <= systolic < 180) or (100 <= diastolic < 110):
            return "2级高血压"
        else:
            return "3级高血压"
    
    def get_patient_summary(self, patient_id: int) -> Optional[PatientSummary]:
        """获取患者摘要信息"""
        patient = self.get_patient(patient_id)
        if not patient:
            return None
        
        # 获取最新血压记录
        latest_bp = self.db.query(BloodPressureRecord).filter(
            BloodPressureRecord.patient_id == patient_id
        ).order_by(BloodPressureRecord.measurement_time.desc()).first()
        
        # 获取最近的医疗建议
        recent_advice = self.db.query(MedicalAdvice).filter(
            MedicalAdvice.patient_id == patient_id,
            MedicalAdvice.is_active == True
        ).order_by(MedicalAdvice.created_at.desc()).limit(5).all()
        
        # 计算BMI
        bmi = self.calculate_bmi(patient)
        
        # 评估风险等级
        risk_level = None
        if patient.systolic_bp and patient.diastolic_bp:
            risk_level = self.assess_bp_risk(patient.systolic_bp, patient.diastolic_bp)
        
        return PatientSummary(
            basic_info=PatientResponse.from_orm(patient),
            latest_bp=latest_bp,
            recent_advice=recent_advice,
            bmi=bmi,
            risk_level=risk_level
        )

class BloodPressureService:
    """血压记录管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_record(self, record_data: BloodPressureRecordCreate) -> BloodPressureRecord:
        """创建血压记录"""
        record = BloodPressureRecord(**record_data.model_dump())
        self.db.add(record)
        
        # 更新患者的最新血压信息
        patient = self.db.query(Patient).filter(Patient.id == record_data.patient_id).first()
        if patient:
            patient.systolic_bp = record_data.systolic_bp
            patient.diastolic_bp = record_data.diastolic_bp
            patient.bp_measurement_time = record_data.measurement_time
            patient.updated_at = datetime.now(UTC)
        
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_patient_records(self, patient_id: int, days: int = 30) -> List[BloodPressureRecord]:
        """获取患者的血压记录"""
        start_date = datetime.now(UTC) - timedelta(days=days)
        return self.db.query(BloodPressureRecord).filter(
            BloodPressureRecord.patient_id == patient_id,
            BloodPressureRecord.measurement_time >= start_date
        ).order_by(BloodPressureRecord.measurement_time.desc()).all()
    
    def get_record(self, record_id: int) -> Optional[BloodPressureRecord]:
        """获取血压记录"""
        return self.db.query(BloodPressureRecord).filter(
            BloodPressureRecord.id == record_id
        ).first()
    
    def delete_record(self, record_id: int) -> bool:
        """删除血压记录"""
        record = self.get_record(record_id)
        if not record:
            return False
        
        self.db.delete(record)
        self.db.commit()
        return True
    
    def get_bp_statistics(self, patient_id: int, days: int = 30) -> dict:
        """获取血压统计信息"""
        records = self.get_patient_records(patient_id, days)
        if not records:
            return {}
        
        systolic_values = [r.systolic_bp for r in records]
        diastolic_values = [r.diastolic_bp for r in records]
        
        return {
            "count": len(records),
            "systolic": {
                "avg": round(sum(systolic_values) / len(systolic_values), 1),
                "max": max(systolic_values),
                "min": min(systolic_values)
            },
            "diastolic": {
                "avg": round(sum(diastolic_values) / len(diastolic_values), 1),
                "max": max(diastolic_values),
                "min": min(diastolic_values)
            },
            "period_days": days
        }

class MedicalAdviceService:
    """医疗建议管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_advice(self, advice_data: MedicalAdviceCreate) -> MedicalAdvice:
        """创建医疗建议"""
        advice = MedicalAdvice(**advice_data.model_dump())
        self.db.add(advice)
        self.db.commit()
        self.db.refresh(advice)
        return advice
    
    def get_patient_advice(self, patient_id: int, active_only: bool = True) -> List[MedicalAdvice]:
        """获取患者的医疗建议"""
        query = self.db.query(MedicalAdvice).filter(
            MedicalAdvice.patient_id == patient_id
        )
        if active_only:
            query = query.filter(MedicalAdvice.is_active == True)
        
        return query.order_by(MedicalAdvice.created_at.desc()).all()
    
    def get_advice(self, advice_id: int) -> Optional[MedicalAdvice]:
        """获取医疗建议"""
        return self.db.query(MedicalAdvice).filter(
            MedicalAdvice.id == advice_id
        ).first()
    
    def update_advice(self, advice_id: int, **kwargs) -> Optional[MedicalAdvice]:
        """更新医疗建议"""
        advice = self.get_advice(advice_id)
        if not advice:
            return None
        
        for field, value in kwargs.items():
            if hasattr(advice, field):
                setattr(advice, field, value)
        
        self.db.commit()
        self.db.refresh(advice)
        return advice
    
    def deactivate_advice(self, advice_id: int) -> bool:
        """停用医疗建议"""
        advice = self.get_advice(advice_id)
        if not advice:
            return False
        
        advice.is_active = False
        self.db.commit()
        return True