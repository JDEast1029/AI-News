import asyncio
from twikit import Client

client = Client('en-US')

async def main():
    # 使用字典设置 Cookies
    client.set_cookies({
        
    })
    
    # 验证是否成功加载
    # 尝试获取自己的信息，如果没报错，说明 Cookie 有效
    me = await client.user()
    print(f"当前登录用户: {me.name}")

    # 执行你的搜索逻辑...
    tweets = await client.search_tweet('Claude Code', 'Latest')
    tweet = tweets[0]
    
    # ========== 获取推文链接 ==========
    # 1. 推文本身的链接（最重要）
    tweet_url = f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}"
    print(f"推文链接: {tweet_url}")
    
    # ========== 获取用户链接 ==========
    # 2. 用户主页链接
    user_profile_url = f"https://x.com/{tweet.user.screen_name}"
    print(f"用户主页: {user_profile_url}")
    
    # ========== 推文内容中的链接 ==========
    # 3. 推文内容中包含的URL（如果有的话）
    if tweet.urls:
        print(f"推文中的链接: {tweet.urls}")
    else:
        print("推文中没有包含链接")
    
    # ========== 其他信息 ==========
    print(f"\n推文内容: {tweet.full_text}")
    print(f"发布时间: {tweet.created_at}")
    print(f"作者: {tweet.user.name} (@{tweet.user.screen_name})")
    
    # 4. 缩略图链接（如果有媒体）
    if tweet.thumbnail_url:
        print(f"缩略图: {tweet.thumbnail_url}")
asyncio.run(main())