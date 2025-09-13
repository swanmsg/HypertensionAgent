#!/usr/bin/env python3
"""
Streamlit Web应用启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动Streamlit应用"""
    # 确保在正确的目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 设置环境变量
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_CLIENT_SHOW_ERROR_DETAILS"] = "true"
    
    # 启动命令
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "web/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    print("🚀 启动Streamlit Web应用...")
    print(f"📍 Web地址: http://localhost:8501")
    print(f"🔧 启动命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n⏹️ 用户停止了Web应用")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())