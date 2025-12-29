# python环境搭配
1. 安装 pyenv：brew install pyenv
2. 下载与安装 Python 版本
    - 查看可安装版本：pyenv install --list
    - 安装指定版本：pyenv install 3.14.0
3. 切换 Python 版本
    - 当前终端会话：pyenv shell <version> , 也可以在项目内设置 .python-version文件，内容为：3.14
    - 当前目录：pyenv local <version>
    - 全局系统：pyenv global <version>
4. 其他
    - 查看当前 Python 可执行文件的路径：pyenv which python


# 虚拟环境
1. 创建虚拟环境：在项目根目录下运行：python -m venv .venv
2. 激活环境：source .venv/bin/activate
3. 安装包：pip install langchain_community
4. 退出虚拟环境：deactivate
5. 设置“安全开关”：禁止全局安装：~/.zshrc  export PIP_REQUIRE_VIRTUALENV=true

# 安装依赖
`pip install -r requirements.txt`