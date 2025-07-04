#!/usr/bin/env python3
"""
NewsHub 数据库初始化脚本
在Supabase中创建所需的表结构和初始数据
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user import USER_TABLE_SQL
from app.models.news import NEWS_TABLES_SQL
from app.db.database import get_supabase_admin_client
from app.core.config import settings

async def init_database():
    """初始化数据库表结构"""
    print("🏗️  开始初始化 NewsHub 数据库...")
    
    # 检查Supabase配置
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("❌ 请先配置 Supabase 环境变量:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    try:
        # 获取Supabase管理员客户端
        client = get_supabase_admin_client()
        if not client:
            print("❌ 无法连接到 Supabase")
            return False
        
        print("✅ Supabase 连接成功")
        
        # 1. 创建用户扩展表
        print("📝 创建用户表结构...")
        result = client.rpc('exec_sql', {'sql': USER_TABLE_SQL}).execute()
        if result.data:
            print("✅ 用户表创建成功")
        
        # 2. 创建新闻相关表
        print("📰 创建新闻表结构...")
        result = client.rpc('exec_sql', {'sql': NEWS_TABLES_SQL}).execute()
        if result.data:
            print("✅ 新闻表创建成功")
        
        # 3. 插入初始分类数据
        print("🏷️  插入初始新闻分类...")
        categories_data = [
            {
                "name": "technology",
                "display_name": "科技",
                "description": "科技新闻和创新资讯",
                "color": "#2196F3",
                "sort_order": 1
            },
            {
                "name": "business", 
                "display_name": "商业",
                "description": "商业资讯和财经新闻",
                "color": "#4CAF50",
                "sort_order": 2
            },
            {
                "name": "sports",
                "display_name": "体育", 
                "description": "体育赛事和运动资讯",
                "color": "#FF9800",
                "sort_order": 3
            },
            {
                "name": "entertainment",
                "display_name": "娱乐",
                "description": "娱乐八卦和影视资讯", 
                "color": "#E91E63",
                "sort_order": 4
            },
            {
                "name": "health",
                "display_name": "健康",
                "description": "健康养生和医疗资讯",
                "color": "#009688",
                "sort_order": 5
            },
            {
                "name": "world",
                "display_name": "国际",
                "description": "国际新闻和全球资讯",
                "color": "#673AB7",
                "sort_order": 6
            }
        ]
        
        result = client.table('categories').upsert(categories_data).execute()
        if result.data:
            print(f"✅ 插入 {len(categories_data)} 个新闻分类")
        
        # 4. 创建RLS策略 (行级安全)
        print("🔒 配置行级安全策略...")
        rls_policies = """
        -- 启用行级安全
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE news ENABLE ROW LEVEL SECURITY;
        ALTER TABLE user_news_interactions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE news_comments ENABLE ROW LEVEL SECURITY;
        
        -- 用户表策略
        CREATE POLICY "Users can view own profile" ON users 
            FOR SELECT USING (auth_id = auth.uid());
        
        CREATE POLICY "Users can update own profile" ON users 
            FOR UPDATE USING (auth_id = auth.uid());
        
        -- 新闻表策略 (公开读取)
        CREATE POLICY "Anyone can view published news" ON news 
            FOR SELECT USING (status = 'published');
        
        -- 用户互动策略
        CREATE POLICY "Users can manage own interactions" ON user_news_interactions 
            FOR ALL USING (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()));
        
        -- 评论策略
        CREATE POLICY "Users can view all comments" ON news_comments 
            FOR SELECT USING (true);
        
        CREATE POLICY "Users can manage own comments" ON news_comments 
            FOR ALL USING (user_id IN (SELECT id FROM users WHERE auth_id = auth.uid()));
        """
        
        result = client.rpc('exec_sql', {'sql': rls_policies}).execute()
        if result.data:
            print("✅ 行级安全策略配置成功")
        
        print("\n🎉 数据库初始化完成!")
        print("📱 移动端友好的表结构已就绪")
        print("🔒 安全策略已配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def main():
    """主函数"""
    success = asyncio.run(init_database())
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 