import asyncio
import os
import json
from twikit import Client
from twikit.errors import TooManyRequests
from dotenv import load_dotenv
import time
from datetime import datetime

# AI 关键词定义
AI_KEYWORDS = {
    'en': [
        # 核心概念
        'AI', 'Artificial Intelligence', 'Machine Learning', 'Deep Learning', 
        'ML', 'DL', 'Neural Network', 'Transformer',
        
        # 大模型相关
        'LLM', 'Large Language Model', 'GPT', 'Claude', 'Gemini', 'Grok',
        'ChatGPT', 'DeepSeek', 'Llama', 'Mistral', 'OpenAI', 'Anthropic',
        'Codex',
        
        # 技术领域
        'NLP', 'Natural Language Processing', 'Computer Vision', 'CV',
        'Agent', 'AI Agent', 'Robotics', 'Reinforcement Learning',
        'Generative AI', 'Gen AI', 'AGI', 'Prompt Engineering',
        
        # 公司/产品
        'Google AI', 'Meta AI', 'DeepMind', 'Stability AI', 
        'Midjourney', 'Stable Diffusion', 'DALL-E',
        
        # 应用
        'Data Science', 'MLOps', 'AI Research', 'AI Safety',
        'Autonomous', 'Automation'
    ],
    'zh': [
        '人工智能', 'AI', '机器学习', '深度学习', '大模型', 
        '大语言模型', 'LLM', 'GPT', 'Claude', 'ChatGPT',
        '通义', '文心', '智谱', '百川', '月之暗面',
        '数据科学', '自然语言处理', '计算机视觉', 
        '强化学习', '生成式AI', 'Agent', '智能体'
    ],
    'ja': [
        'AI', '人工知能', '機械学習', '深層学習', 
        'LLM', 'GPT', 'ChatGPT', 'データサイエンス'
    ]
}

# 最小粉丝数要求
MIN_FOLLOWERS = 10000


async def handle_rate_limit(e: TooManyRequests, context: str = "") -> None:
    """
    处理速率限制，智能计算休眠时间
    
    参数:
        e: TooManyRequests 异常对象
        context: 上下文信息，用于日志输出
    """
    if e.rate_limit_reset:
        reset_time = datetime.fromtimestamp(e.rate_limit_reset)
        current_time = datetime.now()
        sleep_seconds = (reset_time - current_time).total_seconds() + 10  # 加 10 秒缓冲
        sleep_seconds = max(sleep_seconds, 60)  # 至少休眠 60 秒
        
        print(f"  ⚠️  遇到速率限制 (429)")
        if context:
            print(f"  {context}")
        print(f"  当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  重置时间: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  休眠 {int(sleep_seconds)} 秒 ({int(sleep_seconds/60)} 分钟)...")
    else:
        sleep_seconds = 3600  # 默认 1 小时
        print(f"  ⚠️  遇到速率限制 (429)，未获取到重置时间，默认休眠 1 小时...")
        if context:
            print(f"  {context}")
        print(f"  当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await asyncio.sleep(sleep_seconds)
    print(f"  休眠结束，继续执行... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def is_ai_related_user(user, keywords: dict) -> bool:
    """
    检查用户是否为 AI 相关用户
    """
    # 检查粉丝数
    if user.followers_count < MIN_FOLLOWERS:
        return False
    
    # 检查描述是否为空
    if not user.description:
        return False
    
    # 转小写进行关键词匹配
    description_lower = user.description.lower()
    
    # 检查所有语言的关键词
    for lang, keyword_list in keywords.items():
        for keyword in keyword_list:
            if keyword.lower() in description_lower:
                return True
    
    return False


async def get_user_following(client, user_id: str, max_count: int = 200) -> list:
    """
    获取用户的关注列表，支持分页
    
    参数:
        client: Twitter 客户端
        user_id: 用户ID
        max_count: 最多获取多少个关注用户（避免过度请求）
    
    返回:
        关注用户对象列表
    """
    all_following = []
    
    try:
        # 获取第一页（每页20个）
        following_result = await client.get_user_following(user_id, count=200)
        
        # 添加到结果列表
        all_following.extend(following_result)
        
        # 分页获取更多数据
        pages_fetched = 1
        max_pages = (max_count // 20) + 1  # 计算需要获取多少页
        
        while len(all_following) < max_count and pages_fetched < max_pages:
            try:
                # 获取下一页
                following_result = await following_result.next()
                
                if not following_result:  # 没有更多数据
                    break
                
                all_following.extend(following_result)
                pages_fetched += 1
                
                # 延迟避免限流
                await asyncio.sleep(1)
            
            except TooManyRequests as e:
                await handle_rate_limit(e, "分页获取关注列表时")
            except Exception as e:
                print(f"  分页获取出错: {e}")
                break
        
        # 截取到指定数量
        return all_following[:max_count]
    
    except TooManyRequests as e:
        await handle_rate_limit(e, "获取用户关注列表时")
        return []
    except Exception as e:
        print(f"  获取关注列表失败: {e}")
        return []


def extract_user_info(user, depth: int, source: str) -> dict:
    """
    从 User 对象提取需要的信息
    """
    return {
        'screen_name': user.screen_name,
        'name': user.name,
        'id': user.id,
        'description': user.description,
        'followers_count': user.followers_count,
        'following_count': user.following_count,
        'verified': user.verified,
        'profile_url': f"https://x.com/{user.screen_name}",
        'discovered_at_depth': depth,
        'discovered_from': source
    }


def save_progress(progress: dict, filename: str):
    """
    保存进度到文件
    """
    # 将 set 转换为 list 以便 JSON 序列化
    progress_copy = progress.copy()
    progress_copy['processed_users'] = list(progress['processed_users'])
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(progress_copy, f, ensure_ascii=False, indent=2)
    
    print(f"  [进度已保存] 深度:{progress['current_depth']}, "
          f"队列位置:{progress.get('current_queue_index', 0)}/{len(progress.get('queue', []))}")


def load_progress(filename: str) -> dict:
    """
    从文件加载进度
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            progress = json.load(f)
            progress['processed_users'] = set(progress['processed_users'])
            # 确保有 current_queue_index 字段
            if 'current_queue_index' not in progress:
                progress['current_queue_index'] = 0
            return progress
    except FileNotFoundError:
        return None


def load_seed_users(filename: str) -> list:
    """
    加载种子用户列表
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('seed_users', data) if isinstance(data, dict) else data
    except FileNotFoundError:
        return []


async def collect_ai_users(client, seed_users: list, max_depth: int = 5, resume_progress: dict = None) -> dict:
    """
    收集 AI 相关用户，支持断点续传
    """
    # 如果有恢复进度，则从进度恢复
    if resume_progress:
        ai_users = resume_progress['ai_users']
        processed_users = resume_progress['processed_users']
        start_depth = resume_progress['current_depth']
        current_queue = resume_progress['queue']
        start_index = resume_progress.get('current_queue_index', 0)
        
        print(f"\n🔄 从上次进度恢复:")
        print(f"   深度: 第 {start_depth + 1} 层")
        print(f"   已找到: {len(ai_users)} 个 AI 用户")
        print(f"   队列位置: {start_index}/{len(current_queue)}")
    else:
        # 全新开始
        ai_users = {}
        processed_users = set()
        start_depth = 0
        current_queue = seed_users.copy()
        start_index = 0
    
    # 按深度遍历
    for depth in range(start_depth, max_depth):
        print(f"\n=== 开始处理第 {depth + 1} 层 ===")
        print(f"待处理用户数: {len(current_queue)}")
        
        # 如果是恢复的层，从 start_index 开始；否则从 0 开始
        queue_start = start_index if depth == start_depth else 0
        
        next_queue = []
        
        # 处理当前层的每个用户（从指定位置开始）
        for idx in range(queue_start, len(current_queue)):
            screen_name = current_queue[idx]
            # 跳过已处理用户
            if screen_name in processed_users:
                continue
            
            # 标记为已处理
            processed_users.add(screen_name)
            
            try:
                # 获取用户信息
                user = await client.get_user_by_screen_name(screen_name)
                
                # 检查是否符合 AI 用户标准
                if is_ai_related_user(user, AI_KEYWORDS):
                    # 保存用户信息
                    user_info = extract_user_info(user, depth, 'seed' if depth == 0 else 'following')
                    ai_users[screen_name] = user_info
                    print(f"✓ 找到 AI 用户: @{screen_name} (粉丝: {user.followers_count}, 关注: {user.following_count})")
                    
                    # 如果关注数超过 500，跳过获取关注列表
                    if user.following_count > 500:
                        print(f"  ⚠️  关注数 {user.following_count} 超过 500，跳过获取关注列表")
                    else:
                        # 获取该用户的关注列表
                        following_list = await get_user_following(client, user.id, max_count=user.followers_count)
                        print(f"  获取到 {len(following_list)} 个关注用户")
                        
                        # 将关注列表加入下一层队列
                        for followed_user in following_list:
                            if followed_user.screen_name not in processed_users:
                                next_queue.append(followed_user.screen_name)
                else:
                    print(f"✗ 跳过: @{screen_name}")
                
                # 延迟避免限流
                await asyncio.sleep(10)
                
                # 每处理 1 个用户保存一次进度
                progress = {
                    'current_depth': depth,
                    'current_queue_index': idx + 1,  # 记录下一个要处理的位置
                    'processed_users': processed_users,
                    'ai_users': ai_users,
                    'queue': current_queue  # 保存当前层队列
                }
                save_progress(progress, 'progress.json')
            
            except TooManyRequests as e:
                # 保存当前进度
                progress = {
                    'current_depth': depth,
                    'current_queue_index': idx,  # 保持当前位置，下次继续处理这个用户
                    'processed_users': processed_users,
                    'ai_users': ai_users,
                    'queue': current_queue
                }
                save_progress(progress, 'progress.json')
                
                # 处理速率限制
                context = f"处理进度: 第 {depth + 1} 层, 位置 {idx + 1}/{len(current_queue)}"
                await handle_rate_limit(e, context)
                
                # 重试当前用户（不增加 idx，循环会继续）
                continue
                
            except Exception as e:
                print(f"处理用户 @{screen_name} 时出错: {e}")
                continue
        
        # 去重下一层队列
        current_queue = list(set(next_queue))
        
        # 重置索引（下一层从头开始）
        start_index = 0
        
        # 保存本层完成的进度
        progress = {
            'current_depth': depth + 1,  # 下一层深度
            'current_queue_index': 0,     # 下一层从头开始
            'processed_users': processed_users,
            'ai_users': ai_users,
            'queue': current_queue
        }
        save_progress(progress, 'progress.json')
        
        print(f"第 {depth + 1} 层完成，找到 {len(ai_users)} 个 AI 用户")
    
    return ai_users


async def main():
    """
    主入口函数
    """
    # 加载环境变量
    load_dotenv()
    
    # 初始化客户端
    client = Client('en-US')
    client.set_cookies({
        'auth_token': os.getenv('TWITTER_AUTH_TOKEN'),
        'ct0': os.getenv('TWITTER_CT0'),
        'twid': os.getenv('TWITTER_TWID'),
        'kdt': os.getenv('TWITTER_KDT')
    })
    
    # 验证登录
    me = await client.user()
    print(f"当前登录用户: {me.name}\n")
    
    # 检查是否有进度文件
    progress = load_progress('progress.json')
    
    if progress:
        print("=" * 60)
        print("发现上次未完成的进度！")
        print(f"  深度: 第 {progress['current_depth'] + 1} 层")
        print(f"  已找到: {len(progress['ai_users'])} 个 AI 用户")
        print(f"  队列剩余: {len(progress['queue'])} 个用户")
        print(f"  当前位置: {progress.get('current_queue_index', 0)}/{len(progress['queue'])}")
        print("=" * 60)
        
        # 询问是否继续
        response = input("\n是否从上次位置继续？(y/n，直接回车默认 y): ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            print("\n✅ 从上次进度继续...\n")
            # 从进度恢复
            ai_users = await collect_ai_users(
                client, 
                seed_users=[], 
                max_depth=3, 
                resume_progress=progress
            )
        else:
            print("\n❌ 放弃上次进度，重新开始...\n")
            # 删除旧进度文件
            import os as os_module
            if os_module.path.exists('progress.json'):
                os_module.remove('progress.json')
            
            # 读取种子用户，重新开始
            seed_users = load_seed_users('seed_users.json')
            if not seed_users:
                seed_users = ['karpathy', 'AndrewYNg', 'goodfellow_ian']
                print(f"使用默认种子用户: {seed_users}")
            
            ai_users = await collect_ai_users(client, seed_users, max_depth=3)
    else:
        # 没有进度文件，全新开始
        print("📋 开始全新的收集任务...\n")
        seed_users = load_seed_users('seed_users.json')
        if not seed_users:
            seed_users = ['karpathy', 'AndrewYNg', 'goodfellow_ian']
            print(f"使用默认种子用户: {seed_users}")
        
        ai_users = await collect_ai_users(client, seed_users, max_depth=3)
    
    # 保存最终结果
    with open('ai_users_result.json', 'w', encoding='utf-8') as f:
        json.dump(ai_users, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 完成！共找到 {len(ai_users)} 个 AI 领域用户")
    print(f"结果已保存至: ai_users_result.json")
    
    # 清理进度文件
    import os as os_module
    if os_module.path.exists('progress.json'):
        os_module.remove('progress.json')
        print("✓ 进度文件已清理")


if __name__ == '__main__':
    asyncio.run(main())

