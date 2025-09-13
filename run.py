"""
运行脚本
快速启动系统的各个组件
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_requirements():
    """检查环境要求"""
    print("🔍 检查环境要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查依赖文件
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ 未找到requirements.txt文件")
        return False
    
    print("✅ 依赖文件检查通过")
    
    # 检查环境变量文件
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ 未找到.env文件，请复制.env.example并配置")
        return False
    
    print("✅ 环境变量文件检查通过")
    return True

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def init_database():
    """初始化数据库"""
    print("🗄️ 初始化数据库...")
    try:
        from app.models.database import create_tables
        create_tables()
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def start_api_server():
    """启动API服务器"""
    print("🚀 启动API服务器...")
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ API服务器启动中... (端口: 8000)")
        print("📖 API文档: http://localhost:8000/docs")
        return process
    except Exception as e:
        print(f"❌ API服务器启动失败: {e}")
        return None

def start_web_app():
    """启动Web应用"""
    print("🌐 启动Web应用...")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "web/app.py", 
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Web应用启动中... (端口: 8501)")
        print("🌐 访问地址: http://localhost:8501")
        return process
    except Exception as e:
        print(f"❌ Web应用启动失败: {e}")
        return None

def wait_for_service(url, timeout=30):
    """等待服务启动"""
    import requests
    
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def run_setup():
    """运行设置"""
    print("🏥 高血压患者医嘱智能体平台 - 设置向导")
    print("=" * 60)
    
    # 检查环境
    if not check_requirements():
        print("❌ 环境检查失败，请修复后重试")
        return False
    
    # 询问是否安装依赖
    install_deps = input("是否安装/更新依赖包? (y/N): ").strip().lower()
    if install_deps in ['y', 'yes']:
        if not install_dependencies():
            return False
    
    # 初始化数据库
    init_db = input("是否初始化数据库? (y/N): ").strip().lower()
    if init_db in ['y', 'yes']:
        if not init_database():
            return False
    
    # 创建示例数据
    create_sample = input("是否创建示例数据? (y/N): ").strip().lower()
    if create_sample in ['y', 'yes']:
        try:
            subprocess.run([sys.executable, "scripts/db_manager.py"], check=True)
        except Exception as e:
            print(f"⚠️ 示例数据创建失败: {e}")
    
    print("✅ 设置完成！")
    return True

def run_dev():
    """开发模式运行"""
    print("🏥 高血压患者医嘱智能体平台 - 开发模式")
    print("=" * 60)
    
    # 检查环境
    if not check_requirements():
        print("❌ 环境检查失败，请先运行设置: python run.py setup")
        return
    
    processes = []
    
    try:
        # 启动API服务器
        api_process = start_api_server()
        if api_process:
            processes.append(api_process)
            
            # 等待API服务启动
            print("⏳ 等待API服务启动...")
            if wait_for_service("http://localhost:8000", 30):
                print("✅ API服务启动成功")
                
                # 启动Web应用
                web_process = start_web_app()
                if web_process:
                    processes.append(web_process)
                    
                    # 等待Web应用启动
                    print("⏳ 等待Web应用启动...")
                    time.sleep(5)  # Streamlit需要更多时间
                    print("✅ Web应用启动成功")
                    
                    print("\n🎉 系统启动完成！")
                    print("=" * 60)
                    print("📖 API文档: http://localhost:8000/docs")
                    print("🌐 Web应用: http://localhost:8501")
                    print("按 Ctrl+C 停止服务")
                    
                    # 等待用户中断
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 正在停止服务...")
            else:
                print("❌ API服务启动超时")
                
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
    finally:
        # 清理进程
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✅ 服务已停止")

def run_test():
    """运行测试"""
    print("🧪 运行测试套件...")
    
    try:
        # 运行单元测试
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False

def run_validate():
    """运行系统验证"""
    print("🔍 运行系统验证...")
    
    try:
        result = subprocess.run([
            sys.executable, "scripts/system_validator.py"
        ])
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 系统验证失败: {e}")
        return False

def show_help():
    """显示帮助信息"""
    print("""
🏥 高血压患者医嘱智能体平台 - 运行脚本

用法: python run.py <命令>

命令:
  setup     - 运行设置向导（首次使用）
  dev       - 开发模式运行（启动API和Web服务）
  test      - 运行测试套件
  validate  - 运行系统验证
  help      - 显示此帮助信息

示例:
  python run.py setup      # 首次设置
  python run.py dev        # 启动开发服务器
  python run.py test       # 运行所有测试
  python run.py validate   # 验证系统功能

注意:
- 首次使用请先运行 'setup' 命令
- 开发模式需要配置.env文件
- 确保已安装Python 3.8+
    """)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        run_setup()
    elif command == "dev":
        run_dev()
    elif command == "test":
        success = run_test()
        sys.exit(0 if success else 1)
    elif command == "validate":
        success = run_validate()
        sys.exit(0 if success else 1)
    elif command == "help":
        show_help()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()