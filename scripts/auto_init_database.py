#!/usr/bin/env python3
"""
自动化数据库初始化脚本
使用PostgreSQL连接直接执行SQL文件
"""
import os
import sys
from pathlib import Path
import re

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

load_env_file()

def get_postgres_connection_string():
    """从Supabase URL构建PostgreSQL连接字符串"""
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_key:
        raise ValueError("缺少SUPABASE_URL或SUPABASE_SERVICE_ROLE_KEY")
    
    # 从Supabase URL提取项目信息
    # https://xxxx.supabase.co -> xxxx
    match = re.match(r'https://([^.]+)\.supabase\.co', supabase_url)
    if not match:
        raise ValueError(f"无法解析Supabase URL: {supabase_url}")
    
    project_ref = match.group(1)
    
    # 构建PostgreSQL连接字符串
    postgres_url = f"postgresql://postgres:{service_key}@db.{project_ref}.supabase.co:5432/postgres"
    return postgres_url

def execute_sql_file_with_psycopg2(sql_file_path):
    """使用psycopg2执行SQL文件"""
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2未安装")
        print("💡 安装命令: pip install psycopg2-binary")
        return False
    
    try:
        postgres_url = get_postgres_connection_string()
        
        # 读取SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 连接数据库并执行SQL
        with psycopg2.connect(postgres_url) as conn:
            with conn.cursor() as cursor:
                # 分割SQL语句（简单处理）
                sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for i, stmt in enumerate(sql_statements):
                    try:
                        cursor.execute(stmt)
                        conn.commit()
                        print(f"  ✅ 执行语句 {i+1}/{len(sql_statements)}")
                    except Exception as e:
                        print(f"  ⚠️ 语句 {i+1} 执行失败: {e}")
                        # 继续执行下一条语句
                        conn.rollback()
        
        return True
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def execute_sql_file_with_requests():
    """使用HTTP请求执行SQL（备用方案）"""
    try:
        import requests
    except ImportError:
        print("❌ requests未安装")
        print("💡 安装命令: pip install requests")
        return False
    
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # 读取SQL文件
        sql_file_path = project_root / 'sql_scripts' / '01_create_tables.sql'
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 尝试通过REST API执行（可能不支持）
        headers = {
            'apikey': service_key,
            'Authorization': f'Bearer {service_key}',
            'Content-Type': 'application/json'
        }
        
        # 分割成多个语句
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for stmt in sql_statements:
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={'sql': stmt}
            )
            if response.status_code != 200:
                print(f"❌ SQL执行失败: {response.text}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def check_and_install_psycopg2():
    """检查并安装psycopg2"""
    try:
        import psycopg2
        print("✅ psycopg2已安装")
        return True
    except ImportError:
        print("📦 安装psycopg2...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'])
            print("✅ psycopg2安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ psycopg2安装失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 NewsHub 数据库自动初始化")
    print("=" * 50)
    
    # 检查SQL文件
    sql_files = [
        '01_create_tables.sql',
        '02_setup_rls.sql', 
        '03_sample_data.sql'
    ]
    
    sql_dir = project_root / 'sql_scripts'
    missing_files = []
    
    for sql_file in sql_files:
        if not (sql_dir / sql_file).exists():
            missing_files.append(sql_file)
    
    if missing_files:
        print(f"❌ 缺少SQL文件: {', '.join(missing_files)}")
        return False
    
    print("✅ SQL文件检查通过")
    
    # 检查并安装依赖
    if not check_and_install_psycopg2():
        print("❌ 无法安装必要依赖")
        return False
    
    # 执行SQL文件
    success_count = 0
    for sql_file in sql_files:
        print(f"\n📄 执行 {sql_file}...")
        sql_path = sql_dir / sql_file
        
        if execute_sql_file_with_psycopg2(sql_path):
            print(f"✅ {sql_file} 执行成功")
            success_count += 1
        else:
            print(f"❌ {sql_file} 执行失败")
    
    print("\n" + "=" * 50)
    print(f"📊 执行结果: {success_count}/{len(sql_files)} 成功")
    
    if success_count == len(sql_files):
        print("🎉 数据库初始化完成！")
        print("\n📋 接下来可以:")
        print("1. 运行测试: python scripts/test_supabase.py")
        print("2. 启动应用: python -m app.main")
        return True
    else:
        print("⚠️ 部分脚本执行失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 