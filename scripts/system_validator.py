"""
系统集成验证脚本
验证整个系统的功能完整性
"""

import os
import sys
import requests
import time
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import create_tables
from data.rules.medical_rules import HypertensionRuleEngine, PatientProfile

class SystemValidator:
    """系统验证器"""
    
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_api_connectivity(self):
        """检查API连接"""
        try:
            response = requests.get(f"{self.api_base_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test("API连接", True, "API服务正常运行")
                return True
            else:
                self.log_test("API连接", False, f"API返回状态码: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("API连接", False, f"无法连接到API: {e}")
            return False
    
    def test_database_operations(self):
        """测试数据库操作"""
        try:
            # 测试数据库初始化
            create_tables()
            self.log_test("数据库初始化", True, "数据库表创建成功")
            
            # 测试患者创建
            patient_data = {
                "name": "系统验证测试患者",
                "age": 55,
                "gender": "男",
                "height": 170.0,
                "weight": 75.0,
                "systolic_bp": 150.0,
                "diastolic_bp": 95.0,
                "smoking": True,
                "diabetes": False
            }
            
            response = requests.post(
                f"{self.api_base_url}/patients/",
                json=patient_data,
                timeout=10
            )
            
            if response.status_code == 200:
                patient = response.json()
                self.log_test("患者创建", True, f"患者ID: {patient['id']}")
                return patient['id']
            else:
                self.log_test("患者创建", False, f"创建失败: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("数据库操作", False, f"数据库操作失败: {e}")
            return None
    
    def test_blood_pressure_management(self, patient_id):
        """测试血压管理功能"""
        if not patient_id:
            self.log_test("血压管理", False, "缺少患者ID")
            return
        
        try:
            # 创建血压记录
            bp_data = {
                "patient_id": patient_id,
                "systolic_bp": 155.0,
                "diastolic_bp": 98.0,
                "heart_rate": 78,
                "measurement_time": datetime.now().isoformat(),
                "measurement_location": "左臂"
            }
            
            response = requests.post(
                f"{self.api_base_url}/blood-pressure/",
                json=bp_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("血压记录创建", True, "血压记录创建成功")
                
                # 获取血压记录
                response = requests.get(
                    f"{self.api_base_url}/blood-pressure/patient/{patient_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    records = response.json()
                    self.log_test("血压记录查询", True, f"找到 {len(records)} 条记录")
                else:
                    self.log_test("血压记录查询", False, "查询失败")
            else:
                self.log_test("血压记录创建", False, f"创建失败: {response.text}")
                
        except Exception as e:
            self.log_test("血压管理", False, f"血压管理测试失败: {e}")
    
    def test_ai_services(self):
        """测试AI服务"""
        try:
            # 测试模型信息
            response = requests.get(
                f"{self.api_base_url}/ai/model-info",
                timeout=10
            )
            
            if response.status_code == 200:
                model_info = response.json()
                model_desc = model_info.get('description', '未知模型')
                model_status = model_info.get('status', 'offline')
                self.log_test("AI模型信息", True, f"模型: {model_desc} ({model_status})")
            else:
                self.log_test("AI模型信息", False, "模型信息获取失败")
            # 测试血压分析
            response = requests.post(
                f"{self.api_base_url}/ai/analyze-blood-pressure?systolic=150&diastolic=95",
                timeout=15
            )
            
            if response.status_code == 200:
                analysis = response.json()
                self.log_test("AI血压分析", True, f"分级: {analysis.get('classification', '未知')}")
            else:
                self.log_test("AI血压分析", False, f"分析失败: {response.text}")
            
            # 测试医疗建议生成（增加超时时间和降级处理）
            patient_data = {
                "age": 60,
                "gender": "男",
                "systolic_bp": 165,
                "diastolic_bp": 105,
                "diabetes": True,
                "smoking": True
            }
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/ai/generate-advice",
                    json=patient_data,
                    timeout=45  # 增加超时时间到45秒
                )
                
                if response.status_code == 200:
                    advice = response.json()
                    self.log_test("AI医疗建议", True, "医疗建议生成成功")
                else:
                    self.log_test("AI医疗建议", False, f"生成失败: {response.text}")
                    
            except requests.exceptions.Timeout:
                # 超时时的降级处理
                self.log_test("AI医疗建议", False, "AI服务响应超时，可能是网络或API配置问题")
            
            # 测试药物推荐
            try:
                response = requests.post(
                    f"{self.api_base_url}/ai/medication-advice",
                    json=patient_data,
                    timeout=20  # 适度增加超时时间
                )
                
                if response.status_code == 200:
                    medication = response.json()
                    needs_med = medication.get('needs_medication', False)
                    self.log_test("AI药物推荐", True, f"需要药物治疗: {needs_med}")
                else:
                    self.log_test("AI药物推荐", False, f"推荐失败: {response.text}")
                    
            except requests.exceptions.Timeout:
                self.log_test("AI药物推荐", False, "药物推荐服务响应超时")
                
        except requests.exceptions.Timeout as e:
            self.log_test("AI服务", False, f"AI服务响应超时: {e}")
        except Exception as e:
            self.log_test("AI服务", False, f"AI服务测试失败: {e}")
    
    def test_knowledge_base(self):
        """测试知识库"""
        try:
            # 测试知识搜索
            response = requests.get(
                f"{self.api_base_url}/knowledge/search?query=血压分类",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("知识库搜索", True, "搜索功能正常")
            else:
                self.log_test("知识库搜索", False, f"搜索失败: {response.text}")
            
            # 测试血压分类信息
            response = requests.get(
                f"{self.api_base_url}/knowledge/blood-pressure-classification",
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("血压分类信息", True, "血压分类信息获取成功")
            else:
                self.log_test("血压分类信息", False, "信息获取失败")
                
        except Exception as e:
            self.log_test("知识库", False, f"知识库测试失败: {e}")
    
    def test_rule_engine(self):
        """测试规则引擎"""
        try:
            engine = HypertensionRuleEngine()
            
            # 测试血压分级
            bp_level = engine.classify_blood_pressure(150, 95)
            self.log_test("血压分级", True, f"分级结果: {bp_level.value}")
            
            # 测试风险评估
            patient = PatientProfile(
                age=60, gender="男", systolic_bp=160, diastolic_bp=100,
                smoking=True, diabetes=True
            )
            
            risk = engine.assess_cardiovascular_risk(patient)
            self.log_test("风险评估", True, f"风险等级: {risk.value}")
            
            # 测试生活方式建议
            lifestyle = engine.recommend_lifestyle_interventions(patient)
            self.log_test("生活方式建议", True, f"生成 {len(lifestyle)} 条建议")
            
            # 测试药物推荐
            medication = engine.recommend_medications(patient)
            self.log_test("药物推荐", True, f"需要药物治疗: {medication['needs_medication']}")
            
        except Exception as e:
            self.log_test("规则引擎", False, f"规则引擎测试失败: {e}")
    
    def test_data_validation(self):
        """测试数据验证"""
        try:
            # 测试无效血压值
            response = requests.post(
                f"{self.api_base_url}/ai/analyze-blood-pressure?systolic=50&diastolic=200",
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("数据验证", True, "无效血压值被正确拒绝")
            else:
                self.log_test("数据验证", False, "无效数据未被拒绝")
            
            # 测试无效患者数据
            invalid_patient = {
                "name": "",
                "age": -5,
                "gender": "无效性别"
            }
            
            response = requests.post(
                f"{self.api_base_url}/patients/",
                json=invalid_patient,
                timeout=10
            )
            
            if response.status_code in [400, 422]:
                self.log_test("患者数据验证", True, "无效患者数据被正确拒绝")
            else:
                self.log_test("患者数据验证", False, "无效患者数据未被拒绝")
                
        except Exception as e:
            self.log_test("数据验证", False, f"数据验证测试失败: {e}")
    
    def test_emergency_detection(self):
        """测试急症检测"""
        try:
            # 测试高血压危象检测
            response = requests.post(
                f"{self.api_base_url}/ai/analyze-blood-pressure?systolic=190&diastolic=120",
                timeout=10
            )
            
            if response.status_code == 200:
                analysis = response.json()
                if analysis.get('is_emergency'):
                    self.log_test("急症检测", True, "高血压危象被正确识别")
                else:
                    self.log_test("急症检测", False, "高血压危象未被识别")
            else:
                self.log_test("急症检测", False, "急症检测请求失败")
                
        except Exception as e:
            self.log_test("急症检测", False, f"急症检测测试失败: {e}")
    
    def run_full_validation(self):
        """运行完整的系统验证"""
        print("🏥 开始系统集成验证...")
        print("=" * 60)
        
        # 1. 检查API连接
        if not self.check_api_connectivity():
            print("\n❌ API服务未运行，请先启动API服务")
            return False
        
        # 2. 测试数据库操作
        patient_id = self.test_database_operations()
        
        # 3. 测试血压管理
        self.test_blood_pressure_management(patient_id)
        
        # 4. 测试AI服务
        self.test_ai_services()
        
        # 5. 测试知识库
        self.test_knowledge_base()
        
        # 6. 测试规则引擎
        self.test_rule_engine()
        
        # 7. 测试数据验证
        self.test_data_validation()
        
        # 8. 测试急症检测
        self.test_emergency_detection()
        
        # 生成验证报告
        self.generate_report()
        
        return self.get_overall_result()
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "=" * 60)
        print("📊 系统验证报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        # 保存详细报告
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "validation_time": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "test_results": self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存至: {report_file}")
    
    def get_overall_result(self):
        """获取总体验证结果"""
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        if success_rate >= 90:
            print("\n🎉 系统验证通过！所有核心功能正常运行。")
            return True
        elif success_rate >= 70:
            print("\n⚠️ 系统基本可用，但存在一些问题需要修复。")
            return False
        else:
            print("\n❌ 系统验证失败，存在严重问题需要修复。")
            return False

def main():
    """主函数"""
    print("🏥 高血压患者医嘱智能体平台 - 系统验证工具")
    
    # 检查是否有API URL参数
    api_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    print(f"API服务地址: {api_url}")
    print("请确保API服务已启动...")
    
    # 等待用户确认
    input("按Enter键开始验证...")
    
    # 创建验证器并运行验证
    validator = SystemValidator(api_url)
    success = validator.run_full_validation()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()