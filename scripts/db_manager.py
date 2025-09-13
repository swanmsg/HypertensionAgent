"""
数据库初始化和管理脚本
"""

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Base, create_tables, get_db, Patient, BloodPressureRecord, MedicalAdvice
from app.models.schemas import PatientCreate, BloodPressureRecordCreate, MedicalAdviceCreate
from app.services.patient_service import PatientService, BloodPressureService, MedicalAdviceService

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    try:
        create_tables()
        print("✅ 数据库表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def create_sample_data():
    """创建示例数据"""
    print("正在创建示例数据...")
    
    try:
        db = next(get_db())
        patient_service = PatientService(db)
        bp_service = BloodPressureService(db)
        advice_service = MedicalAdviceService(db)
        
        # 示例患者数据
        sample_patients = [
            {
                "name": "张三",
                "age": 55,
                "gender": "男",
                "height": 175.0,
                "weight": 75.0,
                "phone": "13812345678",
                "email": "zhangsan@example.com",
                "systolic_bp": 150.0,
                "diastolic_bp": 95.0,
                "hypertension_duration": 3,
                "family_history": True,
                "smoking": True,
                "drinking": False,
                "diabetes": False,
                "heart_disease": False,
                "kidney_disease": False,
                "stroke_history": False,
                "exercise_frequency": "偶尔运动",
                "current_medications": "氨氯地平5mg 每日一次\n美托洛尔25mg 每日两次",
                "allergies": "青霉素过敏"
            },
            {
                "name": "李四",
                "age": 62,
                "gender": "女",
                "height": 160.0,
                "weight": 65.0,
                "phone": "13987654321",
                "email": "lisi@example.com",
                "systolic_bp": 165.0,
                "diastolic_bp": 100.0,
                "hypertension_duration": 8,
                "family_history": False,
                "smoking": False,
                "drinking": False,
                "diabetes": True,
                "heart_disease": False,
                "kidney_disease": True,
                "stroke_history": False,
                "exercise_frequency": "经常运动",
                "current_medications": "缬沙坦80mg 每日一次\n二甲双胍500mg 每日两次",
                "allergies": None
            },
            {
                "name": "王五",
                "age": 45,
                "gender": "男",
                "height": 170.0,
                "weight": 80.0,
                "phone": "13765432109",
                "email": "wangwu@example.com",
                "systolic_bp": 140.0,
                "diastolic_bp": 90.0,
                "hypertension_duration": 1,
                "family_history": True,
                "smoking": False,
                "drinking": True,
                "diabetes": False,
                "heart_disease": False,
                "kidney_disease": False,
                "stroke_history": False,
                "exercise_frequency": "有时运动",
                "current_medications": None,
                "allergies": None
            }
        ]
        
        created_patients = []
        for patient_data in sample_patients:
            patient_create = PatientCreate(**patient_data)
            patient = patient_service.create_patient(patient_create)
            created_patients.append(patient)
            print(f"✅ 创建患者: {patient.name}")
        
        # 为患者创建血压记录
        from datetime import timedelta
        import random
        
        for patient in created_patients:
            # 创建最近30天的血压记录
            for i in range(10):
                days_ago = random.randint(1, 30)
                measurement_time = datetime.now() - timedelta(days=days_ago)
                
                # 基于患者基础血压添加随机变化
                systolic_variation = random.randint(-15, 15)
                diastolic_variation = random.randint(-10, 10)
                
                systolic = patient.systolic_bp + systolic_variation
                diastolic = patient.diastolic_bp + diastolic_variation
                
                # 确保血压值合理
                systolic = max(100, min(200, systolic))
                diastolic = max(60, min(120, diastolic))
                
                bp_record = BloodPressureRecordCreate(
                    patient_id=patient.id,
                    systolic_bp=systolic,
                    diastolic_bp=diastolic,
                    heart_rate=random.randint(60, 100),
                    measurement_time=measurement_time,
                    measurement_location="左臂",
                    notes=f"第{i+1}次测量" if i % 3 == 0 else None
                )
                
                bp_service.create_record(bp_record)
            
            print(f"✅ 为患者 {patient.name} 创建了10条血压记录")
            
            # 创建医疗建议
            advice_create = MedicalAdviceCreate(
                patient_id=patient.id,
                advice_type="初始评估",
                content=f"基于患者 {patient.name} 的血压情况，建议进行生活方式干预和定期监测。",
                risk_level="中风险",
                ai_confidence=0.85
            )
            
            advice_service.create_advice(advice_create)
            print(f"✅ 为患者 {patient.name} 创建了医疗建议")
        
        db.close()
        print("✅ 示例数据创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 示例数据创建失败: {e}")
        return False

def backup_database(backup_path: str = None):
    """备份数据库"""
    if backup_path is None:
        backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        import shutil
        shutil.copy("hypertension_agent.db", backup_path)
        print(f"✅ 数据库备份成功: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ 数据库备份失败: {e}")
        return False

def clear_database():
    """清空数据库（谨慎使用）"""
    print("⚠️ 警告：这将清空所有数据！")
    confirm = input("请输入 'YES' 确认清空数据库: ")
    
    if confirm == "YES":
        try:
            from sqlalchemy import create_engine, MetaData
            engine = create_engine("sqlite:///./hypertension_agent.db")
            
            # 删除所有表
            Base.metadata.drop_all(bind=engine)
            print("✅ 数据库清空成功")
            
            # 重新创建表
            Base.metadata.create_all(bind=engine)
            print("✅ 数据库表重新创建成功")
            return True
        except Exception as e:
            print(f"❌ 清空数据库失败: {e}")
            return False
    else:
        print("❌ 操作已取消")
        return False

def check_database():
    """检查数据库状态"""
    print("正在检查数据库状态...")
    
    try:
        db = next(get_db())
        
        # 检查患者数量
        patient_count = db.query(Patient).filter(Patient.is_active == True).count()
        print(f"活跃患者数量: {patient_count}")
        
        # 检查血压记录数量
        bp_count = db.query(BloodPressureRecord).count()
        print(f"血压记录数量: {bp_count}")
        
        # 检查医疗建议数量
        advice_count = db.query(MedicalAdvice).filter(MedicalAdvice.is_active == True).count()
        print(f"有效医疗建议数量: {advice_count}")
        
        db.close()
        print("✅ 数据库状态检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库状态检查失败: {e}")
        return False

def export_data(export_path: str = None):
    """导出数据为JSON格式"""
    if export_path is None:
        export_path = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        db = next(get_db())
        
        # 导出患者数据
        patients = db.query(Patient).filter(Patient.is_active == True).all()
        patients_data = []
        
        for patient in patients:
            patient_dict = {
                "id": patient.id,
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender,
                "height": patient.height,
                "weight": patient.weight,
                "phone": patient.phone,
                "email": patient.email,
                "systolic_bp": patient.systolic_bp,
                "diastolic_bp": patient.diastolic_bp,
                "hypertension_duration": patient.hypertension_duration,
                "created_at": patient.created_at.isoformat(),
                
                # 血压记录
                "blood_pressure_records": [],
                
                # 医疗建议
                "medical_advice": []
            }
            
            # 获取血压记录
            bp_records = db.query(BloodPressureRecord).filter(
                BloodPressureRecord.patient_id == patient.id
            ).all()
            
            for bp in bp_records:
                patient_dict["blood_pressure_records"].append({
                    "systolic_bp": bp.systolic_bp,
                    "diastolic_bp": bp.diastolic_bp,
                    "heart_rate": bp.heart_rate,
                    "measurement_time": bp.measurement_time.isoformat(),
                    "notes": bp.notes
                })
            
            # 获取医疗建议
            advice_list = db.query(MedicalAdvice).filter(
                MedicalAdvice.patient_id == patient.id,
                MedicalAdvice.is_active == True
            ).all()
            
            for advice in advice_list:
                patient_dict["medical_advice"].append({
                    "advice_type": advice.advice_type,
                    "content": advice.content,
                    "risk_level": advice.risk_level,
                    "created_at": advice.created_at.isoformat()
                })
            
            patients_data.append(patient_dict)
        
        # 保存到文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump({
                "export_time": datetime.now().isoformat(),
                "total_patients": len(patients_data),
                "patients": patients_data
            }, f, ensure_ascii=False, indent=2)
        
        db.close()
        print(f"✅ 数据导出成功: {export_path}")
        return True
        
    except Exception as e:
        print(f"❌ 数据导出失败: {e}")
        return False

def main():
    """主函数"""
    print("🏥 高血压患者医嘱智能体平台 - 数据库管理工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 初始化数据库")
        print("2. 创建示例数据")
        print("3. 检查数据库状态")
        print("4. 备份数据库")
        print("5. 导出数据")
        print("6. 清空数据库")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-6): ").strip()
        
        if choice == "1":
            init_database()
        elif choice == "2":
            create_sample_data()
        elif choice == "3":
            check_database()
        elif choice == "4":
            backup_path = input("输入备份文件路径（回车使用默认路径）: ").strip()
            backup_database(backup_path if backup_path else None)
        elif choice == "5":
            export_path = input("输入导出文件路径（回车使用默认路径）: ").strip()
            export_data(export_path if export_path else None)
        elif choice == "6":
            clear_database()
        elif choice == "0":
            print("再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main()