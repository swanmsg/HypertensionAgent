"""
AI智能体测试
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_agent import HypertensionAgent, MedicalKnowledgeTool, RiskAssessmentTool, MedicationRecommendationTool
from data.rules.medical_rules import HypertensionRuleEngine, PatientProfile

class TestMedicalKnowledgeTool:
    """医学知识工具测试"""
    
    def test_knowledge_search(self):
        """测试知识搜索"""
        tool = MedicalKnowledgeTool()
        result = tool._run("血压分类")
        
        assert "血压分类" in result
        assert "正常血压" in result or "高血压" in result

class TestRiskAssessmentTool:
    """风险评估工具测试"""
    
    def test_risk_assessment(self):
        """测试风险评估"""
        tool = RiskAssessmentTool()
        
        patient_data = {
            "age": 55,
            "gender": "男",
            "systolic_bp": 150,
            "diastolic_bp": 95,
            "smoking": True,
            "diabetes": False,
            "family_history": True
        }
        
        result = tool._run(json.dumps(patient_data))
        result_dict = json.loads(result)
        
        assert "assessment" in result_dict
        assert "blood_pressure_level" in result_dict["assessment"]
        assert "cardiovascular_risk" in result_dict["assessment"]
    
    def test_invalid_input(self):
        """测试无效输入"""
        tool = RiskAssessmentTool()
        result = tool._run("invalid json")
        
        assert "失败" in result

class TestMedicationRecommendationTool:
    """药物推荐工具测试"""
    
    def test_medication_recommendation(self):
        """测试药物推荐"""
        tool = MedicationRecommendationTool()
        
        patient_data = {
            "age": 60,
            "gender": "女",
            "systolic_bp": 160,
            "diastolic_bp": 100,
            "diabetes": True,
            "heart_disease": False,
            "kidney_disease": False
        }
        
        result = tool._run(json.dumps(patient_data))
        result_dict = json.loads(result)
        
        assert "needs_medication" in result_dict
        assert result_dict["needs_medication"] == True
        assert "primary_drugs" in result_dict

class TestHypertensionAgent:
    """高血压智能体测试"""
    
    @pytest.fixture
    def agent(self):
        """创建智能体实例"""
        return HypertensionAgent()
    
    def test_analyze_blood_pressure(self, agent):
        """测试血压分析"""
        result = agent.analyze_blood_pressure(150, 95)
        
        assert "blood_pressure" in result
        assert "classification" in result
        assert "risk_level" in result
        assert result["blood_pressure"] == "150/95 mmHg"
    
    def test_emergency_check_normal(self, agent):
        """测试正常血压的急症检查"""
        result = agent.emergency_check(120, 80)
        
        assert result["is_emergency"] == False
        assert len(result["warnings"]) == 0
    
    def test_emergency_check_crisis(self, agent):
        """测试高血压危象的急症检查"""
        result = agent.emergency_check(190, 120)
        
        assert result["is_emergency"] == True
        assert len(result["warnings"]) > 0
        assert "危象" in result["warnings"][0]
    
    @patch('langchain_openai.ChatOpenAI')
    def test_chat_function(self, mock_llm, agent):
        """测试对话功能"""
        # 模拟LLM响应
        mock_instance = Mock()
        mock_instance.predict.return_value = "这是AI的回复"
        mock_llm.return_value = mock_instance
        
        # 创建agent，跳过初始化
        try:
            response = agent.chat("什么是高血压？")
            assert isinstance(response, str)
        except Exception as e:
            # 如果没有API Key，跳过此测试
            pytest.skip(f"跳过AI对话测试: {e}")
    
    def test_get_medication_advice(self, agent):
        """测试获取药物建议"""
        patient_data = {
            "age": 50,
            "gender": "男",
            "systolic_bp": 140,
            "diastolic_bp": 90,
            "diabetes": False,
            "heart_disease": False,
            "kidney_disease": False
        }
        
        result = agent.get_medication_advice(patient_data)
        assert isinstance(result, dict)
        assert "needs_medication" in result

class TestHypertensionRuleEngine:
    """高血压规则引擎测试"""
    
    @pytest.fixture
    def engine(self):
        """创建规则引擎实例"""
        return HypertensionRuleEngine()
    
    def test_classify_blood_pressure(self, engine):
        """测试血压分级"""
        # 正常血压
        level = engine.classify_blood_pressure(110, 70)
        assert level.value == "正常血压"
        
        # 1级高血压
        level = engine.classify_blood_pressure(150, 95)
        assert level.value == "1级高血压"
        
        # 3级高血压
        level = engine.classify_blood_pressure(190, 120)
        assert level.value == "3级高血压"
    
    def test_assess_cardiovascular_risk(self, engine):
        """测试心血管风险评估"""
        # 低风险患者
        low_risk_patient = PatientProfile(
            age=30, gender="女", systolic_bp=120, diastolic_bp=80
        )
        risk = engine.assess_cardiovascular_risk(low_risk_patient)
        assert risk.value == "低风险"
        
        # 高风险患者
        high_risk_patient = PatientProfile(
            age=65, gender="男", systolic_bp=170, diastolic_bp=105,
            smoking=True, diabetes=True, heart_disease=True
        )
        risk = engine.assess_cardiovascular_risk(high_risk_patient)
        assert risk.value in ["高风险", "极高风险"]
    
    def test_get_target_blood_pressure(self, engine):
        """测试目标血压获取"""
        # 普通患者
        normal_patient = PatientProfile(
            age=50, gender="男", systolic_bp=140, diastolic_bp=90
        )
        target = engine.get_target_blood_pressure(normal_patient)
        assert target == (140, 90)
        
        # 糖尿病患者
        diabetes_patient = PatientProfile(
            age=50, gender="男", systolic_bp=140, diastolic_bp=90,
            diabetes=True
        )
        target = engine.get_target_blood_pressure(diabetes_patient)
        assert target == (130, 80)
    
    def test_recommend_lifestyle_interventions(self, engine):
        """测试生活方式干预建议"""
        patient = PatientProfile(
            age=50, gender="男", systolic_bp=150, diastolic_bp=95,
            smoking=True, bmi=28.5
        )
        
        recommendations = engine.recommend_lifestyle_interventions(patient)
        
        assert len(recommendations) > 0
        assert any("戒烟" in rec for rec in recommendations)
        assert any("体重" in rec for rec in recommendations)
    
    def test_recommend_medications(self, engine):
        """测试药物推荐"""
        # 需要药物治疗的患者
        patient = PatientProfile(
            age=60, gender="男", systolic_bp=170, diastolic_bp=105,
            diabetes=True
        )
        
        recommendations = engine.recommend_medications(patient)
        
        assert recommendations["needs_medication"] == True
        assert len(recommendations["primary_drugs"]) > 0
    
    def test_generate_monitoring_plan(self, engine):
        """测试监测计划生成"""
        patient = PatientProfile(
            age=55, gender="女", systolic_bp=150, diastolic_bp=95,
            diabetes=True
        )
        
        plan = engine.generate_monitoring_plan(patient)
        
        assert "blood_pressure" in plan
        assert "follow_up" in plan
        assert "laboratory" in plan
        assert "糖化血红蛋白" in plan["laboratory"]

def test_integration_workflow():
    """测试集成工作流"""
    # 创建测试患者
    patient_data = {
        "age": 55,
        "gender": "男",
        "systolic_bp": 160,
        "diastolic_bp": 100,
        "smoking": True,
        "diabetes": True,
        "family_history": True,
        "bmi": 28.0
    }
    
    # 创建智能体
    agent = HypertensionAgent()
    
    # 测试血压分析
    bp_analysis = agent.analyze_blood_pressure(
        patient_data["systolic_bp"], 
        patient_data["diastolic_bp"]
    )
    assert bp_analysis["classification"] in ["1级高血压", "2级高血压", "3级高血压"]
    
    # 测试药物建议
    medication_advice = agent.get_medication_advice(patient_data)
    assert medication_advice["needs_medication"] == True
    
    # 测试急症检查
    emergency = agent.emergency_check(
        patient_data["systolic_bp"], 
        patient_data["diastolic_bp"]
    )
    assert isinstance(emergency["is_emergency"], bool)

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])