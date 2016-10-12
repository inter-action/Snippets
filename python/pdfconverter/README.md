# About this Repo
用来将目标网页转换成pdf的小工具, 你可以限制输出的文件页码大小。这是比pdfcrowd网页上操作好的地方，
而且还没有水印。

python3 的项目, 注意下

# start it up

activate virtualenv (optional, but is recommended)

    source .env/bin/activate    #activate virtual env
    deactivate                  #deactivate virtual

install dependencies:

     pip install pdfcrowd3



注册 http://pdfcrowd.com/ 用户:

添加配置文件`touch config.ini`, 将你注册的用户名和apikey(可以在你的账户信息中找到)添加到下面

    # Application config file
    [main]
    username          = <username>
    apikey = <apikey, something like 0ece3b457cce484ef3d726ba5c48fc9s>
    output_path = target
    

运行, 根据提示添加对应的信息, 目标路径的url是必填的:

    python main.py


## todo:

    add packaging
        http://www.pyinstaller.org/