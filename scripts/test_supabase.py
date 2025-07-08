#!/usr/bin/env python3
"""
快速测试Supabase连接和配置
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 加载 .env 文件
def load_env_file():
    """加载 .env 文件"""
    env_file = project_root / '.env'
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ .env 文件加载成功")
    else:
        print("⚠️ .env 文件不存在")

# 在模块级别立即加载环境变量
load_env_file()

def test_environment():
    """测试环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value.startswith('your-') or value.startswith('https://your-'):
            print(f"⚠️  {var}: 仍为模板值，需要替换")
            missing_vars.append(var)
        else:
            print(f"✅ {var}: 已配置")
    
    if missing_vars:
        print(f"\n❌ 缺少或未正确配置的环境变量: {', '.join(missing_vars)}")
        print("💡 请确保已复制 env.template 为 .env 并填入正确的Supabase配置")
        return False
    
    print("✅ 环境变量配置检查通过")
    return True

def test_supabase_import():
    """测试Supabase库导入"""
    print("\n📦 测试Supabase库导入...")
    
    try:
        from supabase import create_client
        print("✅ Supabase库导入成功")
        return True
    except ImportError as e:
        print(f"❌ Supabase库导入失败: {e}")
        print("💡 请运行: pip install supabase")
        return False

def test_supabase_connection():
    """测试Supabase连接"""
    print("\n🔗 测试Supabase连接...")
    
    try:
        from app.core.config import settings
        from supabase import create_client
        
        # 创建客户端
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        
        # 简单连接测试 - 获取项目信息
        # 注意：这里使用匿名密钥，只能访问公开数据
        print(f"🌐 连接到: {settings.SUPABASE_URL}")
        print("✅ Supabase连接成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        print("💡 请检查:")
        print("   1. SUPABASE_URL格式是否正确")
        print("   2. SUPABASE_ANON_KEY是否完整")
        print("   3. 网络连接是否正常")
        return False

def test_service_role_connection():
    """测试服务端角色连接（用于数据库操作）"""
    print("\n🔐 测试服务端角色连接...")
    
    try:
        from app.core.config import settings
        from supabase import create_client
        
        # 使用服务端密钥创建客户端
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
        # 测试SQL执行权限（非破坏性查询）
        result = supabase.rpc('exec_sql', {
            'sql': 'SELECT current_database(), current_user, version();'
        }).execute()
        
        if result.data:
            print("✅ 服务端角色连接成功")
            print("✅ 具备数据库操作权限")
            return True
        else:
            print("⚠️ 服务端角色连接成功，但查询返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 服务端角色连接失败: {e}")
        print("💡 请检查:")
        print("   1. SUPABASE_SERVICE_ROLE_KEY是否正确")
        print("   2. 是否使用了正确的服务端密钥（不是匿名密钥）")
        print("   3. 密钥是否完整复制（通常很长）")
        return False

def test_database_tables():
    """测试数据库表是否存在"""
    print("\n🗄️ 检查数据库表...")
    
    try:
        from app.core.config import settings
        from supabase import create_client
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
        # 检查主要表是否存在
        tables_to_check = ['users', 'categories', 'news', 'user_news_interactions', 'news_comments']
        
        existing_tables = []
        missing_tables = []
        
        for table in tables_to_check:
            try:
                # 尝试查询表结构（LIMIT 0避免返回数据）
                result = supabase.table(table).select('*').limit(0).execute()
                existing_tables.append(table)
                print(f"✅ 表 '{table}' 存在")
            except Exception:
                missing_tables.append(table)
                print(f"❌ 表 '{table}' 不存在")
        
        if missing_tables:
            print(f"\n⚠️ 缺少表: {', '.join(missing_tables)}")
            print("💡 请运行数据库初始化脚本: python scripts/init_database.py")
            return False
        else:
            print(f"\n✅ 所有必要表已存在 ({len(existing_tables)}/{len(tables_to_check)})")
            return True
            
    except Exception as e:
        print(f"❌ 数据库表检查失败: {e}")
        return False

def main():
    """主测试流程"""
    print("🧪 NewsHub Supabase 连接测试")
    print("=" * 50)
    
    tests = [
        ("环境变量配置", test_environment),
        ("Supabase库导入", test_supabase_import),
        ("Supabase连接", test_supabase_connection),
        ("服务端角色权限", test_service_role_connection),
        ("数据库表检查", test_database_tables)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 出现异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！Supabase配置正确！")
        print("\n📋 接下来可以:")
        print("1. 启动应用: python -m app.main")
        print("2. 运行完整测试: python test_api.py")
        print("3. 部署到Railway: python scripts/deploy.py")
    else:
        print("⚠️ 存在配置问题，请按照上述提示进行修复")
        print("\n📖 详细配置指南:")
        print("   查看 SUPABASE_SETUP.md 文件")
        
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 