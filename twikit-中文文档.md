# Twikit 中文文档

Twikit 是一个 Python 异步 Twitter/X API 客户端库。

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [客户端初始化](#客户端初始化)
- [认证方式](#认证方式)
- [用户相关](#用户相关)
- [推文相关](#推文相关)
- [搜索功能](#搜索功能)
- [数据对象属性](#数据对象属性)
- [错误处理](#错误处理)

---

## 安装

```bash
pip install twikit
```

---

## 快速开始

```python
import asyncio
from twikit import Client

async def main():
    # 创建客户端
    client = Client('en-US')
    
    # 设置 Cookies 认证
    client.set_cookies({
        'auth_token': 'your_auth_token',
        'ct0': 'your_ct0',
        'twid': 'your_twid',
        'kdt': 'your_kdt'
    })
    
    # 获取当前用户信息
    me = await client.user()
    print(f"当前用户: {me.name} (@{me.screen_name})")
    
    # 搜索推文
    tweets = await client.search_tweet('Python', 'Latest')
    for tweet in tweets:
        print(f"{tweet.user.name}: {tweet.text}")

asyncio.run(main())
```

---

## 客户端初始化

### 基本初始化

```python
from twikit import Client

# 指定语言代码
client = Client('en-US')  # 英语
client = Client('zh-CN')  # 简体中文
client = Client('ja-JP')  # 日语
```

### 带代理初始化

```python
# HTTP 代理
client = Client('en-US', proxy='http://proxy.example.com:8080')

# SOCKS5 代理
client = Client('en-US', proxy='socks5://proxy.example.com:1080')
```

### 带验证码求解器初始化

```python
from twikit import Capsolver, Client

# 使用 Capsolver 自动解决验证码
solver = Capsolver(
    api_key='your_capsolver_api_key',
    max_attempts=10
)
client = Client('en-US', captcha_solver=solver)
```

---

## 认证方式

### 方式 1: 使用 Cookies（推荐）

```python
# 使用字典设置 Cookies
client.set_cookies({
    'auth_token': 'your_auth_token',  # 必需
    'ct0': 'your_ct0',                # 必需（CSRF token）
    'twid': 'u%3D1234567890',         # 可选
    'kdt': 'your_kdt'                 # 可选
})

# 验证 Cookies 是否有效
me = await client.user()
print(f"认证成功: {me.name}")
```

**如何获取 Cookies：**
1. 在浏览器中登录 https://x.com
2. 按 F12 打开开发者工具
3. 切换到 Console（控制台）
4. 运行 `document.cookie` 获取 cookie 字符串
5. 或查看 Application → Cookies → https://x.com

### 方式 2: 使用用户名密码登录

```python
# 登录
await client.login('username', 'password')

# 登录后可以保存 Cookies
await client.save_cookies('cookies.json')

# 下次使用时加载 Cookies
await client.load_cookies('cookies.json')
```

### 方式 3: 使用已保存的 Cookies

```python
# 从文件加载
await client.load_cookies('cookies.json')

# 获取当前 Cookies
cookies = await client.get_cookies()
print(cookies)
```

---

## 用户相关

### 获取当前登录用户

```python
# 获取当前用户信息
me = await client.user()
print(f"用户名: @{me.screen_name}")
print(f"显示名: {me.name}")
print(f"用户ID: {me.id}")
print(f"简介: {me.description}")
print(f"粉丝数: {me.followers_count}")
print(f"关注数: {me.following_count}")
print(f"推文数: {me.tweet_count}")
```

### 通过用户名获取用户

```python
# 通过 screen_name（用户名，不带@符号）
user = await client.get_user_by_screen_name('elonmusk')
print(f"{user.name} (@{user.screen_name})")
print(f"粉丝数: {user.followers_count}")
```

### 通过用户ID获取用户

```python
# 通过用户ID
user = await client.get_user_by_id('44196397')
print(f"{user.name}")
```

### 搜索用户

```python
# 搜索用户
users = await client.search_user('Python', count=20)

for user in users:
    print(f"{user.name} (@{user.screen_name})")
    print(f"简介: {user.description}")
    print("-" * 50)

# 获取更多结果
more_users = await users.next()
```

### 获取用户的推文

```python
# 获取指定用户的推文
user = await client.get_user_by_screen_name('elonmusk')

# 获取推文（类型：'Tweets', 'Replies', 'Media', 'Likes'）
tweets = await user.get_tweets('Tweets', count=20)

for tweet in tweets:
    print(f"{tweet.text}")
    print(f"时间: {tweet.created_at}")
    print("-" * 50)

# 获取更多推文
more_tweets = await tweets.next()
```

### 获取用户时间线

```python
# 获取用户主页时间线
timeline = await client.get_timeline('elonmusk', count=20)

# 获取最新时间线
latest_timeline = await client.get_latest_timeline('elonmusk', count=20)
```

### 关注/取消关注用户

```python
user = await client.get_user_by_screen_name('elonmusk')

# 关注用户
await client.follow_user(user.id)

# 取消关注
await client.unfollow_user(user.id)
```

### 获取关注者和关注列表

```python
user = await client.get_user_by_screen_name('elonmusk')

# 获取粉丝列表
followers = await client.get_user_followers(user.id, count=20)

# 获取关注列表
following = await client.get_user_following(user.id, count=20)

# 获取最新粉丝
latest_followers = await client.get_latest_followers(user.id, count=20)
```

---

## 推文相关

### 搜索推文

```python
# 搜索推文
# 类型：'Top'（热门）, 'Latest'（最新）, 'Media'（媒体）
tweets = await client.search_tweet('Python programming', 'Latest', count=20)

for tweet in tweets:
    print(f"用户: @{tweet.user.screen_name}")
    print(f"内容: {tweet.text}")
    print(f"时间: {tweet.created_at}")
    print(f"点赞: {tweet.favorite_count}")
    print(f"转发: {tweet.retweet_count}")
    print("-" * 50)

# 获取更多结果
more_tweets = await tweets.next()
```

### 通过ID获取推文

```python
# 获取单条推文
tweet = await client.get_tweet_by_id('1234567890123456789')
print(tweet.text)

# 批量获取推文
tweet_ids = ['1234567890123456789', '9876543210987654321']
tweets = await client.get_tweets_by_ids(tweet_ids)
```

### 发送推文

```python
# 发送纯文本推文
tweet = await client.create_tweet('Hello, Twitter!')
print(f"推文已发送: {tweet.id}")

# 回复推文
reply = await tweet.reply('这是回复内容')

# 引用推文
quote = await client.create_tweet('这是引用推文', quote_id=tweet.id)
```

### 发送带媒体的推文

```python
# 1. 上传媒体
media = await client.upload_media('image.jpg')

# 2. 检查上传状态
status = await client.check_media_status(media.media_id)

# 3. 创建媒体元数据（可选）
await client.create_media_metadata(media.media_id, alt_text='图片描述')

# 4. 发送带图片的推文
tweet = await client.create_tweet('带图片的推文', media_ids=[media.media_id])
```

### 点赞和取消点赞

```python
tweet = await client.get_tweet_by_id('1234567890123456789')

# 点赞
await tweet.favorite()
# 或
await client.favorite_tweet(tweet.id)

# 取消点赞
await tweet.unfavorite()
# 或
await client.unfavorite_tweet(tweet.id)
```

### 转发和取消转发

```python
tweet = await client.get_tweet_by_id('1234567890123456789')

# 转发
await tweet.retweet()
# 或
await client.retweet(tweet.id)

# 取消转发
await tweet.delete_retweet()
# 或
await client.delete_retweet(tweet.id)
```

### 删除推文

```python
tweet = await client.get_tweet_by_id('1234567890123456789')
await tweet.delete()
```

### 书签功能

```python
tweet = await client.get_tweet_by_id('1234567890123456789')

# 添加书签
await tweet.bookmark()
# 或
await client.bookmark_tweet(tweet.id)

# 删除书签
await tweet.delete_bookmark()
# 或
await client.delete_bookmark(tweet.id)

# 获取所有书签
bookmarks = await client.get_bookmarks(count=20)
```

---

## 搜索功能

### 搜索推文

```python
# 基本搜索
tweets = await client.search_tweet('Python', 'Latest')

# 高级搜索（使用 Twitter 搜索语法）
tweets = await client.search_tweet('Python lang:en -RT', 'Top')
```

### 搜索用户

```python
users = await client.search_user('developer', count=20)
```

### 搜索相似推文

```python
tweet = await client.get_tweet_by_id('1234567890123456789')
similar = await tweet.get_similar_tweets(count=10)
```

---

## 数据对象属性

### User（用户）对象

```python
user = await client.get_user_by_screen_name('elonmusk')

# 基本信息
user.id                    # 用户ID
user.name                  # 显示名称
user.screen_name           # 用户名（不带@）
user.description           # 个人简介
user.location              # 位置
user.url                   # 个人网站URL

# 统计信息
user.followers_count       # 粉丝数
user.following_count       # 关注数
user.tweet_count           # 推文数
user.listed_count          # 列表数

# 媒体
user.profile_image_url     # 头像URL
user.profile_banner_url    # 横幅URL

# 状态
user.verified              # 是否认证
user.protected             # 是否私密账号
user.following             # 是否已关注
user.follow_request_sent   # 是否已发送关注请求

# 时间
user.created_at            # 账号创建时间（时间戳）
user.created_at_datetime   # 账号创建时间（datetime对象）
```

### Tweet（推文）对象

```python
tweet = await client.get_tweet_by_id('1234567890123456789')

# 基本信息
tweet.id                   # 推文ID
tweet.text                 # 推文文本（可能被截断）
tweet.full_text            # 完整推文文本
tweet.lang                 # 语言代码
tweet.created_at           # 创建时间（时间戳）
tweet.created_at_datetime  # 创建时间（datetime对象）

# 用户信息
tweet.user                 # User对象
tweet.user.name            # 用户名
tweet.user.screen_name     # 用户handle

# 互动统计
tweet.favorite_count       # 点赞数
tweet.retweet_count        # 转发数
tweet.reply_count          # 回复数
tweet.quote_count          # 引用数
tweet.bookmark_count       # 书签数
tweet.view_count           # 浏览数

# 状态
tweet.favorited            # 是否已点赞
tweet.retweeted            # 是否已转发
tweet.bookmarked           # 是否已收藏

# 媒体
tweet.media                # 媒体列表（图片、视频等）

# 回复相关
tweet.in_reply_to          # 回复的推文ID
tweet.reply_to             # 回复的推文对象

# 引用相关
tweet.is_quote_status      # 是否为引用推文
tweet.quote                # 被引用的推文对象

# 转发相关
tweet.retweeted_tweet      # 被转发的原始推文

# 其他
tweet.place                # 位置信息
tweet.hashtags             # 话题标签列表
tweet.urls                 # URL列表
tweet.possibly_sensitive   # 是否可能包含敏感内容
```

### Result（结果集）对象

```python
# 搜索结果返回 Result 对象
tweets = await client.search_tweet('Python', 'Latest')

# 基本属性
tweets.next_cursor         # 下一页游标
tweets.previous_cursor     # 上一页游标
tweets.token              # 别名，等同于 next_cursor
tweets.cursor             # 别名，等同于 next_cursor

# 获取更多结果
more_tweets = await tweets.next()      # 获取下一页
prev_tweets = await tweets.previous()  # 获取上一页

# 像列表一样使用
print(tweets[0])          # 访问第一条
for tweet in tweets:      # 遍历
    print(tweet)
```

---

## 错误处理

### 常见错误类型

```python
from twikit.errors import (
    BadRequest,           # 400 - 请求错误
    Unauthorized,         # 401 - 未授权（Cookies无效）
    Forbidden,           # 403 - 禁止访问
    NotFound,             # 404 - 未找到（Code 34）
    RequestTimeout,       # 408 - 请求超时
    TooManyRequests,      # 429 - 请求过多（限流）
    ServerError,          # 5xx - 服务器错误
    AccountLocked,        # 账号被锁定
    AccountSuspended,     # 账号被暂停
    UserNotFound,         # 用户不存在
    TweetNotAvailable     # 推文不可用
)
```

### 错误处理示例

```python
import asyncio
from twikit import Client
from twikit.errors import Unauthorized, NotFound, TooManyRequests

async def main():
    client = Client('en-US')
    client.set_cookies({
        'auth_token': 'your_token',
        'ct0': 'your_ct0'
    })
    
    try:
        me = await client.user()
        print(f"成功: {me.name}")
        
    except Unauthorized:
        print("❌ 认证失败：Cookies 无效或已过期，请重新获取")
        
    except NotFound as e:
        print(f"❌ 未找到：{e}")
        # Code 34 通常表示 Cookies 无效
        
    except TooManyRequests:
        print("❌ 请求过多：请稍后再试")
        
    except Exception as e:
        print(f"❌ 其他错误：{e}")

asyncio.run(main())
```

---

## 实用示例

### 示例 1: 监控特定关键词的推文

```python
import asyncio
from twikit import Client

async def monitor_keyword(keyword):
    client = Client('en-US')
    client.set_cookies({
        'auth_token': 'your_token',
        'ct0': 'your_ct0'
    })
    
    tweets = await client.search_tweet(keyword, 'Latest', count=10)
    
    for tweet in tweets:
        print(f"[{tweet.created_at_datetime}] @{tweet.user.screen_name}")
        print(f"{tweet.full_text}")
        print(f"链接: https://x.com/{tweet.user.screen_name}/status/{tweet.id}")
        print("-" * 50)

asyncio.run(monitor_keyword('Python'))
```

### 示例 2: 获取用户主页链接

```python
tweet = tweets[0]
user = tweet.user

# 构建用户主页URL
profile_url = f"https://x.com/{user.screen_name}"
print(f"用户主页: {profile_url}")

# 构建推文URL
tweet_url = f"https://x.com/{user.screen_name}/status/{tweet.id}"
print(f"推文链接: {tweet_url}")
```

### 示例 3: 批量获取用户信息

```python
async def get_users_info(screen_names):
    client = Client('en-US')
    client.set_cookies({
        'auth_token': 'your_token',
        'ct0': 'your_ct0'
    })
    
    users_info = []
    for screen_name in screen_names:
        try:
            user = await client.get_user_by_screen_name(screen_name)
            users_info.append({
                'name': user.name,
                'screen_name': user.screen_name,
                'followers': user.followers_count,
                'following': user.following_count,
                'tweets': user.tweet_count
            })
        except Exception as e:
            print(f"获取 {screen_name} 失败: {e}")
    
    return users_info

# 使用
users = await get_users_info(['elonmusk', 'openai', 'anthropicai'])
for user in users:
    print(user)
```

---

## 注意事项

1. **Cookies 有效期**：Twitter Cookies 有时效性，通常几小时到几天，过期后需要重新获取
2. **请求频率限制**：注意不要过于频繁地请求，避免触发限流（429错误）
3. **账号安全**：不要分享你的 `auth_token`，它等同于你的登录密码
4. **异步编程**：所有 API 调用都是异步的，需要使用 `await` 关键字
5. **错误处理**：建议始终使用 try-except 处理可能的错误

---

## 参考资源

- [Twikit 官方文档](https://twikit.readthedocs.io/)
- [Twikit GitHub](https://github.com/twikit/twikit)

---

**最后更新：** 2024年

