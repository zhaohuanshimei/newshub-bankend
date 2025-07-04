#!/usr/bin/env python3
"""
NewsHub Backend 启动脚本
便捷的开发服务器启动工具
"""
import uvicorn
import os
import sys

def main():
    """启动开发服务器"""
    # 确保在正确的目录
    if not os.path.exists("app"):
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    print("🚀 启动 NewsHub Backend API...")
    print("📱 移动端友好的新闻聚合后端服务")
    print("🔗 API文档: http://localhost:8000/docs")
    print("💝 健康检查: http://localhost:8000/health")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式自动重载
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 