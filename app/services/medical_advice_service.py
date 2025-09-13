"""
医嘱生成和风险评估服务
综合患者信息生成个性化医疗建议
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict

from app.models.schemas import PatientResponse
from app.services.knowledge_service import knowledge_base
from data.rules.medical_rules import HypertensionRuleEngine, PatientProfile, RiskLevel
from app.utils.helpers import calculate_bmi, format_medical_advice

class MedicalAdviceGenerator:
    """医疗建议生成器"""
    
    def __init__(self):
        self.rule_engine = HypertensionRuleEngine()
    
    def generate_comprehensive_advice(self, patient_data: Dict) -> Dict:
        """生成综合医疗建议"""
        try:
            # 创建患者档案
            patient_profile = self._create_patient_profile(patient_data)
            
            # 基础评估
            assessment = self._perform_basic_assessment(patient_profile)
            
            # 风险评估
            risk_assessment = self._perform_risk_assessment(patient_profile)
            
            # 生活方式建议
            lifestyle_advice = self._generate_lifestyle_advice(patient_profile)
            
            # 药物治疗建议
            medication_advice = self._generate_medication_advice(patient_profile)
            
            # 监测计划
            monitoring_plan = self._generate_monitoring_plan(patient_profile)
            
            # 紧急情况处理
            emergency_info = self._check_emergency_status(patient_profile)
            
            # 综合建议
            comprehensive_advice = {
                "patient_info": {
                    "name": patient_data.get('name', ''),
                    "age": patient_profile.age,
                    "gender": patient_profile.gender,
                    "bmi": patient_profile.bmi
                },
                "assessment": assessment,
                "risk_assessment": risk_assessment,
                "lifestyle_interventions": lifestyle_advice,
                "medication_recommendations": medication_advice,
                "monitoring_plan": monitoring_plan,
                "emergency_info": emergency_info,
                "follow_up_recommendations": self._generate_followup_plan(patient_profile),
                "patient_education": self._generate_patient_education(patient_profile),
                "generated_at": datetime.now().isoformat()
            }
            
            return comprehensive_advice
            
        except Exception as e:
            return {"error": f"生成医疗建议失败: {str(e)}"}
    
    def _create_patient_profile(self, patient_data: Dict) -> PatientProfile:
        """创建患者档案"""
        # 计算BMI
        bmi = None
        if patient_data.get('height') and patient_data.get('weight'):
            bmi = calculate_bmi(patient_data['height'], patient_data['weight'])
        
        return PatientProfile(
            age=patient_data.get('age', 50),
            gender=patient_data.get('gender', '男'),
            systolic_bp=patient_data.get('systolic_bp', 120),
            diastolic_bp=patient_data.get('diastolic_bp', 80),
            smoking=patient_data.get('smoking', False),
            diabetes=patient_data.get('diabetes', False),
            family_history=patient_data.get('family_history', False),
            heart_disease=patient_data.get('heart_disease', False),
            kidney_disease=patient_data.get('kidney_disease', False),
            stroke_history=patient_data.get('stroke_history', False),
            bmi=bmi,
            hypertension_duration=patient_data.get('hypertension_duration', 0),
            current_medications=patient_data.get('current_medications'),
            allergies=patient_data.get('allergies')
        )
    
    def _perform_basic_assessment(self, patient: PatientProfile) -> Dict:
        """基础评估"""
        bp_level = self.rule_engine.classify_blood_pressure(patient.systolic_bp, patient.diastolic_bp)
        target_bp = self.rule_engine.get_target_blood_pressure(patient)
        
        # BMI评估
        bmi_status = "未知"
        if patient.bmi:
            if patient.bmi < 18.5:
                bmi_status = "偏瘦"
            elif patient.bmi < 24:
                bmi_status = "正常"
            elif patient.bmi < 28:
                bmi_status = "超重"
            else:
                bmi_status = "肥胖"
        
        return {
            "blood_pressure_level": bp_level.value,
            "current_bp": f"{patient.systolic_bp}/{patient.diastolic_bp} mmHg",
            "target_bp": f"{target_bp[0]}/{target_bp[1]} mmHg",
            "bmi": patient.bmi,
            "bmi_status": bmi_status,
            "hypertension_duration": f"{patient.hypertension_duration}年" if patient.hypertension_duration else "新诊断"
        }
    
    def _perform_risk_assessment(self, patient: PatientProfile) -> Dict:
        """风险评估"""
        cardiovascular_risk = self.rule_engine.assess_cardiovascular_risk(patient)
        
        # 计算风险因子
        risk_factors = []
        if patient.age >= 55 and patient.gender == "男":
            risk_factors.append("年龄(男性≥55岁)")
        elif patient.age >= 65 and patient.gender == "女":
            risk_factors.append("年龄(女性≥65岁)")
        
        if patient.smoking:
            risk_factors.append("吸烟")
        if patient.diabetes:
            risk_factors.append("糖尿病")
        if patient.family_history:
            risk_factors.append("家族史")
        if patient.bmi and patient.bmi >= 28:
            risk_factors.append("肥胖")
        
        # 靶器官损害
        target_organ_damage = []
        if patient.heart_disease:
            target_organ_damage.append("心脏疾病")
        if patient.kidney_disease:
            target_organ_damage.append("肾脏疾病")
        if patient.stroke_history:
            target_organ_damage.append("脑卒中史")
        
        return {
            "cardiovascular_risk_level": cardiovascular_risk.value,
            "risk_factors": risk_factors,
            "target_organ_damage": target_organ_damage,
            "risk_score": len(risk_factors) + len(target_organ_damage) * 2,
            "ten_year_risk": self._estimate_ten_year_risk(patient, len(risk_factors))
        }
    
    def _estimate_ten_year_risk(self, patient: PatientProfile, risk_factor_count: int) -> str:
        """估算10年心血管风险"""
        base_risk = 5  # 基础风险5%
        
        # 年龄因子
        if patient.age >= 65:
            base_risk += 15
        elif patient.age >= 55:
            base_risk += 10
        elif patient.age >= 45:
            base_risk += 5
        
        # 血压因子
        if patient.systolic_bp >= 180:
            base_risk += 20
        elif patient.systolic_bp >= 160:
            base_risk += 15
        elif patient.systolic_bp >= 140:
            base_risk += 10
        
        # 其他风险因子
        base_risk += risk_factor_count * 5
        
        # 性别因子
        if patient.gender == "男":
            base_risk += 5
        
        # 限制在合理范围内
        final_risk = min(base_risk, 80)
        
        if final_risk < 10:
            return f"低风险 (<{final_risk}%)"
        elif final_risk < 20:
            return f"中等风险 (~{final_risk}%)"
        else:
            return f"高风险 (>{final_risk}%)"
    
    def _generate_lifestyle_advice(self, patient: PatientProfile) -> List[Dict]:
        """生成生活方式建议"""
        advice_list = []
        
        # 基础建议
        basic_advice = [
            {
                "category": "饮食调节",
                "recommendation": "减少钠盐摄入，每日食盐摄入量控制在6g以下",
                "priority": "高",
                "evidence_level": "A"
            },
            {
                "category": "饮食调节", 
                "recommendation": "增加富含钾的食物摄入，如新鲜蔬菜、水果、坚果",
                "priority": "高",
                "evidence_level": "A"
            },
            {
                "category": "运动锻炼",
                "recommendation": "进行规律的有氧运动，每周至少150分钟中等强度运动",
                "priority": "高",
                "evidence_level": "A"
            }
        ]
        advice_list.extend(basic_advice)
        
        # 个性化建议
        if patient.bmi and patient.bmi >= 24:
            advice_list.append({
                "category": "体重管理",
                "recommendation": f"控制体重，目标BMI在18.5-23.9之间（当前BMI: {patient.bmi:.1f}）",
                "priority": "高",
                "evidence_level": "A"
            })
        
        if patient.smoking:
            advice_list.append({
                "category": "戒烟限酒",
                "recommendation": "完全戒烟，避免被动吸烟，考虑使用戒烟辅助方法",
                "priority": "极高",
                "evidence_level": "A"
            })
        
        if patient.diabetes:
            advice_list.append({
                "category": "血糖控制",
                "recommendation": "严格控制血糖，HbA1c目标值<7%，配合内分泌科治疗",
                "priority": "高",
                "evidence_level": "A"
            })
        
        # 心理健康建议
        advice_list.append({
            "category": "心理调节",
            "recommendation": "保持心理平衡，学习放松技巧，保证充足睡眠7-8小时",
            "priority": "中",
            "evidence_level": "B"
        })
        
        return advice_list
    
    def _generate_medication_advice(self, patient: PatientProfile) -> Dict:
        """生成药物治疗建议"""
        return self.rule_engine.recommend_medications(patient)
    
    def _generate_monitoring_plan(self, patient: PatientProfile) -> Dict:
        """生成监测计划"""
        plan = self.rule_engine.generate_monitoring_plan(patient)
        
        # 添加个性化监测建议
        if patient.diabetes:
            plan["additional_monitoring"] = [
                "每3个月检查HbA1c",
                "定期监测血糖",
                "年度眼底检查"
            ]
        
        if patient.kidney_disease:
            if "additional_monitoring" not in plan:
                plan["additional_monitoring"] = []
            plan["additional_monitoring"].extend([
                "每3-6个月检查肾功能",
                "定期监测尿蛋白",
                "注意药物肾毒性"
            ])
        
        return plan
    
    def _check_emergency_status(self, patient: PatientProfile) -> Dict:
        """检查紧急状况"""
        emergency_info = {
            "is_emergency": False,
            "urgency_level": "常规",
            "warnings": [],
            "immediate_actions": []
        }
        
        # 高血压危象
        if patient.systolic_bp >= 180 or patient.diastolic_bp >= 110:
            emergency_info.update({
                "is_emergency": True,
                "urgency_level": "紧急",
                "warnings": ["血压严重升高，属于高血压危象"],
                "immediate_actions": [
                    "立即就医，不要等待",
                    "避免血压急剧下降",
                    "监测神经系统症状",
                    "准备急救药物"
                ]
            })
        
        # 严重并发症风险
        elif patient.systolic_bp >= 160 or patient.diastolic_bp >= 100:
            emergency_info.update({
                "urgency_level": "优先",
                "warnings": ["血压明显升高，需要及时干预"],
                "immediate_actions": [
                    "1-2周内就医",
                    "开始或调整降压治疗",
                    "密切监测血压变化"
                ]
            })
        
        # 特殊人群警告
        if patient.diabetes and (patient.systolic_bp >= 140 or patient.diastolic_bp >= 90):
            emergency_info["warnings"].append("糖尿病患者血压控制目标更严格")
        
        if patient.stroke_history and patient.systolic_bp >= 160:
            emergency_info["warnings"].append("有脑卒中史，血压控制不佳，脑血管事件风险增加")
        
        return emergency_info
    
    def _generate_followup_plan(self, patient: PatientProfile) -> Dict:
        """生成随访计划"""
        bp_level = self.rule_engine.classify_blood_pressure(patient.systolic_bp, patient.diastolic_bp)
        
        if bp_level.value in ["3级高血压", "2级高血压"]:
            return {
                "initial_follow_up": "1-2周",
                "adjustment_period": "每2-4周调整治疗方案",
                "stable_follow_up": "血压稳定后每1-2个月",
                "annual_assessment": "每年全面评估一次"
            }
        elif bp_level.value == "1级高血压":
            return {
                "initial_follow_up": "2-4周",
                "adjustment_period": "每4-6周评估疗效",
                "stable_follow_up": "血压稳定后每2-3个月",
                "annual_assessment": "每年全面评估一次"
            }
        else:
            return {
                "initial_follow_up": "1-3个月",
                "adjustment_period": "根据需要调整",
                "stable_follow_up": "每3-6个月",
                "annual_assessment": "每年体检一次"
            }
    
    def _generate_patient_education(self, patient: PatientProfile) -> List[str]:
        """生成患者教育内容"""
        education_points = [
            "了解高血压是慢性疾病，需要长期管理",
            "学会正确测量血压的方法",
            "了解目标血压值和达标的重要性",
            "掌握生活方式干预的具体方法",
            "了解药物治疗的必要性和注意事项",
            "识别高血压急症的症状和处理方法"
        ]
        
        if patient.diabetes:
            education_points.append("了解糖尿病与高血压的相互影响")
        
        if patient.smoking:
            education_points.append("了解吸烟对心血管系统的危害")
        
        if patient.bmi and patient.bmi >= 28:
            education_points.append("学习科学的减重方法")
        
        return education_points

class RiskScoreCalculator:
    """风险评分计算器"""
    
    @staticmethod
    def calculate_framingham_risk_score(patient: PatientProfile) -> Dict:
        """计算Framingham风险评分"""
        # 简化的Framingham评分
        score = 0
        
        # 年龄评分
        if patient.gender == "男":
            if patient.age >= 70:
                score += 5
            elif patient.age >= 60:
                score += 4
            elif patient.age >= 50:
                score += 3
            elif patient.age >= 40:
                score += 2
        else:  # 女性
            if patient.age >= 70:
                score += 6
            elif patient.age >= 60:
                score += 5
            elif patient.age >= 50:
                score += 4
            elif patient.age >= 40:
                score += 3
        
        # 血压评分
        if patient.systolic_bp >= 180:
            score += 4
        elif patient.systolic_bp >= 160:
            score += 3
        elif patient.systolic_bp >= 140:
            score += 2
        elif patient.systolic_bp >= 120:
            score += 1
        
        # 其他因素
        if patient.smoking:
            score += 2
        if patient.diabetes:
            score += 2
        if patient.family_history:
            score += 1
        
        # 风险分层
        if score >= 20:
            risk_level = "极高风险"
            ten_year_risk = ">30%"
        elif score >= 15:
            risk_level = "高风险"
            ten_year_risk = "20-30%"
        elif score >= 10:
            risk_level = "中等风险"
            ten_year_risk = "10-20%"
        else:
            risk_level = "低风险"
            ten_year_risk = "<10%"
        
        return {
            "total_score": score,
            "risk_level": risk_level,
            "ten_year_cardiovascular_risk": ten_year_risk,
            "recommendations": RiskScoreCalculator._get_risk_recommendations(risk_level)
        }
    
    @staticmethod
    def _get_risk_recommendations(risk_level: str) -> List[str]:
        """根据风险等级提供建议"""
        recommendations = {
            "低风险": [
                "继续维持健康的生活方式",
                "定期监测血压",
                "每年体检一次"
            ],
            "中等风险": [
                "积极的生活方式干预",
                "考虑药物治疗",
                "每3-6个月随访",
                "控制其他心血管危险因素"
            ],
            "高风险": [
                "强化生活方式干预",
                "启动药物治疗",
                "每1-3个月随访",
                "严格控制血压和其他危险因素"
            ],
            "极高风险": [
                "立即启动药物治疗",
                "多重药物联合治疗",
                "每1-2个月随访",
                "考虑专科会诊",
                "积极预防心血管事件"
            ]
        }
        
        return recommendations.get(risk_level, ["请咨询专业医生"])

# 全局医疗建议生成器实例
medical_advice_generator = MedicalAdviceGenerator()