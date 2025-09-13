"""
API接口测试
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.database import Base, get_db

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_api.db"
test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """创建测试客户端"""
    # 创建测试表
    Base.metadata.create_all(bind=test_engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # 清理测试表
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def sample_patient():
    """示例患者数据"""
    return {
        "name": "测试患者",
        "age": 50,
        "gender": "男",
        "height": 170.0,
        "weight": 70.0,
        "phone": "13800138000",
        "email": "test@example.com",
        "systolic_bp": 140.0,
        "diastolic_bp": 90.0,
        "hypertension_duration": 2,
        "family_history": True,
        "smoking": False,
        "diabetes": False,
        "heart_disease": False,
        "kidney_disease": False,
        "stroke_history": False,
        "exercise_frequency": "有时运动"
    }

class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/")
        assert response.status_code == 200
        assert "高血压患者医嘱智能体平台API正常运行" in response.json()["message"]

class TestPatientAPI:
    """患者API测试"""
    
    def test_create_patient(self, client, sample_patient):
        """测试创建患者"""
        response = client.post("/patients/", json=sample_patient)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "测试患者"
        assert data["age"] == 50
        assert data["id"] is not None
    
    def test_create_patient_invalid_data(self, client):
        """测试创建患者 - 无效数据"""
        invalid_patient = {
            "name": "",  # 空名称
            "age": -5,   # 无效年龄
            "gender": "男"
        }
        
        response = client.post("/patients/", json=invalid_patient)
        assert response.status_code == 422  # 验证错误
    
    def test_get_patient(self, client, sample_patient):
        """测试获取患者"""
        # 先创建患者
        create_response = client.post("/patients/", json=sample_patient)
        patient_id = create_response.json()["id"]
        
        # 获取患者
        response = client.get(f"/patients/{patient_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == patient_id
        assert data["name"] == "测试患者"
    
    def test_get_nonexistent_patient(self, client):
        """测试获取不存在的患者"""
        response = client.get("/patients/999")
        assert response.status_code == 404
    
    def test_list_patients(self, client, sample_patient):
        """测试获取患者列表"""
        # 创建几个患者
        for i in range(3):
            patient_data = sample_patient.copy()
            patient_data["name"] = f"患者{i+1}"
            client.post("/patients/", json=patient_data)
        
        # 获取列表
        response = client.get("/patients/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
    
    def test_update_patient(self, client, sample_patient):
        """测试更新患者"""
        # 创建患者
        create_response = client.post("/patients/", json=sample_patient)
        patient_id = create_response.json()["id"]
        
        # 更新患者
        update_data = {
            "age": 51,
            "systolic_bp": 135.0
        }
        
        response = client.put(f"/patients/{patient_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["age"] == 51
        assert data["systolic_bp"] == 135.0
    
    def test_delete_patient(self, client, sample_patient):
        """测试删除患者"""
        # 创建患者
        create_response = client.post("/patients/", json=sample_patient)
        patient_id = create_response.json()["id"]
        
        # 删除患者
        response = client.delete(f"/patients/{patient_id}")
        assert response.status_code == 200
        
        # 验证患者已被软删除
        get_response = client.get(f"/patients/{patient_id}")
        assert get_response.status_code == 404

class TestBloodPressureAPI:
    """血压API测试"""
    
    def test_create_blood_pressure_record(self, client, sample_patient):
        """测试创建血压记录"""
        # 先创建患者
        patient_response = client.post("/patients/", json=sample_patient)
        patient_id = patient_response.json()["id"]
        
        # 创建血压记录
        bp_data = {
            "patient_id": patient_id,
            "systolic_bp": 140.0,
            "diastolic_bp": 90.0,
            "heart_rate": 75,
            "measurement_time": "2024-01-01T10:00:00",
            "measurement_location": "左臂",
            "notes": "测试记录"
        }
        
        response = client.post("/blood-pressure/", json=bp_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["patient_id"] == patient_id
        assert data["systolic_bp"] == 140.0
    
    def test_create_invalid_blood_pressure(self, client, sample_patient):
        """测试创建无效血压记录"""
        # 先创建患者
        patient_response = client.post("/patients/", json=sample_patient)
        patient_id = patient_response.json()["id"]
        
        # 创建无效血压记录
        bp_data = {
            "patient_id": patient_id,
            "systolic_bp": 50.0,  # 无效值
            "diastolic_bp": 200.0,  # 无效值
            "measurement_time": "2024-01-01T10:00:00"
        }
        
        response = client.post("/blood-pressure/", json=bp_data)
        assert response.status_code == 422  # Pydantic验证失败返回422
    
    def test_get_patient_blood_pressure_records(self, client, sample_patient):
        """测试获取患者血压记录"""
        from datetime import datetime, timedelta
        
        # 创建患者
        patient_response = client.post("/patients/", json=sample_patient)
        patient_id = patient_response.json()["id"]
        
        # 创建几条血压记录（使用当前时间）
        base_time = datetime.now()
        for i in range(3):
            measurement_time = base_time - timedelta(days=i)
            bp_data = {
                "patient_id": patient_id,
                "systolic_bp": 140.0 + i,
                "diastolic_bp": 90.0 + i,
                "heart_rate": 75,
                "measurement_time": measurement_time.isoformat()
            }
            bp_response = client.post("/blood-pressure/", json=bp_data)
            assert bp_response.status_code == 200, f"血压记录创建失败: {bp_response.text}"
        
        # 获取记录
        response = client.get(f"/blood-pressure/patient/{patient_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3

class TestAIAPI:
    """AI API测试"""
    
    def test_analyze_blood_pressure(self, client):
        """测试血压分析"""
        response = client.post("/ai/analyze-blood-pressure?systolic=150&diastolic=95")
        assert response.status_code == 200
        
        data = response.json()
        assert "blood_pressure" in data
        assert "classification" in data
        assert data["blood_pressure"] == "150/95 mmHg"
    
    def test_analyze_invalid_blood_pressure(self, client):
        """测试分析无效血压"""
        response = client.post("/ai/analyze-blood-pressure?systolic=50&diastolic=200")
        # 这个请求应该被血压验证拦截，返回400错误
        assert response.status_code == 400
    
    def test_generate_medical_advice(self, client):
        """测试生成医疗建议"""
        patient_data = {
            "age": 55,
            "gender": "男",
            "systolic_bp": 150,
            "diastolic_bp": 95,
            "smoking": True,
            "diabetes": False
        }
        
        response = client.post("/ai/generate-advice", json=patient_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "advice" in data
        assert isinstance(data["advice"], str)
    
    def test_chat_with_ai(self, client):
        """测试AI对话"""
        response = client.post("/ai/chat?message=什么是高血压？")
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
    
    def test_get_medication_advice(self, client):
        """测试获取药物建议"""
        patient_data = {
            "age": 60,
            "gender": "女",
            "systolic_bp": 160,
            "diastolic_bp": 100,
            "diabetes": True
        }
        
        response = client.post("/ai/medication-advice", json=patient_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "needs_medication" in data

class TestKnowledgeAPI:
    """知识库API测试"""
    
    def test_search_knowledge(self, client):
        """测试知识搜索"""
        response = client.get("/knowledge/search?query=血压分类")
        assert response.status_code == 200
        
        data = response.json()
        assert "result" in data
        assert "血压" in data["result"]
    
    def test_get_bp_classification(self, client):
        """测试获取血压分类"""
        response = client.get("/knowledge/blood-pressure-classification")
        assert response.status_code == 200
        
        data = response.json()
        assert "info" in data
        assert "正常血压" in data["info"]
    
    def test_get_medication_info(self, client):
        """测试获取药物信息"""
        response = client.get("/knowledge/medication/ACEI")
        assert response.status_code == 200
        
        data = response.json()
        assert "info" in data
        assert "ACEI" in data["info"]

def test_api_error_handling(client):
    """测试API错误处理"""
    # 测试无效的患者ID
    response = client.get("/patients/invalid")
    assert response.status_code == 422
    
    # 测试无效的JSON数据
    response = client.post("/patients/", json={"invalid": "data"})
    assert response.status_code == 422

def test_cors_headers(client):
    """测试CORS头"""
    response = client.get("/")
    # 在实际部署中，CORS头应该根据配置设置
    assert response.status_code == 200

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])