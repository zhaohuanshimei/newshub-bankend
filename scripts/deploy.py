#!/usr/bin/env python3
"""
NewsHub Backend 部署脚本
自动化部署到Railway的辅助工具
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def check_prerequisites():
    """检查部署前置条件"""
    print("🔍 检查部署前置条件...")
    
    # 检查git状态
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("⚠️ 警告: 有未提交的更改")
            print("建议先提交所有更改后再部署")
            return False
    except subprocess.CalledProcessError:
        print("❌ Git检查失败")
        return False
    
    # 检查必要文件
    required_files = [
        'requirements.txt',
        'railway.toml', 
        'Dockerfile',
        'app/main.py'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少必要文件: {file}")
            return False
    
    print("✅ 前置条件检查通过")
    return True

def generate_secret_key():
    """生成强JWT密钥"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    key = ''.join(secrets.choice(alphabet) for i in range(64))
    return key

def create_env_file():
    """创建.env文件"""
    print("📝 创建环境变量文件...")
    
    if Path('.env').exists():
        response = input("⚠️ .env 文件已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("跳过环境变量文件创建")
            return
    
    # 生成JWT密钥
    jwt_secret = generate_secret_key()
    
    env_content = f"""# NewsHub Backend 环境变量
# 自动生成于部署脚本

# JWT认证配置
SECRET_KEY={jwt_secret}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# 应用配置
DEBUG=false
PORT=8000
PYTHONPATH=/app

# Supabase配置 (请填入实际值)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Redis配置 (Railway会自动设置)
REDIS_URL=redis://localhost:6379

# 移动端配置
MOBILE_API_TIMEOUT=30
PAGINATION_DEFAULT_SIZE=20
PAGINATION_MAX_SIZE=100

# 缓存配置
CACHE_TTL_SHORT=300
CACHE_TTL_MEDIUM=1800
CACHE_TTL_LONG=3600

# CORS配置
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://newshub.com,capacitor://localhost,ionic://localhost
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env 文件已创建")
    print("⚠️ 请编辑 .env 文件填入正确的 Supabase 配置")

def test_api():
    """测试API功能"""
    print("🧪 运行API测试...")
    
    try:
        result = subprocess.run([sys.executable, 'test_api.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if "🎉 所有测试通过" in result.stdout:
            print("✅ API测试通过")
            return True
        else:
            print("⚠️ API测试部分失败")
            print("继续部署，但建议检查配置")
            return True
    except subprocess.TimeoutExpired:
        print("⚠️ API测试超时")
        return True
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def check_railway_cli():
    """检查Railway CLI是否安装"""
    try:
        subprocess.run(['railway', '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_railway_cli():
    """安装Railway CLI"""
    print("📦 安装Railway CLI...")
    
    try:
        # 尝试使用npm安装
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI安装成功")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI安装失败")
        print("请手动安装: https://docs.railway.app/develop/cli")
        return False

def push_to_github():
    """推送代码到GitHub"""
    print("📤 推送代码到GitHub...")
    
    try:
        # 添加所有文件
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 提交更改
        commit_msg = "🚀 准备Railway部署 - 更新配置文件"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # 推送到远程
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("✅ 代码已推送到GitHub")
        return True
    except subprocess.CalledProcessError:
        print("❌ 推送失败，请检查Git配置")
        return False

def deploy_to_railway():
    """部署到Railway"""
    print("🚀 开始Railway部署...")
    
    if not check_railway_cli():
        print("未发现Railway CLI，正在安装...")
        if not install_railway_cli():
            return False
    
    try:
        # 登录Railway (如果需要)
        print("请确保已登录Railway CLI (railway login)")
        
        # 初始化Railway项目
        subprocess.run(['railway', 'link'], check=True)
        
        # 部署
        subprocess.run(['railway', 'up'], check=True)
        
        print("✅ Railway部署成功")
        
        # 获取部署URL
        result = subprocess.run(['railway', 'status'], 
                              capture_output=True, text=True, check=True)
        
        print("🌐 部署信息:")
        print(result.stdout)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Railway部署失败: {e}")
        return False

def show_next_steps():
    """显示部署后的下一步操作"""
    print("\n🎉 部署完成！")
    print("=" * 50)
    print("📋 接下来需要做的事情:")
    print()
    print("1. 在Railway控制台配置环境变量:")
    print("   - SECRET_KEY (已生成)")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_ANON_KEY") 
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    print()
    print("2. 添加Redis插件:")
    print("   - 在Railway项目中点击'Add Plugin'")
    print("   - 选择Redis")
    print()
    print("3. 初始化数据库:")
    print("   - 运行: python scripts/init_database.py")
    print("   - 或访问: https://your-app.railway.app/docs")
    print()
    print("4. 测试API:")
    print("   - 健康检查: https://your-app.railway.app/health")
    print("   - API文档: https://your-app.railway.app/docs")
    print()
    print("📖 详细配置请参考: DEPLOYMENT.md")

def main():
    """主部署流程"""
    print("🚀 NewsHub Backend 自动部署脚本")
    print("=" * 40)
    
    # 检查前置条件
    if not check_prerequisites():
        print("❌ 前置条件检查失败，请解决问题后重试")
        sys.exit(1)
    
    # 创建环境变量文件
    create_env_file()
    
    # 测试API (可选)
    test_response = input("是否运行API测试？(y/N): ")
    if test_response.lower() == 'y':
        if not test_api():
            response = input("测试失败，是否继续部署？(y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    # 推送到GitHub
    push_response = input("是否推送代码到GitHub？(Y/n): ")
    if push_response.lower() != 'n':
        if not push_to_github():
            print("❌ GitHub推送失败")
            sys.exit(1)
    
    # 部署到Railway
    deploy_response = input("是否立即部署到Railway？(Y/n): ")
    if deploy_response.lower() != 'n':
        if not deploy_to_railway():
            print("❌ Railway部署失败")
            sys.exit(1)
    
    # 显示后续步骤
    show_next_steps()

if __name__ == "__main__":
    main() 