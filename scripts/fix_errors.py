#!/usr/bin/env python3
"""
错误修复验证脚本
检查并修复常见的Python导入和语法错误
"""

import ast
import sys
import os
import importlib.util
from pathlib import Path

def check_syntax(file_path):
    """检查Python文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"其他错误: {e}"

def check_imports(file_path):
    """检查导入语句"""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('from ') or line.startswith('import '):
                # 简单检查常见导入错误
                if 'langchain.llms' in line and 'OpenAI' in line:
                    errors.append(f"第{i}行: 建议使用 'from langchain_openai import OpenAI'")
                elif 'langchain.chat_models' in line and 'ChatOpenAI' in line:
                    errors.append(f"第{i}行: 建议使用 'from langchain_openai import ChatOpenAI'")
                elif 'model_name=' in line:
                    errors.append(f"第{i}行: ChatOpenAI参数应使用 'model=' 而不是 'model_name='")
    
    except Exception as e:
        errors.append(f"读取文件失败: {e}")
    
    return errors

def validate_project():
    """验证整个项目"""
    print("🔍 开始项目错误检查...")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    python_files = list(project_root.rglob("*.py"))
    
    syntax_errors = []
    import_warnings = []
    
    for py_file in python_files:
        # 跳过__pycache__和.env等
        if '__pycache__' in str(py_file) or '.venv' in str(py_file):
            continue
        
        print(f"检查文件: {py_file.relative_to(project_root)}")
        
        # 检查语法
        is_valid, error_msg = check_syntax(py_file)
        if not is_valid:
            syntax_errors.append(f"{py_file.relative_to(project_root)}: {error_msg}")
        
        # 检查导入
        import_errs = check_imports(py_file)
        if import_errs:
            import_warnings.extend([f"{py_file.relative_to(project_root)}: {err}" for err in import_errs])
    
    print("\n" + "=" * 50)
    print("📊 检查结果")
    print("=" * 50)
    
    if syntax_errors:
        print("\n❌ 语法错误:")
        for error in syntax_errors:
            print(f"  - {error}")
    else:
        print("\n✅ 无语法错误")
    
    if import_warnings:
        print("\n⚠️ 导入警告:")
        for warning in import_warnings:
            print(f"  - {warning}")
    else:
        print("\n✅ 导入检查通过")
    
    # 检查关键文件是否存在
    print("\n📁 文件结构检查:")
    required_files = [
        "requirements.txt",
        ".env.example",
        "app/main.py",
        "app/models/database.py",
        "app/services/ai_agent.py",
        "web/app.py",
        "run.py"
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")
    
    # 总结
    total_issues = len(syntax_errors) + len(import_warnings)
    if total_issues == 0:
        print(f"\n🎉 项目检查完成！没有发现严重问题。")
        return True
    else:
        print(f"\n⚠️ 项目检查完成，发现 {total_issues} 个问题需要注意。")
        return False

def main():
    """主函数"""
    print("🏥 高血压患者医嘱智能体平台 - 错误修复验证")
    
    success = validate_project()
    
    if success:
        print("\n✅ 所有检查通过！可以尝试运行项目:")
        print("   python run.py setup  # 首次设置")
        print("   python run.py dev    # 启动开发服务器")
    else:
        print("\n🔧 请根据上述提示修复问题后重新运行验证。")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()