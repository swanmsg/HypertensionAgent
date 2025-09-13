#!/usr/bin/env python3
"""
阿里云qwen-plus模型测试脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_qwen_model():
    """测试阿里云qwen-plus模型"""
    print("🧪 测试阿里云qwen-plus模型...")
    
    # 检查环境变量
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 缺少DASHSCOPE_API_KEY环境变量")
        print("请在.env文件中设置：DASHSCOPE_API_KEY=your_api_key_here")
        return False
    
    try:
        # 导入必要的库
        from langchain_community.llms import Tongyi
        print("✅ 成功导入Tongyi类")
        
        # 初始化模型
        llm = Tongyi(
            model_name="qwen-plus",
            temperature=0.3,
            max_tokens=500
        )
        print("✅ 成功初始化qwen-plus模型")
        
        # 测试调用
        test_prompt = "请简单介绍一下高血压的定义和分类。"
        print(f"🤖 测试提示: {test_prompt}")
        
        response = llm(test_prompt)
        print(f"📝 模型回复: {response}")
        
        if response and len(response.strip()) > 10:
            print("✅ qwen-plus模型测试成功！")
            return True
        else:
            print("❌ 模型回复为空或过短")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请安装dashscope: pip install dashscope")
        return False
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False

def test_model_switch():
    """测试模型切换功能"""
    print("\n🔄 测试模型切换功能...")
    
    try:
        from app.services.ai_agent import HypertensionAgent
        print("✅ 成功导入HypertensionAgent")
        
        # 创建智能体
        agent = HypertensionAgent()
        print("✅ 成功创建智能体实例")
        
        # 获取模型信息
        model_info = agent.get_model_info()
        print(f"📊 当前模型信息: {model_info}")
        
        if model_info.get('status') == 'online':
            print("✅ 模型状态正常")
            
            # 测试简单对话
            test_question = "什么是高血压？"
            response = agent.chat(test_question)
            
            if "抱歉" not in response and "失败" not in response:
                print("✅ 对话功能测试成功")
                print(f"🤖 AI回复摘要: {response[:100]}...")
                return True
            else:
                print(f"❌ 对话测试失败: {response}")
                return False
        else:
            print("❌ 模型状态异常")
            return False
            
    except Exception as e:
        print(f"❌ 智能体测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🏥 阿里云qwen-plus模型测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # 测试1: 基础模型调用
    if test_qwen_model():
        success_count += 1
    
    # 测试2: 智能体集成
    if test_model_switch():
        success_count += 1
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"通过测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！qwen-plus模型配置成功。")
        print("\n📋 下一步:")
        print("1. 确保.env文件中设置了 LLM_PROVIDER=qwen-plus")
        print("2. 运行 python run.py dev 启动完整服务")
        return True
    else:
        print("❌ 部分测试失败，请检查配置。")
        print("\n🔧 排查建议:")
        print("1. 确认DASHSCOPE_API_KEY正确设置")
        print("2. 检查网络连接")
        print("3. 确认阿里云账户余额充足")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)