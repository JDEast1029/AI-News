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
    print(tweets[0].full_text)
    print(tweets[0].created_at)
    print(tweets[0].user.name)
    print(tweets[0].user)
    print("https://x.com/" + tweets[0].user.screen_name) # 用户主页
asyncio.run(main())