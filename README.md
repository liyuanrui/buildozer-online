
#### 0. 介绍

应用截图: [screenshot](https://github.com/liyuanrui/buildozer-online/blob/master/screenshot.jpg)

应用下载: [Buildozer-OL.apk](https://github.com/liyuanrui/buildozer-online/releases)

buildozer-online是一个可以在线打包kivy apk的项目, 依赖于buildozer打包环境, 

初衷为了便利喜欢在手机上折腾的萌新, 一键打包, 随心分享. 

打包服务器部署在我的虚拟机里面, 打完即删, 保证安全. 

当然你也可以参照下面的部署教程自己部署.

欢迎加入 [kivy中国开发群](https://shang.qq.com/wpa/qunwpa?idkey=20b15394264f960bf5373e5afa76ac72a37fdc7b41010acc548ffc3113986e04)

#### 1. 部署

首先需要搭建buildozer打包环境, 参照 [KivyMD推荐安装教程](https://github.com/HeaTTheatR/KivyMD#building-with-vm), 或者直接使用 [nkiiiiid](https://github.com/nkiiiiid) 搭建的 [kivydev打包环境](https://github.com/nkiiiiid/kivy-apk)

然后安装服务依赖
``` bash
sudo pip3 install rpyc==4.1.4
```

然后运行服务
``` bash
python3 server.py
```

然后替换main.py中服务器的地址和端口
```
c = rpyc.connect('111.230.24.37',30033)
```

最后重新打包此项目就可以拥有一个属于你的buildozer_online了
