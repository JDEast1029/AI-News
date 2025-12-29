"""
用户领域识别工具
用于识别Twitter用户是否属于特定领域（如AI、加密货币等）
"""

import asyncio
from typing import List, Dict, Optional
from twikit import Client, User

# AI/机器学习领域关键词
AI_KEYWORDS = {
    'en': [
        'AI', 'Artificial Intelligence', 'Machine Learning', 'ML', 'Deep Learning',
        'Neural Network', 'LLM', 'GPT', 'Claude', 'Gemini', 'ChatGPT',
        'Data Science', 'NLP', 'Computer Vision', 'Robotics',
        'OpenAI', 'Anthropic', 'Google AI', 'Meta AI', 'DeepMind'
    ],
    'zh': [
        '人工智能', 'AI', '机器学习', '深度学习', '大模型', 'LLM',
        'GPT', 'Claude', 'ChatGPT', '数据科学', '自然语言处理'
    ],
    'ja': [
        'AI', '人工知能', '機械学習', '深層学習', 'LLM', 'GPT'
    ]
}

# 其他领域关键词示例
CRYPTO_KEYWORDS = ['crypto', 'blockchain', 'bitcoin', 'ethereum', 'web3', 'NFT', 'DeFi']
TECH_KEYWORDS = ['developer', 'engineer', 'programming', 'software', 'tech', 'coding']


def check_user_domain_by_description(user: User, domain_keywords: List[str], min_match: int = 1) -> bool:
    """
    通过用户描述判断用户领域
    
    Args:
        user: User对象
        domain_keywords: 领域关键词列表
        min_match: 最少匹配关键词数量
    
    Returns:
        bool: 是否属于该领域
    """
    if not user.description:
        return False
    
    description_lower = user.description.lower()
    match_count = sum(1 for keyword in domain_keywords if keyword.lower() in description_lower)
    
    return match_count >= min_match


def check_user_domain_by_screen_name(user: User, domain_keywords: List[str]) -> bool:
    """
    通过用户名判断用户领域
    """
    screen_name_lower = user.screen_name.lower()
    return any(keyword.lower() in screen_name_lower for keyword in domain_keywords)


async def analyze_user_tweets_for_domain(
    client: Client,
    user: User, 
    domain_keywords: List[str], 
    tweet_count: int = 20
) -> Dict:
    """
    分析用户推文内容，判断是否属于特定领域
    
    Args:
        client: Client对象
        user: User对象
        domain_keywords: 领域关键词列表
        tweet_count: 分析的推文数量
    
    Returns:
        dict: 包含匹配分数和匹配的关键词
    """
    try:
        tweets = await user.get_tweets('Tweets', count=tweet_count)
        
        keyword_matches = {}
        total_tweets = 0
        
        for tweet in tweets:
            total_tweets += 1
            tweet_text_lower = tweet.full_text.lower()
            
            for keyword in domain_keywords:
                if keyword.lower() in tweet_text_lower:
                    keyword_matches[keyword] = keyword_matches.get(keyword, 0) + 1
        
        # 计算匹配分数（匹配的关键词数量 / 总推文数）
        match_score = len(keyword_matches) / max(total_tweets, 1)
        
        return {
            'is_domain_user': match_score > 0.3,  # 30%以上推文包含关键词
            'match_score': match_score,
            'matched_keywords': keyword_matches,
            'total_tweets_analyzed': total_tweets
        }
    except Exception as e:
        print(f"分析用户推文失败: {e}")
        return {'is_domain_user': False, 'error': str(e)}


async def check_user_domain_by_following(
    client: Client,
    user: User, 
    known_domain_users: List[str], 
    threshold: float = 0.1
) -> bool:
    """
    通过用户关注的人判断领域
    
    Args:
        client: Client对象
        user: User对象
        known_domain_users: 已知的该领域用户screen_name列表
        threshold: 关注列表中领域用户占比阈值（10%）
    
    Returns:
        bool: 是否属于该领域
    """
    try:
        following = await client.get_user_following(user.id, count=100)
        
        domain_following_count = 0
        total_following = 0
        
        known_users_lower = [u.lower() for u in known_domain_users]
        
        for followed_user in following:
            total_following += 1
            if followed_user.screen_name.lower() in known_users_lower:
                domain_following_count += 1
        
        if total_following == 0:
            return False
        
        ratio = domain_following_count / total_following
        return ratio >= threshold
        
    except Exception as e:
        print(f"分析关注列表失败: {e}")
        return False


async def identify_user_domain(
    client: Client,
    user: User, 
    domain_keywords: List[str], 
    known_domain_users: Optional[List[str]] = None,
    min_followers: int = 10000, 
    analyze_tweets: bool = True
) -> Dict:
    """
    综合多种方法判断用户领域
    
    Args:
        client: Client对象
        user: User对象
        domain_keywords: 领域关键词列表
        known_domain_users: 已知的该领域用户列表
        min_followers: 最小粉丝数要求
        analyze_tweets: 是否分析推文内容
    
    Returns:
        dict: 判断结果和详细信息
    """
    result = {
        'user_id': user.id,
        'screen_name': user.screen_name,
        'name': user.name,
        'followers_count': user.followers_count,
        'is_domain_user': False,
        'confidence': 0,
        'methods': {}
    }
    
    # 检查粉丝数
    if user.followers_count < min_followers:
        result['methods']['followers_check'] = False
        result['reason'] = f'粉丝数不足 {min_followers}'
        return result
    
    result['methods']['followers_check'] = True
    confidence = 0
    
    # 方法1: 描述匹配
    desc_match = check_user_domain_by_description(user, domain_keywords, min_match=1)
    result['methods']['description_match'] = desc_match
    if desc_match:
        confidence += 0.3
    
    # 方法2: 用户名匹配
    name_match = check_user_domain_by_screen_name(user, domain_keywords)
    result['methods']['screen_name_match'] = name_match
    if name_match:
        confidence += 0.2
    
    # 方法3: 推文分析
    if analyze_tweets:
        tweet_analysis = await analyze_user_tweets_for_domain(client, user, domain_keywords, tweet_count=10)
        result['methods']['tweet_analysis'] = tweet_analysis
        if tweet_analysis.get('is_domain_user'):
            confidence += 0.4
        result['tweet_match_score'] = tweet_analysis.get('match_score', 0)
    
    # 方法4: 关注列表分析
    if known_domain_users:
        following_match = await check_user_domain_by_following(client, user, known_domain_users)
        result['methods']['following_analysis'] = following_match
        if following_match:
            confidence += 0.1
    
    result['confidence'] = min(confidence, 1.0)
    result['is_domain_user'] = confidence >= 0.5  # 50%以上置信度
    
    return result


async def filter_users_by_domain(
    client: Client,
    users: List[User], 
    domain_keywords: List[str], 
    min_followers: int = 10000
) -> List[Dict]:
    """
    批量筛选属于特定领域的用户
    
    Args:
        client: Client对象
        users: User对象列表
        domain_keywords: 领域关键词列表
        min_followers: 最小粉丝数
    
    Returns:
        list: 符合条件的用户列表
    """
    domain_users = []
    
    for user in users:
        # 快速筛选：粉丝数和描述
        if user.followers_count < min_followers:
            continue
        
        if check_user_domain_by_description(user, domain_keywords, min_match=1):
            domain_users.append({
                'id': user.id,
                'screen_name': user.screen_name,
                'name': user.name,
                'followers_count': user.followers_count,
                'description': user.description
            })
    
    return domain_users


async def filter_following_by_domain(
    client: Client,
    user: User, 
    domain_keywords: List[str], 
    min_followers: int = 10000
) -> List[Dict]:
    """
    从用户的关注列表中筛选特定领域的用户
    
    Args:
        client: Client对象
        user: User对象
        domain_keywords: 领域关键词列表
        min_followers: 最小粉丝数
    
    Returns:
        list: 符合条件的用户列表
    """
    following = await client.get_user_following(user.id, count=200)
    
    domain_users = []
    for followed_user in following:
        if followed_user.followers_count < min_followers:
            continue
        
        if check_user_domain_by_description(followed_user, domain_keywords, min_match=1):
            domain_users.append({
                'id': followed_user.id,
                'screen_name': followed_user.screen_name,
                'name': followed_user.name,
                'followers_count': followed_user.followers_count,
                'description': followed_user.description
            })
    
    return domain_users


# 使用示例
async def example():
    from twikit import Client
    
    client = Client('en-US')
    client.set_cookies({
        'auth_token': 'your_token',
        'ct0': 'your_ct0'
    })
    
    # 示例1: 判断单个用户
    user = await client.get_user_by_screen_name('openai')
    result = await identify_user_domain(
        client,
        user,
        AI_KEYWORDS['en'],
        known_domain_users=['anthropicai', 'googleai'],
        min_followers=10000
    )
    print(f"是否AI用户: {result['is_domain_user']}")
    print(f"置信度: {result['confidence']:.2%}")
    
    # 示例2: 从搜索结果中筛选
    tweets = await client.search_tweet('AI', 'Latest', count=20)
    unique_users = {}
    for tweet in tweets:
        if tweet.user.screen_name not in unique_users:
            unique_users[tweet.user.screen_name] = tweet.user
    
    ai_users = await filter_users_by_domain(
        client,
        list(unique_users.values()),
        AI_KEYWORDS['en'],
        min_followers=10000
    )
    print(f"找到 {len(ai_users)} 个AI领域用户")


if __name__ == '__main__':
    asyncio.run(example())

