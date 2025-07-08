# 🚀 Supabase配置完整指南

> 本指南将一步步带你完成Supabase项目的创建和配置

## 📋 配置步骤概览

1. ✅ 创建Supabase账号和项目
2. ✅ 获取API密钥和项目信息
3. ✅ 配置环境变量
4. ✅ 运行数据库初始化脚本
5. ✅ 验证配置

---

## 1️⃣ 创建Supabase账号和项目

### 1.1 注册账号
1. 🌐 访问 [https://supabase.com](https://supabase.com)
2. 🆕 点击 **"Start your project"** 或 **"Sign Up"**
3. 🔑 推荐使用GitHub账号登录（更便捷）

### 1.2 创建新项目
登录后创建项目：

1. 📊 点击 **"New Project"** 按钮
2. 🏢 选择组织（首次使用会自动创建）
3. 📝 填写项目信息：
   ```
   Project Name: newshub-backend
   Database Password: 创建一个强密码（至少8位，包含大小写字母、数字、特殊字符）
   Region: Southeast Asia (Singapore) - 推荐亚洲用户
   ```
4. ✨ 点击 **"Create new project"**
5. ⏳ 等待1-2分钟项目创建完成

### 1.3 获取项目配置信息
项目创建完成后：

1. 🔗 进入项目仪表板
2. 📡 点击左侧菜单 **Settings** → **API**
3. 📝 记录以下重要信息：

| 配置项 | 位置 | 说明 |
|--------|------|------|
| **Project URL** | Project URL 栏 | `https://your-project-id.supabase.co` |
| **anon public** | Project API keys 栏 | 匿名公开密钥，客户端使用 |
| **service_role** | Project API keys 栏 | 服务端密钥，点击👁️图标显示 |

---

## 2️⃣ 配置环境变量

### 2.1 复制环境变量模板
```bash
# 复制模板文件
cp env.template .env

# 编辑环境变量文件
nano .env  # 或使用 vim/code
```

### 2.2 填写Supabase配置
在 `.env` 文件中找到以下配置并填入你的信息：

```bash
# ==================== Supabase 配置 ====================
# 项目URL (从仪表板Settings->API获取)
SUPABASE_URL=https://your-project-id.supabase.co

# 匿名公开密钥 (前端使用)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 服务端密钥 (后端使用，保密！)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 数据库直连URL (可选，高级用法)
SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres
```

### 2.3 配置其他必要环境变量
```bash
# JWT密钥 (随机生成)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Redis配置 (Railway部署会自动配置)
REDIS_URL=redis://localhost:6379

# 应用配置
API_VERSION=v1
DEBUG=true
ENVIRONMENT=development
```

---

## 3️⃣ 运行数据库初始化脚本

### 3.1 确保环境正确
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖 (如果还没安装)
pip install -r requirements.txt

# 验证Supabase连接
python -c "from supabase import create_client; print('✅ Supabase库可用')"
```

### 3.2 运行初始化脚本
```bash
# 执行数据库初始化
python scripts/init_database.py
```

**脚本执行内容：**
- 📋 创建用户表（与Supabase Auth集成）
- 🗂️ 创建新闻分类表并插入默认分类
- 📰 创建新闻文章表（移动端优化）
- 💬 创建用户互动表（点赞、收藏、分享）
- 💭 创建评论表（支持嵌套回复）
- 🔒 设置行级安全策略(RLS)
- 📝 插入示例数据

### 3.3 预期输出
```
🚀 NewsHub 数据库初始化
========================================
🔗 连接Supabase: https://your-project-id.supabase.co
✅ Supabase连接成功

📋 创建用户表
📝 创建用户表...
✅ 用户表创建成功

📋 创建分类表
📝 创建新闻分类表...
✅ 新闻分类表创建成功

... (其他步骤)

========================================
📊 初始化完成: 7/7 步骤成功
🎉 数据库初始化完全成功！

📋 接下来可以:
1. 启动应用: python -m app.main
2. 测试API: python test_api.py
3. 访问文档: http://localhost:8000/docs
```

---

## 4️⃣ 验证配置

### 4.1 启动应用验证
```bash
# 启动开发服务器
python -m app.main

# 期望看到:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

### 4.2 测试API连接
```bash
# 在新终端窗口运行
python test_api.py

# 检查输出中的数据库相关测试
```

### 4.3 检查Supabase仪表板
1. 🗃️ 返回Supabase项目仪表板
2. 📊 点击 **"Table Editor"**
3. ✅ 确认看到创建的表：
   - `users` - 用户表
   - `categories` - 分类表
   - `news` - 新闻表
   - `user_news_interactions` - 用户互动表
   - `news_comments` - 评论表

---

## 🔧 常见问题解决

### ❌ 连接失败
**错误信息：** `Supabase连接失败`
**解决方案：**
1. 检查网络连接
2. 确认SUPABASE_URL格式正确
3. 验证SUPABASE_SERVICE_ROLE_KEY没有复制错误

### ❌ 权限错误
**错误信息：** `permission denied` 或 `insufficient privileges`
**解决方案：**
1. 确保使用的是SERVICE_ROLE_KEY，不是ANON_KEY
2. 检查密钥是否完整（很长的JWT字符串）

### ❌ 表已存在错误
**错误信息：** `table already exists`
**解决方案：**
- 这是正常的，脚本使用`CREATE TABLE IF NOT EXISTS`
- 可以安全地重新运行脚本

### ❌ SQL执行错误
**解决方案：**
1. 检查Supabase项目是否正常运行
2. 可以在Supabase仪表板的SQL Editor中手动执行SQL
3. 重新运行初始化脚本

---

## 📱 移动端集成配置

### 4.1 获取配置信息
初始化完成后，你的移动端应用需要以下配置：

```typescript
// Capacitor/Ionic应用配置
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',  // 开发环境
  // apiUrl: 'https://your-app.railway.app',  // 生产环境
  supabase: {
    url: 'https://your-project-id.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  }
};
```

### 4.2 验证移动端连接
```bash
# 测试API可访问性
curl http://localhost:8000/api/v1/news/

# 期望返回新闻列表JSON数据
```

---

## 🎯 下一步

配置完成后，你可以：

1. 🚀 **部署到Railway** - 使用 `python scripts/deploy.py`
2. 📱 **连接移动应用** - 配置Ionic/Capacitor应用
3. 🔧 **自定义功能** - 添加更多API端点
4. 📊 **监控和分析** - 查看Supabase仪表板统计

---

## 📞 获取帮助

如果遇到问题：

1. 🔍 检查 [Supabase文档](https://supabase.com/docs)
2. 💬 查看项目的 `DEPLOYMENT.md` 文件
3. 🐛 查看应用日志: `tail -f app.log`

---

**🎉 恭喜！你的NewsHub Supabase配置已完成！** 