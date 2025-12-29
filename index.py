import asyncio
from twikit import Client

client = Client('en-US')

async def main():
    # 使用字典设置 Cookies
    client.set_cookies({
        'auth_token': 'a415a5e51805c69cc4b05507e4110b8a4f7853bf',
        'ct0': '57385f6fcb89235e9d8923c9ce6c4d53c6dcd59833bc9978d57552b6331544a86f56b10ead36eb65d672d0966405b8a2ff9341deb90e56a2e118b48f81515722b311ae9e6fadb782244f090c813d3cba',
        'twid': 'u%3D1991373083178070019', # 如果有的话
        'kdt': 'E4k5bpe2qoqHPbKoN09q5LB8jSeLQCEtyCXhBbVZ'
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