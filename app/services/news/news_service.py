"""
新闻服务层
处理新闻获取、搜索、统计、用户互动
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import Client

from app.models.news import NewsCategory, NewsPublic, NewsListResponse

class NewsService:
    def __init__(self, db: Client):
        self.db = db
    
    async def get_news_list(
        self,
        page: int = 1,
        size: int = 20,
        category: Optional[NewsCategory] = None,
        keyword: Optional[str] = None,
        sort: str = "published_at",
        order: str = "desc"
    ) -> NewsListResponse:
        """获取新闻列表"""
        try:
            # 构建查询
            query = self.db.table('news').select('*')
            
            # 只显示已发布的新闻
            query = query.eq('status', 'published')
            
            # 分类筛选
            if category:
                query = query.eq('category', category.value)
            
            # 关键词搜索
            if keyword:
                query = query.or_(f'title.ilike.%{keyword}%,summary.ilike.%{keyword}%')
            
            # 排序
            if order == "desc":
                query = query.order(sort, desc=True)
            else:
                query = query.order(sort, desc=False)
            
            # 分页
            offset = (page - 1) * size
            query = query.range(offset, offset + size - 1)
            
            # 执行查询
            result = query.execute()
            
            # 获取总数
            count_query = self.db.table('news').select('id', count='exact')
            if category:
                count_query = count_query.eq('category', category.value)
            if keyword:
                count_query = count_query.or_(f'title.ilike.%{keyword}%,summary.ilike.%{keyword}%')
            
            count_result = count_query.execute()
            total = count_result.count or 0
            
            # 转换为响应格式
            items = []
            for news_data in result.data:
                items.append(NewsPublic(
                    id=news_data['id'],
                    slug=news_data['slug'],
                    title=news_data['title'],
                    summary=news_data.get('summary'),
                    category=NewsCategory(news_data['category']),
                    tags=news_data.get('tags', []),
                    author=news_data.get('author'),
                    featured_image=news_data.get('featured_image'),
                    thumbnail_image=news_data.get('thumbnail_image'),
                    reading_time=news_data.get('reading_time', 0),
                    view_count=news_data.get('view_count', 0),
                    like_count=news_data.get('like_count', 0),
                    created_at=news_data['created_at'],
                    published_at=news_data.get('published_at')
                ))
            
            return NewsListResponse(
                items=items,
                total=total,
                page=page,
                size=size,
                has_next=total > page * size
            )
            
        except Exception as e:
            raise Exception(f"获取新闻列表失败: {str(e)}")
    
    async def get_news_detail(self, news_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取新闻详情"""
        try:
            # 获取新闻
            news_result = self.db.table('news').select('*').eq('id', news_id).eq('status', 'published').execute()
            if not news_result.data:
                raise ValueError("新闻不存在")
            
            news_data = news_result.data[0]
            
            # 增加浏览量
            self.db.table('news').update({
                'view_count': news_data['view_count'] + 1
            }).eq('id', news_id).execute()
            
            # 记录用户浏览行为
            if user_id:
                self._record_user_interaction(user_id, news_id, 'view')
            
            # 获取用户互动状态
            user_interactions = {}
            if user_id:
                interactions_result = self.db.table('user_news_interactions').select('interaction_type').eq('user_id', user_id).eq('news_id', news_id).execute()
                user_interactions = {item['interaction_type']: True for item in interactions_result.data}
            
            # 构建响应
            return {
                'id': news_data['id'],
                'slug': news_data['slug'],
                'title': news_data['title'],
                'summary': news_data.get('summary'),
                'content': news_data.get('content'),
                'category': news_data['category'],
                'tags': news_data.get('tags', []),
                'author': news_data.get('author'),
                'source_url': news_data.get('source_url'),
                'featured_image': news_data.get('featured_image'),
                'thumbnail_image': news_data.get('thumbnail_image'),
                'reading_time': news_data.get('reading_time', 0),
                'view_count': news_data['view_count'] + 1,  # 返回更新后的浏览量
                'like_count': news_data.get('like_count', 0),
                'comment_count': news_data.get('comment_count', 0),
                'share_count': news_data.get('share_count', 0),
                'created_at': news_data['created_at'],
                'published_at': news_data.get('published_at'),
                'metadata': news_data.get('metadata', {}),
                'user_interactions': user_interactions  # 用户互动状态
            }
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"获取新闻详情失败: {str(e)}")
    
    async def toggle_news_like(self, news_id: str, user_id: str) -> Dict[str, Any]:
        """切换新闻点赞状态"""
        try:
            # 检查新闻是否存在
            news_result = self.db.table('news').select('id, like_count').eq('id', news_id).execute()
            if not news_result.data:
                raise ValueError("新闻不存在")
            
            news_data = news_result.data[0]
            
            # 检查是否已点赞
            like_result = self.db.table('user_news_interactions').select('*').eq('user_id', user_id).eq('news_id', news_id).eq('interaction_type', 'like').execute()
            
            if like_result.data:
                # 取消点赞
                self.db.table('user_news_interactions').delete().eq('user_id', user_id).eq('news_id', news_id).eq('interaction_type', 'like').execute()
                new_like_count = max(0, news_data['like_count'] - 1)
                action = "unliked"
            else:
                # 添加点赞
                self.db.table('user_news_interactions').insert({
                    'user_id': user_id,
                    'news_id': news_id,
                    'interaction_type': 'like'
                }).execute()
                new_like_count = news_data['like_count'] + 1
                action = "liked"
            
            # 更新新闻点赞数
            self.db.table('news').update({
                'like_count': new_like_count
            }).eq('id', news_id).execute()
            
            return {
                'action': action,
                'like_count': new_like_count,
                'is_liked': action == "liked"
            }
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"点赞操作失败: {str(e)}")
    
    async def toggle_news_favorite(self, news_id: str, user_id: str) -> Dict[str, Any]:
        """切换新闻收藏状态"""
        try:
            # 检查新闻是否存在
            news_result = self.db.table('news').select('id').eq('id', news_id).execute()
            if not news_result.data:
                raise ValueError("新闻不存在")
            
            # 检查是否已收藏
            favorite_result = self.db.table('user_news_interactions').select('*').eq('user_id', user_id).eq('news_id', news_id).eq('interaction_type', 'favorite').execute()
            
            if favorite_result.data:
                # 取消收藏
                self.db.table('user_news_interactions').delete().eq('user_id', user_id).eq('news_id', news_id).eq('interaction_type', 'favorite').execute()
                action = "unfavorited"
            else:
                # 添加收藏
                self.db.table('user_news_interactions').insert({
                    'user_id': user_id,
                    'news_id': news_id,
                    'interaction_type': 'favorite'
                }).execute()
                action = "favorited"
            
            return {
                'action': action,
                'is_favorited': action == "favorited"
            }
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"收藏操作失败: {str(e)}")
    
    async def share_news(self, news_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """分享新闻"""
        try:
            # 检查新闻是否存在
            news_result = self.db.table('news').select('id, share_count, title').eq('id', news_id).execute()
            if not news_result.data:
                raise ValueError("新闻不存在")
            
            news_data = news_result.data[0]
            
            # 更新分享数
            new_share_count = news_data['share_count'] + 1
            self.db.table('news').update({
                'share_count': new_share_count
            }).eq('id', news_id).execute()
            
            # 记录用户分享行为
            if user_id:
                self._record_user_interaction(user_id, news_id, 'share')
            
            return {
                'share_count': new_share_count,
                'share_url': f"/news/{news_id}",  # 可以根据实际需求生成完整URL
                'title': news_data['title']
            }
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"分享操作失败: {str(e)}")
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """获取新闻分类列表"""
        try:
            # 从数据库获取分类
            categories_result = self.db.table('categories').select('*').eq('is_active', True).order('sort_order').execute()
            
            categories = []
            for cat_data in categories_result.data:
                categories.append({
                    'id': cat_data['id'],
                    'name': cat_data['name'],
                    'display_name': cat_data['display_name'],
                    'description': cat_data.get('description'),
                    'icon_url': cat_data.get('icon_url'),
                    'color': cat_data.get('color'),
                    'sort_order': cat_data.get('sort_order', 0)
                })
            
            return categories
            
        except Exception as e:
            raise Exception(f"获取分类列表失败: {str(e)}")
    
    async def get_trending_news(self, limit: int = 10) -> List[NewsPublic]:
        """获取热门新闻"""
        try:
            # 基于浏览量和点赞数的综合热度排序
            result = self.db.table('news').select('*').eq('status', 'published').order('view_count', desc=True).order('like_count', desc=True).limit(limit).execute()
            
            trending_news = []
            for news_data in result.data:
                trending_news.append(NewsPublic(
                    id=news_data['id'],
                    slug=news_data['slug'],
                    title=news_data['title'],
                    summary=news_data.get('summary'),
                    category=NewsCategory(news_data['category']),
                    tags=news_data.get('tags', []),
                    author=news_data.get('author'),
                    featured_image=news_data.get('featured_image'),
                    thumbnail_image=news_data.get('thumbnail_image'),
                    reading_time=news_data.get('reading_time', 0),
                    view_count=news_data.get('view_count', 0),
                    like_count=news_data.get('like_count', 0),
                    created_at=news_data['created_at'],
                    published_at=news_data.get('published_at')
                ))
            
            return trending_news
            
        except Exception as e:
            raise Exception(f"获取热门新闻失败: {str(e)}")
    
    async def upsert_news_batch(self, news_list: List[dict]) -> int:
        """
        批量upsert新闻（按slug唯一），返回成功写入的数量
        """
        if not news_list:
            return 0
        upsert_data = []
        for item in news_list:
            upsert_data.append({
                "title": item.get("title"),
                "summary": item.get("summary"),
                "content": item.get("content", ""),  # RSS一般无正文
                "category": item.get("category") or "technology",  # 默认分类
                "tags": item.get("tags", []),
                "author": item.get("author"),
                "source_url": item.get("link"),
                "slug": item.get("guid") or item.get("link"),
                "status": "published",
                "published_at": item.get("published"),
            })
        # 按slug唯一键upsert
        result = self.db.table("news").upsert(upsert_data, on_conflict="slug").execute()
        return len(result.data) if hasattr(result, "data") and result.data else 0

    def _record_user_interaction(self, user_id: str, news_id: str, interaction_type: str):
        """记录用户互动行为"""
        try:
            # 使用upsert避免重复记录
            self.db.table('user_news_interactions').upsert({
                'user_id': user_id,
                'news_id': news_id,
                'interaction_type': interaction_type,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception:
            pass  # 记录失败不影响主要功能 