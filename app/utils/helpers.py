"""
工具函数模块
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """计算BMI"""
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("身高和体重必须为正数")
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def classify_bmi(bmi: float) -> str:
    """BMI分类"""
    if bmi < 18.5:
        return "偏瘦"
    elif bmi < 24:
        return "正常"
    elif bmi < 28:
        return "超重"
    else:
        return "肥胖"

def validate_blood_pressure(systolic: float, diastolic: float) -> bool:
    """验证血压值的合理性"""
    if not (60 <= systolic <= 300):
        return False
    if not (40 <= diastolic <= 200):
        return False
    if diastolic >= systolic:
        return False
    return True

def format_blood_pressure(systolic: float, diastolic: float) -> str:
    """格式化血压显示"""
    return f"{int(systolic)}/{int(diastolic)} mmHg"

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def generate_patient_id(name: str, phone: str) -> str:
    """生成患者ID"""
    data = f"{name}{phone}{datetime.now().isoformat()}"
    return hashlib.md5(data.encode()).hexdigest()[:8].upper()

def parse_medication_string(medication_str: str) -> List[Dict[str, str]]:
    """解析用药字符串"""
    if not medication_str:
        return []
    
    medications = []
    lines = medication_str.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line:
            # 简单解析药物名称和剂量
            parts = line.split()
            if parts:
                medication = {
                    "name": parts[0],
                    "dosage": " ".join(parts[1:]) if len(parts) > 1 else ""
                }
                medications.append(medication)
    
    return medications

def calculate_age_from_birth_date(birth_date: datetime) -> int:
    """根据出生日期计算年龄"""
    today = datetime.now()
    age = today.year - birth_date.year
    
    if today.month < birth_date.month or \
       (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age

def get_blood_pressure_trend(records: List[Dict]) -> Dict[str, Any]:
    """分析血压趋势"""
    if len(records) < 2:
        return {"trend": "数据不足", "change": 0}
    
    # 按时间排序
    sorted_records = sorted(records, key=lambda x: x['measurement_time'])
    
    # 计算最近7天的平均值
    recent_systolic = [r['systolic_bp'] for r in sorted_records[-7:]]
    recent_diastolic = [r['diastolic_bp'] for r in sorted_records[-7:]]
    
    # 计算之前7天的平均值
    if len(sorted_records) >= 14:
        previous_systolic = [r['systolic_bp'] for r in sorted_records[-14:-7]]
        previous_diastolic = [r['diastolic_bp'] for r in sorted_records[-14:-7]]
    else:
        previous_systolic = [r['systolic_bp'] for r in sorted_records[:-7]]
        previous_diastolic = [r['diastolic_bp'] for r in sorted_records[:-7]]
    
    if not previous_systolic:
        return {"trend": "数据不足", "change": 0}
    
    recent_avg_systolic = sum(recent_systolic) / len(recent_systolic)
    recent_avg_diastolic = sum(recent_diastolic) / len(recent_diastolic)
    
    previous_avg_systolic = sum(previous_systolic) / len(previous_systolic)
    previous_avg_diastolic = sum(previous_diastolic) / len(previous_diastolic)
    
    systolic_change = recent_avg_systolic - previous_avg_systolic
    diastolic_change = recent_avg_diastolic - previous_avg_diastolic
    
    # 判断趋势
    if abs(systolic_change) < 5 and abs(diastolic_change) < 3:
        trend = "稳定"
    elif systolic_change > 5 or diastolic_change > 3:
        trend = "上升"
    else:
        trend = "下降"
    
    return {
        "trend": trend,
        "systolic_change": round(systolic_change, 1),
        "diastolic_change": round(diastolic_change, 1),
        "recent_avg": f"{recent_avg_systolic:.1f}/{recent_avg_diastolic:.1f}",
        "previous_avg": f"{previous_avg_systolic:.1f}/{previous_avg_diastolic:.1f}"
    }

def format_medical_advice(advice: Dict) -> str:
    """格式化医疗建议为可读文本"""
    formatted = []
    
    # 血压评估
    if "assessment" in advice:
        assessment = advice["assessment"]
        formatted.append("【血压评估】")
        formatted.append(f"血压分级：{assessment.get('blood_pressure_level', '未知')}")
        formatted.append(f"心血管风险：{assessment.get('cardiovascular_risk', '未知')}")
        target = assessment.get('target_bp', [])
        if target:
            formatted.append(f"目标血压：{target[0]}/{target[1]} mmHg")
        formatted.append("")
    
    # 生活方式建议
    if "lifestyle_interventions" in advice:
        formatted.append("【生活方式建议】")
        for i, item in enumerate(advice["lifestyle_interventions"], 1):
            formatted.append(f"{i}. {item}")
        formatted.append("")
    
    # 药物治疗
    if "medication_recommendations" in advice:
        med_rec = advice["medication_recommendations"]
        formatted.append("【药物治疗建议】")
        
        if med_rec.get("needs_medication"):
            formatted.append("建议药物治疗")
            
            if "primary_drugs" in med_rec:
                formatted.append("\n推荐药物：")
                for drug in med_rec["primary_drugs"]:
                    formatted.append(f"• {drug.get('type')}: {', '.join(drug.get('examples', []))}")
                    formatted.append(f"  适应症：{drug.get('reason', '')}")
        else:
            formatted.append("暂时不需要药物治疗，建议生活方式干预")
        formatted.append("")
    
    # 监测计划
    if "monitoring_plan" in advice:
        plan = advice["monitoring_plan"]
        formatted.append("【监测随访】")
        
        if "blood_pressure" in plan:
            bp_plan = plan["blood_pressure"]
            formatted.append(f"血压监测：{bp_plan.get('frequency', '定期监测')}")
        
        if "follow_up" in plan:
            follow_up = plan["follow_up"]
            formatted.append(f"复查计划：{follow_up.get('initial', '定期复查')}")
        formatted.append("")
    
    # 警告信息
    if "warnings" in advice and advice["warnings"]:
        formatted.append("【重要提醒】")
        for warning in advice["warnings"]:
            formatted.append(f"⚠️ {warning}")
        formatted.append("")
    
    # 免责声明
    formatted.append("【免责声明】")
    formatted.append("以上建议仅供参考，不能替代专业医生的诊断和治疗。如有疑问或症状加重，请及时就医。")
    
    return "\n".join(formatted)

def safe_float_convert(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_int_convert(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def clean_medication_input(medication_str: str) -> str:
    """清理用药输入"""
    if not medication_str:
        return ""
    
    # 移除多余的空格和换行
    cleaned = re.sub(r'\s+', ' ', medication_str.strip())
    
    # 移除特殊字符（保留中文、英文、数字、常见符号）
    cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,，。、/（）()]', '', cleaned)
    
    return cleaned