"""
高血压医嘱规则引擎
基于循证医学指南的智能决策系统
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "低风险"
    MEDIUM = "中风险" 
    HIGH = "高风险"
    VERY_HIGH = "极高风险"

class BloodPressureLevel(Enum):
    NORMAL = "正常血压"
    HIGH_NORMAL = "正常高值"
    GRADE_1 = "1级高血压"
    GRADE_2 = "2级高血压"
    GRADE_3 = "3级高血压"
    ISOLATED_SYSTOLIC = "单纯收缩期高血压"

@dataclass
class PatientProfile:
    """患者档案"""
    age: int
    gender: str
    systolic_bp: float
    diastolic_bp: float
    
    # 危险因素
    smoking: bool = False
    diabetes: bool = False
    family_history: bool = False
    heart_disease: bool = False
    kidney_disease: bool = False
    stroke_history: bool = False
    
    # 体征
    bmi: Optional[float] = None
    hypertension_duration: Optional[int] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None

class HypertensionRuleEngine:
    """高血压诊疗规则引擎"""
    
    def __init__(self):
        self.risk_factors = [
            "smoking", "diabetes", "family_history", 
            "heart_disease", "kidney_disease", "stroke_history"
        ]
    
    def classify_blood_pressure(self, systolic: float, diastolic: float) -> BloodPressureLevel:
        """血压分级"""
        if systolic < 120 and diastolic < 80:
            return BloodPressureLevel.NORMAL
        elif systolic < 130 and diastolic < 80:
            return BloodPressureLevel.HIGH_NORMAL
        elif (130 <= systolic < 140) or (80 <= diastolic < 90):
            return BloodPressureLevel.HIGH_NORMAL
        elif (140 <= systolic < 160) or (90 <= diastolic < 100):
            return BloodPressureLevel.GRADE_1
        elif (160 <= systolic < 180) or (100 <= diastolic < 110):
            return BloodPressureLevel.GRADE_2
        elif systolic >= 180 or diastolic >= 110:
            return BloodPressureLevel.GRADE_3
        elif systolic >= 140 and diastolic < 90:
            return BloodPressureLevel.ISOLATED_SYSTOLIC
        else:
            return BloodPressureLevel.HIGH_NORMAL
    
    def assess_cardiovascular_risk(self, patient: PatientProfile) -> RiskLevel:
        """心血管风险评估"""
        bp_level = self.classify_blood_pressure(patient.systolic_bp, patient.diastolic_bp)
        
        # 计算危险因素数量
        risk_count = sum([
            getattr(patient, factor) for factor in self.risk_factors
        ])
        
        # 年龄因素
        age_risk = (patient.age >= 55 and patient.gender == "男") or \
                  (patient.age >= 65 and patient.gender == "女")
        if age_risk:
            risk_count += 1
        
        # BMI因素
        if patient.bmi and patient.bmi >= 28:
            risk_count += 1
        
        # 靶器官损害或临床疾病
        target_organ_damage = patient.heart_disease or patient.kidney_disease or patient.stroke_history
        
        # 风险分层
        if bp_level == BloodPressureLevel.NORMAL:
            return RiskLevel.LOW
        elif bp_level == BloodPressureLevel.HIGH_NORMAL:
            if risk_count == 0:
                return RiskLevel.LOW
            elif risk_count <= 2:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.HIGH
        elif bp_level == BloodPressureLevel.GRADE_1:
            if risk_count == 0:
                return RiskLevel.MEDIUM
            elif risk_count <= 2 and not target_organ_damage:
                return RiskLevel.MEDIUM
            elif risk_count >= 3 or target_organ_damage:
                return RiskLevel.HIGH
            else:
                return RiskLevel.VERY_HIGH
        elif bp_level == BloodPressureLevel.GRADE_2:
            if risk_count <= 2 and not target_organ_damage:
                return RiskLevel.HIGH
            else:
                return RiskLevel.VERY_HIGH
        else:  # GRADE_3
            return RiskLevel.VERY_HIGH
    
    def get_target_blood_pressure(self, patient: PatientProfile) -> Tuple[int, int]:
        """获取目标血压"""
        if patient.diabetes or patient.kidney_disease:
            return (130, 80)
        elif patient.age >= 65:
            return (150, 90)
        elif patient.heart_disease:
            return (130, 80)
        else:
            return (140, 90)
    
    def recommend_lifestyle_interventions(self, patient: PatientProfile) -> List[str]:
        """生活方式干预建议"""
        recommendations = []
        
        # 基础建议
        recommendations.extend([
            "减少钠盐摄入，每日食盐摄入量控制在6g以下",
            "增加富含钾的食物摄入，如新鲜蔬菜和水果",
            "进行规律的有氧运动，每周至少150分钟中等强度运动"
        ])
        
        # 个性化建议
        if patient.bmi and patient.bmi >= 24:
            recommendations.append("控制体重，目标BMI在18.5-23.9 kg/m²")
        
        if patient.smoking:
            recommendations.append("戒烟，避免被动吸烟")
        
        if patient.diabetes:
            recommendations.extend([
                "严格控制血糖，HbA1c目标值<7%",
                "定期监测血糖变化"
            ])
        
        # 心理健康
        recommendations.extend([
            "保持心理平衡，学习放松技巧",
            "保证充足睡眠，每晚7-8小时",
            "限制饮酒，男性每日酒精摄入<25g，女性<15g"
        ])
        
        return recommendations
    
    def recommend_medications(self, patient: PatientProfile) -> Dict:
        """药物治疗建议"""
        bp_level = self.classify_blood_pressure(patient.systolic_bp, patient.diastolic_bp)
        risk_level = self.assess_cardiovascular_risk(patient)
        
        # 判断是否需要药物治疗
        needs_medication = False
        if bp_level in [BloodPressureLevel.GRADE_2, BloodPressureLevel.GRADE_3]:
            needs_medication = True
        elif bp_level == BloodPressureLevel.GRADE_1:
            if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                needs_medication = True
        
        result = {
            "needs_medication": needs_medication,
            "primary_drugs": [],
            "combination_drugs": [],
            "contraindications": []
        }
        
        if not needs_medication:
            result["recommendation"] = "暂时不需要药物治疗，建议生活方式干预，3个月后复查"
            return result
        
        # 首选药物推荐
        primary_drugs = []
        
        if patient.diabetes or patient.kidney_disease:
            primary_drugs.append({
                "type": "ACEI/ARB",
                "examples": ["依那普利", "氯沙坦", "缬沙坦"],
                "reason": "糖尿病/肾病患者首选，具有肾脏保护作用"
            })
        
        if patient.heart_disease:
            primary_drugs.append({
                "type": "β受体阻滞剂",
                "examples": ["美托洛尔", "比索洛尔"],
                "reason": "冠心病患者首选，可降低心脏事件风险"
            })
        
        if patient.age >= 60 or bp_level == BloodPressureLevel.ISOLATED_SYSTOLIC:
            primary_drugs.append({
                "type": "钙通道阻滞剂",
                "examples": ["氨氯地平", "硝苯地平缓释片"],
                "reason": "老年患者和单纯收缩期高血压首选"
            })
        
        # 如果没有特殊适应症，给出一般推荐
        if not primary_drugs:
            primary_drugs.append({
                "type": "ACEI/ARB",
                "examples": ["依那普利", "氯沙坦"],
                "reason": "一线降压药物，心血管保护作用确切"
            })
        
        result["primary_drugs"] = primary_drugs
        
        # 联合用药建议
        if bp_level in [BloodPressureLevel.GRADE_2, BloodPressureLevel.GRADE_3]:
            result["combination_drugs"] = [
                "ACEI/ARB + 钙通道阻滞剂",
                "ACEI/ARB + 利尿剂",
                "钙通道阻滞剂 + 利尿剂"
            ]
        
        # 禁忌症检查
        contraindications = []
        if patient.allergies:
            contraindications.append(f"注意药物过敏史：{patient.allergies}")
        
        result["contraindications"] = contraindications
        
        return result
    
    def generate_monitoring_plan(self, patient: PatientProfile) -> Dict:
        """生成监测计划"""
        plan = {
            "blood_pressure": {
                "frequency": "每周2-3次",
                "target": self.get_target_blood_pressure(patient),
                "notes": "建议家庭血压监测，记录血压日记"
            },
            "follow_up": {
                "initial": "2-4周后复查，评估疗效",
                "stable": "血压稳定后每1-3个月复查",
                "notes": "调整药物剂量或联合用药"
            },
            "laboratory": []
        }
        
        # 实验室检查建议
        lab_tests = ["血常规", "生化全项", "尿常规", "心电图"]
        
        if patient.diabetes:
            lab_tests.extend(["HbA1c", "糖化血红蛋白"])
        
        if patient.kidney_disease:
            lab_tests.extend(["肾功能", "尿蛋白"])
        
        plan["laboratory"] = lab_tests
        
        return plan
    
    def generate_medical_advice(self, patient: PatientProfile) -> Dict:
        """生成综合医疗建议"""
        bp_level = self.classify_blood_pressure(patient.systolic_bp, patient.diastolic_bp)
        risk_level = self.assess_cardiovascular_risk(patient)
        
        advice = {
            "assessment": {
                "blood_pressure_level": bp_level.value,
                "cardiovascular_risk": risk_level.value,
                "target_bp": self.get_target_blood_pressure(patient)
            },
            "lifestyle_interventions": self.recommend_lifestyle_interventions(patient),
            "medication_recommendations": self.recommend_medications(patient),
            "monitoring_plan": self.generate_monitoring_plan(patient),
            "warnings": self._generate_warnings(patient)
        }
        
        return advice
    
    def _generate_warnings(self, patient: PatientProfile) -> List[str]:
        """生成警告信息"""
        warnings = []
        
        if patient.systolic_bp >= 180 or patient.diastolic_bp >= 110:
            warnings.append("血压严重升高，建议立即就医")
        
        if patient.stroke_history and patient.systolic_bp >= 160:
            warnings.append("有脑卒中史，血压控制不佳，请及时调整治疗方案")
        
        if patient.diabetes and (patient.systolic_bp >= 140 or patient.diastolic_bp >= 90):
            warnings.append("糖尿病患者血压控制目标更严格，建议强化降压治疗")
        
        return warnings

# 使用示例
if __name__ == "__main__":
    # 创建规则引擎
    engine = HypertensionRuleEngine()
    
    # 示例患者
    patient = PatientProfile(
        age=55,
        gender="男",
        systolic_bp=150,
        diastolic_bp=95,
        smoking=True,
        diabetes=True,
        bmi=26.5
    )
    
    # 生成医疗建议
    advice = engine.generate_medical_advice(patient)
    print(json.dumps(advice, indent=2, ensure_ascii=False))