"""
患者服务测试
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Base, Patient, BloodPressureRecord, MedicalAdvice
from app.models.schemas import PatientCreate, PatientUpdate, BloodPressureRecordCreate, MedicalAdviceCreate
from app.services.patient_service import PatientService, BloodPressureService, MedicalAdviceService

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_hypertension_agent.db"
test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=test_engine)
    
    # 创建会话
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理表
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def sample_patient_data():
    """示例患者数据"""
    return PatientCreate(
        name="测试患者",
        age=50,
        gender="男",
        height=170.0,
        weight=70.0,
        phone="13800138000",
        email="test@example.com",
        systolic_bp=140.0,
        diastolic_bp=90.0,
        hypertension_duration=2,
        family_history=True,
        smoking=False,
        diabetes=False,
        heart_disease=False,
        kidney_disease=False,
        stroke_history=False,
        exercise_frequency="有时运动"
    )

class TestPatientService:
    """患者服务测试类"""
    
    def test_create_patient(self, test_db, sample_patient_data):
        """测试创建患者"""
        service = PatientService(test_db)
        patient = service.create_patient(sample_patient_data)
        
        assert patient.id is not None
        assert patient.name == "测试患者"
        assert patient.age == 50
        assert patient.gender == "男"
        assert patient.is_active == True
    
    def test_get_patient(self, test_db, sample_patient_data):
        """测试获取患者"""
        service = PatientService(test_db)
        created_patient = service.create_patient(sample_patient_data)
        
        retrieved_patient = service.get_patient(created_patient.id)
        assert retrieved_patient is not None
        assert retrieved_patient.id == created_patient.id
        assert retrieved_patient.name == "测试患者"
    
    def test_get_nonexistent_patient(self, test_db):
        """测试获取不存在的患者"""
        service = PatientService(test_db)
        patient = service.get_patient(999)
        assert patient is None
    
    def test_update_patient(self, test_db, sample_patient_data):
        """测试更新患者信息"""
        service = PatientService(test_db)
        patient = service.create_patient(sample_patient_data)
        
        update_data = PatientUpdate(
            age=51,
            systolic_bp=135.0,
            diastolic_bp=85.0
        )
        
        updated_patient = service.update_patient(patient.id, update_data)
        assert updated_patient.age == 51
        assert updated_patient.systolic_bp == 135.0
        assert updated_patient.diastolic_bp == 85.0
    
    def test_delete_patient(self, test_db, sample_patient_data):
        """测试删除患者（软删除）"""
        service = PatientService(test_db)
        patient = service.create_patient(sample_patient_data)
        
        success = service.delete_patient(patient.id)
        assert success == True
        
        # 验证软删除
        deleted_patient = test_db.query(Patient).filter(Patient.id == patient.id).first()
        assert deleted_patient.is_active == False
    
    def test_calculate_bmi(self, test_db, sample_patient_data):
        """测试BMI计算"""
        service = PatientService(test_db)
        patient = service.create_patient(sample_patient_data)
        
        bmi = service.calculate_bmi(patient)
        expected_bmi = 70 / (1.7 ** 2)  # 24.22
        assert abs(bmi - expected_bmi) < 0.01
    
    def test_assess_bp_risk(self, test_db):
        """测试血压风险评估"""
        service = PatientService(test_db)
        
        # 正常血压
        risk = service.assess_bp_risk(110, 70)
        assert risk == "正常"
        
        # 1级高血压
        risk = service.assess_bp_risk(150, 95)
        assert risk == "1级高血压"
        
        # 3级高血压
        risk = service.assess_bp_risk(190, 120)
        assert risk == "3级高血压"

class TestBloodPressureService:
    """血压服务测试类"""
    
    def test_create_record(self, test_db, sample_patient_data):
        """测试创建血压记录"""
        # 先创建患者
        patient_service = PatientService(test_db)
        patient = patient_service.create_patient(sample_patient_data)
        
        # 创建血压记录
        bp_service = BloodPressureService(test_db)
        bp_data = BloodPressureRecordCreate(
            patient_id=patient.id,
            systolic_bp=140.0,
            diastolic_bp=90.0,
            heart_rate=75,
            measurement_time=datetime.now(),
            measurement_location="左臂",
            notes="测试记录"
        )
        
        record = bp_service.create_record(bp_data)
        assert record.id is not None
        assert record.patient_id == patient.id
        assert record.systolic_bp == 140.0
        assert record.diastolic_bp == 90.0
    
    def test_get_patient_records(self, test_db, sample_patient_data):
        """测试获取患者血压记录"""
        # 创建患者和血压记录
        patient_service = PatientService(test_db)
        patient = patient_service.create_patient(sample_patient_data)
        
        bp_service = BloodPressureService(test_db)
        
        # 创建多条记录
        for i in range(5):
            bp_data = BloodPressureRecordCreate(
                patient_id=patient.id,
                systolic_bp=140.0 + i,
                diastolic_bp=90.0 + i,
                heart_rate=75,
                measurement_time=datetime.now() - timedelta(days=i),
                measurement_location="左臂"
            )
            bp_service.create_record(bp_data)
        
        # 获取记录
        records = bp_service.get_patient_records(patient.id, days=30)
        assert len(records) == 5
    
    def test_get_bp_statistics(self, test_db, sample_patient_data):
        """测试血压统计"""
        # 创建患者和血压记录
        patient_service = PatientService(test_db)
        patient = patient_service.create_patient(sample_patient_data)
        
        bp_service = BloodPressureService(test_db)
        
        # 创建测试数据
        bp_values = [(140, 90), (145, 95), (135, 85)]
        for systolic, diastolic in bp_values:
            bp_data = BloodPressureRecordCreate(
                patient_id=patient.id,
                systolic_bp=systolic,
                diastolic_bp=diastolic,
                heart_rate=75,
                measurement_time=datetime.now(),
                measurement_location="左臂"
            )
            bp_service.create_record(bp_data)
        
        # 获取统计
        stats = bp_service.get_bp_statistics(patient.id, days=30)
        assert stats['count'] == 3
        assert stats['systolic']['avg'] == 140.0  # (140+145+135)/3
        assert stats['diastolic']['avg'] == 90.0  # (90+95+85)/3

class TestMedicalAdviceService:
    """医疗建议服务测试类"""
    
    def test_create_advice(self, test_db, sample_patient_data):
        """测试创建医疗建议"""
        # 创建患者
        patient_service = PatientService(test_db)
        patient = patient_service.create_patient(sample_patient_data)
        
        # 创建医疗建议
        advice_service = MedicalAdviceService(test_db)
        advice_data = MedicalAdviceCreate(
            patient_id=patient.id,
            advice_type="生活方式建议",
            content="建议低盐饮食，每日食盐摄入量少于6g",
            risk_level="中风险",
            ai_confidence=0.85
        )
        
        advice = advice_service.create_advice(advice_data)
        assert advice.id is not None
        assert advice.patient_id == patient.id
        assert advice.advice_type == "生活方式建议"
        assert advice.is_active == True
    
    def test_get_patient_advice(self, test_db, sample_patient_data):
        """测试获取患者医疗建议"""
        # 创建患者
        patient_service = PatientService(test_db)
        patient = patient_service.create_patient(sample_patient_data)
        
        # 创建多条建议
        advice_service = MedicalAdviceService(test_db)
        for i in range(3):
            advice_data = MedicalAdviceCreate(
                patient_id=patient.id,
                advice_type=f"建议类型{i+1}",
                content=f"建议内容{i+1}",
                risk_level="中风险"
            )
            advice_service.create_advice(advice_data)
        
        # 获取建议
        advice_list = advice_service.get_patient_advice(patient.id)
        assert len(advice_list) == 3
    
    def test_deactivate_advice(self, test_db, sample_patient_data):
        """测试停用医疗建议"""
        # 创建患者和建议
        patient_service = PatientService(test_db)
        patient = patient_service.create_patient(sample_patient_data)
        
        advice_service = MedicalAdviceService(test_db)
        advice_data = MedicalAdviceCreate(
            patient_id=patient.id,
            advice_type="测试建议",
            content="测试内容",
            risk_level="低风险"
        )
        
        advice = advice_service.create_advice(advice_data)
        
        # 停用建议
        success = advice_service.deactivate_advice(advice.id)
        assert success == True
        
        # 验证停用
        updated_advice = advice_service.get_advice(advice.id)
        assert updated_advice.is_active == False

def test_input_validation():
    """测试输入验证"""
    from pydantic import ValidationError
    
    # 测试无效的血压值
    with pytest.raises(ValidationError):
        PatientCreate(
            name="测试",
            age=50,
            gender="男",
            systolic_bp=50,  # 无效值
            diastolic_bp=90
        )
    
    # 测试无效的年龄
    with pytest.raises(ValidationError):
        PatientCreate(
            name="测试",
            age=-5,  # 无效年龄
            gender="男"
        )

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])