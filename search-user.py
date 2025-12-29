from ast import If
import os
from dotenv import load_dotenv
import asyncio
from twikit import Client

client = Client('en-US')

async def main():
    load_dotenv()
    # 使用字典设置 Cookies
    client.set_cookies({
        'auth_token': os.getenv('TWITTER_AUTH_TOKEN'),
        'ct0': os.getenv('TWITTER_CT0'),
        'twid': os.getenv('TWITTER_TWID'), # 如果有的话
        'kdt': os.getenv('TWITTER_KDT')
    })
    
    # 验证是否成功加载
    # 尝试获取自己的信息，如果没报错，说明 Cookie 有效
    me = await client.user()
    print(f"当前登录用户: {me.name}")

    # 执行你的搜索逻辑...
    screen_name = 'WesRothMoney'  # 用户名（不带@符号）
    user = await client.get_user_by_screen_name(screen_name)
    
    user_tweets = await user.get_tweets('Tweets', count=1)
    for tweet in user_tweets:
        if tweet.retweeted_tweet:
            print("-------转发推文-------")
            print(f"转发用户: {tweet.retweeted_tweet.user.screen_name}")
            print(f"转发内容: {tweet.retweeted_tweet.full_text}")
            print(f"转发时间: {tweet.retweeted_tweet.created_at_datetime}")
            print(f"转发点赞: {tweet.retweeted_tweet.favorite_count}")
            print(f"转发链接: https://x.com/{tweet.retweeted_tweet.user.screen_name}/status/{tweet.retweeted_tweet.id}")
            print("--------------------------------")
        else:
            print("-------普通推文-------")
            print(f"内容: {tweet.full_text}")
            print(f"时间: {tweet.created_at_datetime}")
            print(f"点赞: {tweet.favorite_count}")
            print(f"是否转发: {tweet.retweeted_tweet}")
            print(f"链接: https://x.com/{tweet.user.screen_name}/status/{tweet.id}")
asyncio.run(main())