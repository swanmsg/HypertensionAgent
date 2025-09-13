"""
知识库管理服务
负责加载和管理医学知识库
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path

class KnowledgeBase:
    """医学知识库管理"""
    
    def __init__(self, knowledge_dir: str = None):
        if knowledge_dir is None:
            knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge")
        
        self.knowledge_dir = Path(knowledge_dir)
        self.guidelines = {}
        self.medications = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        """加载知识库内容"""
        try:
            # 加载诊疗指南
            guidelines_file = self.knowledge_dir / "hypertension_guidelines.md"
            if guidelines_file.exists():
                with open(guidelines_file, 'r', encoding='utf-8') as f:
                    self.guidelines['content'] = f.read()
            
            # 加载药物信息
            medications_file = self.knowledge_dir / "medications.md"
            if medications_file.exists():
                with open(medications_file, 'r', encoding='utf-8') as f:
                    self.medications['content'] = f.read()
            
            print("知识库加载完成")
        except Exception as e:
            print(f"知识库加载失败: {e}")
    
    def get_bp_classification_info(self) -> str:
        """获取血压分类信息"""
        return """
血压分类标准（中国高血压防治指南2018）：

1. 正常血压：收缩压 < 120 mmHg 且舒张压 < 80 mmHg
2. 正常高值：收缩压 120-139 mmHg 和/或舒张压 80-89 mmHg  
3. 1级高血压：收缩压 140-159 mmHg 和/或舒张压 90-99 mmHg
4. 2级高血压：收缩压 160-179 mmHg 和/或舒张压 100-109 mmHg
5. 3级高血压：收缩压 ≥ 180 mmHg 和/或舒张压 ≥ 110 mmHg
6. 单纯收缩期高血压：收缩压 ≥ 140 mmHg 且舒张压 < 90 mmHg
        """
    
    def get_risk_factors_info(self) -> str:
        """获取危险因素信息"""
        return """
高血压危险因素：

1. 不可改变因素：
   - 年龄：男性 ≥ 55岁，女性 ≥ 65岁
   - 家族史：直系亲属有高血压史
   - 性别：男性风险更高

2. 可改变因素：
   - 吸烟
   - 血脂异常
   - 糖尿病
   - 肥胖（BMI ≥ 28 kg/m²）
   - 缺乏体力活动
   - 高盐饮食
   - 过量饮酒
   - 精神压力过大
        """
    
    def get_medication_info(self, drug_type: str = None) -> str:
        """获取药物信息"""
        if drug_type:
            # 返回特定类型药物信息
            drug_info = {
                "ACEI": """
ACEI类药物（血管紧张素转换酶抑制剂）：
- 代表药物：依那普利、卡托普利、赖诺普利
- 适应症：高血压、心力衰竭、糖尿病肾病
- 优势：心肾保护作用强
- 不良反应：干咳、高血钾
- 禁忌症：妊娠、血管性水肿史
                """,
                "ARB": """
ARB类药物（血管紧张素受体阻滞剂）：
- 代表药物：氯沙坦、缬沙坦、厄贝沙坦
- 适应症：高血压、糖尿病肾病、心力衰竭
- 优势：干咳发生率低，心肾保护作用
- 不良反应：高血钾、头晕
- 禁忌症：妊娠、双侧肾动脉狭窄
                """,
                "CCB": """
钙通道阻滞剂（CCB）：
- 代表药物：氨氯地平、硝苯地平、非洛地平
- 适应症：高血压、冠心病、老年高血压
- 优势：降压效果强，适用于老年患者
- 不良反应：踝部水肿、牙龈增生
- 注意事项：缓释制剂不可咀嚼
                """,
                "利尿剂": """
利尿剂：
- 代表药物：氢氯噻嗪、吲达帕胺、呋塞米
- 适应症：高血压、心力衰竭、水肿
- 优势：价格便宜，适用于老年患者
- 不良反应：低血钾、高尿酸、糖耐量异常
- 注意事项：监测电解质平衡
                """,
                "β受体阻滞剂": """
β受体阻滞剂：
- 代表药物：美托洛尔、比索洛尔、阿替洛尔
- 适应症：高血压、冠心病、心力衰竭
- 优势：心脏保护作用，抗心律失常
- 不良反应：心动过缓、支气管痉挛
- 禁忌症：哮喘、严重心动过缓
                """
            }
            return drug_info.get(drug_type, "未找到该类型药物信息")
        
        return self.medications.get('content', '药物信息加载中...')
    
    def get_lifestyle_recommendations(self) -> str:
        """获取生活方式建议"""
        return """
高血压患者生活方式干预建议：

1. 饮食调节：
   - 减少钠盐摄入：每日食盐 < 6g
   - 增加钾摄入：多吃新鲜蔬果
   - 控制体重：BMI保持在18.5-23.9
   - 限制饮酒：男性<25g/日，女性<15g/日

2. 运动锻炼：
   - 有氧运动：每周150分钟中等强度
   - 阻抗运动：每周2-3次
   - 避免突然用力的动作

3. 戒烟限酒：
   - 完全戒烟，避免被动吸烟
   - 限制酒精摄入

4. 心理调节：
   - 减轻精神压力
   - 保持心理平衡
   - 充足睡眠：7-8小时/晚

5. 规律监测：
   - 定期测量血压
   - 记录血压日记
   - 定期体检
        """
    
    def get_treatment_targets(self) -> str:
        """获取治疗目标"""
        return """
高血压治疗目标：

1. 一般患者：< 140/90 mmHg

2. 特殊人群：
   - 糖尿病患者：< 130/80 mmHg
   - 慢性肾病患者：< 130/80 mmHg
   - 老年患者（≥65岁）：< 150/90 mmHg
   - 冠心病患者：< 130/80 mmHg

3. 降压原则：
   - 平稳降压，避免血压剧烈波动
   - 个体化治疗方案
   - 达标后长期维持治疗
        """
    
    def search_knowledge(self, query: str) -> str:
        """搜索知识库"""
        query_lower = query.lower()
        results = []
        
        # 关键词映射
        keyword_map = {
            "血压分类": self.get_bp_classification_info,
            "危险因素": self.get_risk_factors_info,
            "生活方式": self.get_lifestyle_recommendations,
            "治疗目标": self.get_treatment_targets,
            "药物": lambda: self.get_medication_info(),
        }
        
        for keyword, func in keyword_map.items():
            if keyword in query_lower:
                results.append(func())
        
        if not results:
            results.append("抱歉，没有找到相关信息。请尝试搜索：血压分类、危险因素、生活方式、治疗目标、药物等关键词。")
        
        return "\n\n".join(results)
    
    def get_emergency_info(self) -> str:
        """获取急症处理信息"""
        return """
高血压急症处理：

1. 高血压危象（收缩压≥180mmHg或舒张压≥110mmHg）：
   - 立即就医
   - 避免血压急剧下降
   - 目标：第一小时降压幅度不超过25%

2. 高血压急症症状：
   - 剧烈头痛
   - 视力模糊
   - 胸痛
   - 呼吸困难
   - 神经系统症状

3. 紧急处理：
   - 保持冷静，安静休息
   - 立即测量血压
   - 如有急症症状，立即拨打120
   - 不要自行服用短效降压药

警告：高血压急症是医疗急症，需要专业医疗处理！
        """

# 全局知识库实例
knowledge_base = KnowledgeBase()