"""
LangChain智能体核心逻辑
高血压患者医嘱智能生成系统
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# LangChain imports
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import BaseTool
from langchain.schema.messages import BaseMessage, HumanMessage, AIMessage

# 模型导入
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_community.llms import Tongyi
except ImportError:
    Tongyi = None

from app.services.knowledge_service import knowledge_base
from data.rules.medical_rules import HypertensionRuleEngine, PatientProfile

class MedicalKnowledgeTool(BaseTool):
    """医学知识查询工具"""
    name = "medical_knowledge"
    description = "查询高血压相关的医学知识，包括诊疗指南、药物信息、生活方式建议等"
    
    def _run(self, query: str) -> str:
        """执行知识查询"""
        try:
            return knowledge_base.search_knowledge(query)
        except Exception as e:
            return f"知识查询失败: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """异步执行"""
        return self._run(query)

class RiskAssessmentTool(BaseTool):
    """风险评估工具"""
    name = "risk_assessment"
    description = "根据患者信息评估高血压风险等级和心血管风险"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 使用object.__setattr__绕过Pydantic的字段限制
        object.__setattr__(self, 'rule_engine', HypertensionRuleEngine())
    
    def _run(self, patient_data: str) -> str:
        """执行风险评估"""
        try:
            # 解析患者数据
            data = json.loads(patient_data)
            
            patient = PatientProfile(
                age=data.get('age', 50),
                gender=data.get('gender', '男'),
                systolic_bp=data.get('systolic_bp', 120),
                diastolic_bp=data.get('diastolic_bp', 80),
                smoking=data.get('smoking', False),
                diabetes=data.get('diabetes', False),
                family_history=data.get('family_history', False),
                heart_disease=data.get('heart_disease', False),
                kidney_disease=data.get('kidney_disease', False),
                stroke_history=data.get('stroke_history', False),
                bmi=data.get('bmi')
            )
            
            # 生成评估结果
            advice = self.rule_engine.generate_medical_advice(patient)
            return json.dumps(advice, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"风险评估失败: {str(e)}"
    
    async def _arun(self, patient_data: str) -> str:
        return self._run(patient_data)

class MedicationRecommendationTool(BaseTool):
    """药物推荐工具"""
    name = "medication_recommendation" 
    description = "根据患者情况推荐合适的降压药物"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 使用object.__setattr__绕过Pydantic的字段限制
        object.__setattr__(self, 'rule_engine', HypertensionRuleEngine())
    
    def _run(self, patient_data: str) -> str:
        """执行药物推荐"""
        try:
            data = json.loads(patient_data)
            
            patient = PatientProfile(
                age=data.get('age', 50),
                gender=data.get('gender', '男'),
                systolic_bp=data.get('systolic_bp', 120),
                diastolic_bp=data.get('diastolic_bp', 80),
                diabetes=data.get('diabetes', False),
                heart_disease=data.get('heart_disease', False),
                kidney_disease=data.get('kidney_disease', False),
                allergies=data.get('allergies')
            )
            
            medication_advice = self.rule_engine.recommend_medications(patient)
            return json.dumps(medication_advice, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"药物推荐失败: {str(e)}"
    
    async def _arun(self, patient_data: str) -> str:
        return self._run(patient_data)

class HypertensionAgent:
    """高血压医嘱智能体"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        
        # 初始化记忆
        self.memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="history",  # 修改为"history"以匹配ConversationChain的默认提示
            input_key="input"
        )
        
        # 初始化工具
        self.tools = [
            MedicalKnowledgeTool(),
            RiskAssessmentTool(),
            MedicationRecommendationTool()
        ]
        
        # 初始化提示模板
        self.setup_prompts()
        
        # 初始化对话链
        if self.llm:
            self.conversation_chain = ConversationChain(
                llm=self.llm,
                memory=self.memory,
                verbose=True
            )
        else:
            self.conversation_chain = None
    
    def _initialize_llm(self):
        """初始化语言模型"""
        llm_provider = os.getenv("LLM_PROVIDER", "qwen-plus")
        
        try:
            if llm_provider == "openai":
                return self._init_openai_llm()
            elif llm_provider == "qwen-plus":
                return self._init_qwen_llm()
            else:
                print(f"警告: 不支持的模型提供商: {llm_provider}，使用默认qwen-plus")
                return self._init_qwen_llm()
        except Exception as e:
            print(f"警告: 无法初始化模型: {e}")
            print("请检查API Key和网络连接")
            return None
    
    def _init_openai_llm(self):
        """初始化OpenAI模型"""
        if ChatOpenAI is None:
            raise ImportError("需要安装 langchain-openai: pip install langchain-openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("缺少OPENAI_API_KEY环境变量")
        
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=2000,
            openai_api_key=api_key
        )
    
    def _init_qwen_llm(self):
        """初始化通义千问模型"""
        if Tongyi is None:
            raise ImportError("需要安装 dashscope: pip install dashscope")
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("缺少DASHSCOPE_API_KEY环境变量")
        
        # 设置阿里云API Key
        os.environ["DASHSCOPE_API_KEY"] = api_key
        
        return Tongyi(
            model_name="qwen-plus",
            temperature=0.3,
            max_tokens=2000
        )
    
    def setup_prompts(self):
        """设置提示模板"""
        # 系统提示
        self.system_prompt = """
你是一个专业的高血压医疗咨询智能体。你的任务是：

1. 为高血压患者提供专业、准确的医疗建议
2. 根据患者信息评估风险等级
3. 推荐合适的治疗方案和生活方式干预
4. 回答患者关于高血压的各种问题

重要原则：
- 所有建议仅供参考，不能替代专业医生诊断
- 如遇紧急情况，建议立即就医
- 保持专业、温和、易懂的语言风格
- 基于循证医学证据提供建议

可用工具：
- medical_knowledge: 查询医学知识
- risk_assessment: 评估患者风险
- medication_recommendation: 推荐药物治疗

请根据患者咨询内容，提供个性化的医疗建议。
        """
        
        # 医嘱生成模板
        self.advice_template = PromptTemplate(
            input_variables=["patient_info", "assessment_result", "knowledge"],
            template="""
基于以下信息，为患者生成个性化医疗建议：

患者信息：
{patient_info}

风险评估结果：
{assessment_result}

相关医学知识：
{knowledge}

请生成包含以下内容的医疗建议：
1. 血压状况评估
2. 风险等级判断
3. 生活方式干预建议
4. 药物治疗建议（如需要）
5. 监测和随访计划
6. 注意事项和警告

请确保建议专业、实用、易懂。
            """
        )
    
    def generate_medical_advice(self, patient_data: Dict) -> str:
        """生成医疗建议"""
        try:
            if not self.llm:
                return "抱歉，AI服务不可用。请检查API配置。"
                
            # 1. 风险评估
            risk_assessment = self.tools[1]._run(json.dumps(patient_data))
            
            # 2. 获取相关知识
            knowledge = self.tools[0]._run("高血压诊疗指南")
            
            # 3. 生成建议（添加超时处理）
            prompt_text = self.advice_template.format(
                patient_info=json.dumps(patient_data, ensure_ascii=False),
                assessment_result=risk_assessment,
                knowledge=knowledge
            )
            
            # 根据模型类型选择调用方式
            if hasattr(self.llm, '__class__') and 'Tongyi' in str(self.llm.__class__):
                # 通义千问模型，添加超时控制
                try:
                    # 使用简单的超时机制
                    advice = self.llm(prompt_text)
                except Exception as model_error:
                    # 模型调用失败时的降级处理
                    return self._generate_fallback_advice(patient_data, risk_assessment)
            else:
                # OpenAI模型
                try:
                    advice_chain = LLMChain(
                        llm=self.llm,
                        prompt=self.advice_template
                    )
                    advice = advice_chain.run(
                        patient_info=json.dumps(patient_data, ensure_ascii=False),
                        assessment_result=risk_assessment,
                        knowledge=knowledge
                    )
                except Exception as model_error:
                    return self._generate_fallback_advice(patient_data, risk_assessment)
            
            return advice
            
        except Exception as e:
            # 异常时的降级处理
            return self._generate_fallback_advice(patient_data)
    
    def _generate_fallback_advice(self, patient_data: Dict, risk_assessment: str = None) -> str:
        """生成降级医疗建议（不依赖LLM）"""
        try:
            from data.rules.medical_rules import HypertensionRuleEngine, PatientProfile
            
            # 使用规则引擎生成建议
            engine = HypertensionRuleEngine()
            patient = PatientProfile(
                age=patient_data.get('age', 50),
                gender=patient_data.get('gender', '男'),
                systolic_bp=patient_data.get('systolic_bp', 120),
                diastolic_bp=patient_data.get('diastolic_bp', 80),
                smoking=patient_data.get('smoking', False),
                diabetes=patient_data.get('diabetes', False),
                family_history=patient_data.get('family_history', False),
                heart_disease=patient_data.get('heart_disease', False),
                kidney_disease=patient_data.get('kidney_disease', False),
                stroke_history=patient_data.get('stroke_history', False)
            )
            
            advice = engine.generate_medical_advice(patient)
            
            # 格式化输出
            from app.utils.helpers import format_medical_advice
            return format_medical_advice(advice)
            
        except Exception as e:
            return f"生成医疗建议时出错: {str(e)}。请咨询专业医生。"
    
    def chat(self, user_input: str, patient_context: Optional[Dict] = None) -> str:
        """与用户对话"""
        try:
            if not self.conversation_chain:
                return "抱歉，AI服务不可用。请检查API配置。"
            
            # 构建上下文
            context = ""
            if patient_context:
                context = f"\n当前患者信息：{json.dumps(patient_context, ensure_ascii=False)}\n"
            
            # 添加系统提示到对话中
            full_input = f"{self.system_prompt}\n{context}\n用户咨询：{user_input}"
            
            # 根据模型类型选择不同的调用方式
            if isinstance(self.llm, type(Tongyi)) if Tongyi else False:
                # 通义千问模型使用__call__方法
                response = self.llm(full_input)
            else:
                # OpenAI模型使用predict方法
                response = self.conversation_chain.predict(input=full_input)
            
            return response
            
        except Exception as e:
            return f"对话处理失败: {str(e)}"
    
    def analyze_blood_pressure(self, systolic: float, diastolic: float) -> Dict:
        """分析血压数值"""
        try:
            # 创建临时患者档案
            temp_patient = {
                "systolic_bp": systolic,
                "diastolic_bp": diastolic,
                "age": 50,  # 默认值
                "gender": "男"  # 默认值
            }
            
            # 进行风险评估
            assessment = self.tools[1]._run(json.dumps(temp_patient))
            assessment_data = json.loads(assessment)
            
            result = {
                "blood_pressure": f"{int(systolic)}/{int(diastolic)} mmHg",
                "classification": assessment_data["assessment"]["blood_pressure_level"],
                "risk_level": assessment_data["assessment"]["cardiovascular_risk"],
                "target_bp": assessment_data["assessment"]["target_bp"],
                "recommendations": assessment_data["lifestyle_interventions"][:3],  # 前3条建议
                "needs_medication": assessment_data["medication_recommendations"]["needs_medication"]
            }
            
            return result
            
        except Exception as e:
            return {"error": f"血压分析失败: {str(e)}"}
    
    def get_model_info(self) -> Dict[str, str]:
        """获取当前模型信息"""
        if not self.llm:
            return {"provider": "none", "model": "unavailable", "status": "offline"}
        
        if isinstance(self.llm, type(Tongyi)) if Tongyi else False:
            return {
                "provider": "alibaba",
                "model": "qwen-plus",
                "status": "online",
                "description": "阿里百炼通义千问-Plus模型"
            }
        elif ChatOpenAI and isinstance(self.llm, ChatOpenAI):
            return {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "status": "online",
                "description": "OpenAI GPT-3.5 Turbo模型"
            }
        else:
            return {
                "provider": "unknown",
                "model": str(type(self.llm)),
                "status": "online",
                "description": "未知模型类型"
            }
    
    def get_medication_advice(self, patient_data: Dict) -> Dict:
        """获取药物建议"""
        try:
            medication_advice = self.tools[2]._run(json.dumps(patient_data))
            return json.loads(medication_advice)
        except Exception as e:
            return {"error": f"药物建议获取失败: {str(e)}"}
    
    def emergency_check(self, systolic: float, diastolic: float) -> Dict:
        """急症检查"""
        is_emergency = False
        warnings = []
        
        if systolic >= 180 or diastolic >= 110:
            is_emergency = True
            warnings.append("血压严重升高，属于高血压危象")
            warnings.append("建议立即就医，不要等待")
        
        if systolic >= 160 or diastolic >= 100:
            warnings.append("血压明显升高，建议尽快就医")
        
        return {
            "is_emergency": is_emergency,
            "warnings": warnings,
            "emergency_info": knowledge_base.get_emergency_info() if is_emergency else None
        }
    
    def clear_memory(self):
        """清除对话记忆"""
        self.memory.clear()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        messages = self.memory.chat_memory.messages
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        
        return history

# 全局智能体实例（延迟初始化）
hypertension_agent = None

def get_hypertension_agent():
    """获取全局智能体实例"""
    global hypertension_agent
    if hypertension_agent is None:
        hypertension_agent = HypertensionAgent()
    return hypertension_agent