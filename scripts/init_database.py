#!/usr/bin/env python3
"""
NewsHub 数据库初始化脚本
创建表结构、索引、RLS策略等
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from supabase import create_client
from app.core.config import settings

def get_supabase_admin_client():
    """获取Supabase管理员客户端"""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("❌ 请先配置SUPABASE_URL和SUPABASE_SERVICE_ROLE_KEY环境变量")
        sys.exit(1)
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def create_users_table(supabase):
    """创建用户表"""
    print("📝 创建用户表...")
    
    sql = """
    -- 用户表 (利用Supabase Auth)
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
        username VARCHAR(50) UNIQUE NOT NULL,
        full_name VARCHAR(100),
        avatar_url TEXT,
        device_id VARCHAR(255),
        push_token TEXT,
        preferences JSONB DEFAULT '{"categories": [], "notification_enabled": true, "theme": "light", "language": "zh-CN"}',
        read_count INTEGER DEFAULT 0,
        favorite_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        last_login_at TIMESTAMP WITH TIME ZONE
    );

    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_users_auth_id ON users(auth_id);
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_device_id ON users(device_id);

    -- 创建更新时间触发器
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    CREATE TRIGGER IF NOT EXISTS update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    try:
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 用户表创建成功")
        return True
    except Exception as e:
        print(f"❌ 用户表创建失败: {e}")
        return False

def create_categories_table(supabase):
    """创建新闻分类表"""
    print("📝 创建新闻分类表...")
    
    sql = """
    -- 新闻分类表
    CREATE TABLE IF NOT EXISTS categories (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(50) UNIQUE NOT NULL,
        display_name VARCHAR(100) NOT NULL,
        description TEXT,
        icon_url TEXT,
        color VARCHAR(7), -- 十六进制颜色
        sort_order INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- 插入默认分类
    INSERT INTO categories (name, display_name, description, color, sort_order) VALUES
    ('technology', '科技', '科技新闻和数码产品', '#2563eb', 1),
    ('business', '商业', '商业资讯和经济新闻', '#dc2626', 2),
    ('sports', '体育', '体育赛事和运动新闻', '#16a34a', 3),
    ('entertainment', '娱乐', '娱乐八卦和影视资讯', '#db2777', 4),
    ('health', '健康', '健康养生和医疗资讯', '#059669', 5),
    ('science', '科学', '科学发现和学术研究', '#7c3aed', 6),
    ('politics', '政治', '政治新闻和时事评论', '#ea580c', 7),
    ('world', '国际', '国际新闻和全球资讯', '#0891b2', 8),
    ('local', '本地', '本地新闻和城市资讯', '#65a30d', 9)
    ON CONFLICT (name) DO NOTHING;
    """
    
    try:
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 新闻分类表创建成功")
        return True
    except Exception as e:
        print(f"❌ 新闻分类表创建失败: {e}")
        return False

def create_news_table(supabase):
    """创建新闻表"""
    print("📝 创建新闻表...")
    
    sql = """
    -- 新闻文章表
    CREATE TABLE IF NOT EXISTS news (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        slug VARCHAR(255) UNIQUE NOT NULL,
        title TEXT NOT NULL,
        summary TEXT,
        content TEXT,
        category VARCHAR(50) REFERENCES categories(name),
        tags TEXT[] DEFAULT '{}',
        author VARCHAR(100),
        source_url TEXT,
        
        -- 移动端优化字段
        featured_image TEXT,
        thumbnail_image TEXT,
        reading_time INTEGER DEFAULT 0,
        
        -- 统计数据
        view_count INTEGER DEFAULT 0,
        like_count INTEGER DEFAULT 0,
        comment_count INTEGER DEFAULT 0,
        share_count INTEGER DEFAULT 0,
        
        -- 状态和时间
        status VARCHAR(20) DEFAULT 'published',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        published_at TIMESTAMP WITH TIME ZONE,
        
        -- 移动端元数据
        metadata JSONB DEFAULT '{"mobile_optimized": true, "image_sizes": {}, "external_links": [], "related_news": []}'
    );

    -- 创建索引 (移动端查询优化)
    CREATE INDEX IF NOT EXISTS idx_news_category ON news(category);
    CREATE INDEX IF NOT EXISTS idx_news_status ON news(status);
    CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at DESC);
    CREATE INDEX IF NOT EXISTS idx_news_view_count ON news(view_count DESC);
    CREATE INDEX IF NOT EXISTS idx_news_like_count ON news(like_count DESC);
    CREATE INDEX IF NOT EXISTS idx_news_tags ON news USING GIN(tags);

    -- 更新触发器
    CREATE TRIGGER IF NOT EXISTS update_news_updated_at 
    BEFORE UPDATE ON news
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    try:
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 新闻表创建成功")
        return True
    except Exception as e:
        print(f"❌ 新闻表创建失败: {e}")
        return False

def create_user_interactions_table(supabase):
    """创建用户互动表"""
    print("📝 创建用户互动表...")
    
    sql = """
    -- 用户新闻互动表 (点赞、收藏、分享)
    CREATE TABLE IF NOT EXISTS user_news_interactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        news_id UUID REFERENCES news(id) ON DELETE CASCADE,
        interaction_type VARCHAR(20) NOT NULL, -- 'like', 'favorite', 'share', 'view'
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        
        UNIQUE(user_id, news_id, interaction_type)
    );

    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_news_interactions(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_interactions_news_id ON user_news_interactions(news_id);
    CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_news_interactions(interaction_type);
    """
    
    try:
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 用户互动表创建成功")
        return True
    except Exception as e:
        print(f"❌ 用户互动表创建失败: {e}")
        return False

def create_comments_table(supabase):
    """创建评论表"""
    print("📝 创建评论表...")
    
    sql = """
    -- 新闻评论表
    CREATE TABLE IF NOT EXISTS news_comments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        news_id UUID REFERENCES news(id) ON DELETE CASCADE,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        parent_id UUID REFERENCES news_comments(id) ON DELETE CASCADE, -- 支持回复
        content TEXT NOT NULL,
        like_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_comments_news_id ON news_comments(news_id);
    CREATE INDEX IF NOT EXISTS idx_comments_user_id ON news_comments(user_id);
    CREATE INDEX IF NOT EXISTS idx_comments_created_at ON news_comments(created_at DESC);

    -- 更新触发器
    CREATE TRIGGER IF NOT EXISTS update_comments_updated_at 
    BEFORE UPDATE ON news_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    try:
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 评论表创建成功")
        return True
    except Exception as e:
        print(f"❌ 评论表创建失败: {e}")
        return False

def setup_rls_policies(supabase):
    """设置行级安全策略(RLS)"""
    print("🔒 设置行级安全策略...")
    
    policies = [
        # 启用RLS
        "ALTER TABLE users ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE news ENABLE ROW LEVEL SECURITY;", 
        "ALTER TABLE user_news_interactions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE news_comments ENABLE ROW LEVEL SECURITY;",
        
        # 用户表策略
        """
        CREATE POLICY "Users can view own profile" ON users
        FOR SELECT USING (auth.uid() = auth_id);
        """,
        """
        CREATE POLICY "Users can update own profile" ON users  
        FOR UPDATE USING (auth.uid() = auth_id);
        """,
        
        # 新闻表策略 - 所有人可读，只有发布的新闻
        """
        CREATE POLICY "Anyone can read published news" ON news
        FOR SELECT USING (status = 'published');
        """,
        
        # 用户互动策略
        """
        CREATE POLICY "Users can manage own interactions" ON user_news_interactions
        FOR ALL USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));
        """,
        
        # 评论策略
        """
        CREATE POLICY "Anyone can read comments" ON news_comments
        FOR SELECT USING (true);
        """,
        """
        CREATE POLICY "Authenticated users can create comments" ON news_comments
        FOR INSERT WITH CHECK (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));
        """,
        """
        CREATE POLICY "Users can update own comments" ON news_comments
        FOR UPDATE USING (auth.uid() = (SELECT auth_id FROM users WHERE id = user_id));
        """
    ]
    
    success_count = 0
    for policy in policies:
        try:
            supabase.rpc('exec_sql', {'sql': policy}).execute()
            success_count += 1
        except Exception as e:
            print(f"⚠️ 策略设置失败: {e}")
    
    print(f"✅ RLS策略设置完成 ({success_count}/{len(policies)} 成功)")
    return success_count > 0

def create_sample_data(supabase):
    """创建示例数据"""
    print("📝 创建示例数据...")
    
    sql = """
    -- 插入示例新闻数据
    INSERT INTO news (slug, title, summary, content, category, tags, author, featured_image, reading_time, published_at) VALUES
    (
        'welcome-to-newshub',
        '欢迎来到NewsHub - 您的移动新闻聚合平台',
        'NewsHub是一个专为移动端优化的新闻聚合平台，为您提供最新、最热的新闻资讯。',
        '# 欢迎来到NewsHub\n\nNewsHub是一个全新的移动端新闻聚合平台，致力于为用户提供高质量的新闻阅读体验。\n\n## 主要特性\n\n- 📱 移动端优化设计\n- 🔍 智能新闻推荐\n- 💬 用户互动功能\n- 🎯 个性化分类\n\n立即开始您的新闻阅读之旅吧！',
        'technology',
        ARRAY['欢迎', '介绍', '新功能'],
        'NewsHub团队',
        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800',
        3,
        NOW()
    ),
    (
        'mobile-optimization-guide',
        '移动端优化：提升用户体验的关键策略',
        '了解如何通过移动端优化技术，显著提升用户的阅读体验和应用性能。',
        '# 移动端优化指南\n\n在当今移动为先的时代，优化移动端体验至关重要。\n\n## 优化策略\n\n1. **响应式设计** - 适配各种屏幕尺寸\n2. **加载速度优化** - 减少资源大小\n3. **触摸友好** - 合适的按钮大小\n4. **离线支持** - 缓存关键内容\n\n通过这些策略，可以大幅提升用户满意度。',
        'technology',
        ARRAY['移动端', '优化', 'UX'],
        'Tech Writer',
        'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800',
        5,
        NOW() - INTERVAL '1 hour'
    ),
    (
        'latest-business-trends',
        '2024年商业趋势：数字化转型持续深化',
        '探索2024年最重要的商业趋势，了解数字化转型如何重塑各行各业。',
        '# 2024年商业趋势分析\n\n数字化转型继续成为企业发展的核心驱动力。\n\n## 主要趋势\n\n- **AI集成** - 人工智能在业务流程中的应用\n- **远程工作** - 混合办公模式的普及\n- **可持续发展** - ESG理念的实施\n- **客户体验** - 个性化服务的重要性\n\n企业需要积极拥抱这些变化以保持竞争优势。',
        'business',
        ARRAY['商业', '趋势', '数字化'],
        'Business Analyst',
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800',
        7,
        NOW() - INTERVAL '2 hours'
    )
    ON CONFLICT (slug) DO NOTHING;
    """
    
    try:
        supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ 示例数据创建成功")
        return True
    except Exception as e:
        print(f"❌ 示例数据创建失败: {e}")
        return False

def main():
    """主初始化流程"""
    print("🚀 NewsHub 数据库初始化")
    print("=" * 40)
    
    # 检查环境变量
    if not settings.SUPABASE_URL:
        print("❌ 请先设置SUPABASE_URL环境变量")
        print("💡 提示: 复制 env.template 为 .env 并填入配置")
        sys.exit(1)
    
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("❌ 请先设置SUPABASE_SERVICE_ROLE_KEY环境变量")
        sys.exit(1)
    
    # 连接Supabase
    print(f"🔗 连接Supabase: {settings.SUPABASE_URL}")
    try:
        supabase = get_supabase_admin_client()
        print("✅ Supabase连接成功")
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        sys.exit(1)
    
    # 执行初始化步骤
    steps = [
        ("创建用户表", create_users_table),
        ("创建分类表", create_categories_table), 
        ("创建新闻表", create_news_table),
        ("创建互动表", create_user_interactions_table),
        ("创建评论表", create_comments_table),
        ("设置安全策略", setup_rls_policies),
        ("创建示例数据", create_sample_data)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if step_func(supabase):
            success_count += 1
        else:
            print(f"⚠️ {step_name}失败，但继续执行...")
    
    print("\n" + "=" * 40)
    print(f"📊 初始化完成: {success_count}/{len(steps)} 步骤成功")
    
    if success_count == len(steps):
        print("🎉 数据库初始化完全成功！")
        print("\n📋 接下来可以:")
        print("1. 启动应用: python -m app.main")
        print("2. 测试API: python test_api.py")
        print("3. 访问文档: http://localhost:8000/docs")
    else:
        print("⚠️ 部分步骤失败，请检查错误信息")
        print("💡 可以重新运行此脚本来修复问题")

if __name__ == "__main__":
    main() 