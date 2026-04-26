---
categories:
  - 生活分享
tags:
  - 个人复盘
mathjax: "true"
title: 关于在linux上面使用clash这档事...
date: 2025-11-23 12:59:30
---
测试了好几个库，捣鼓了好几个小时，总算是成功在类AutoDL平台上成功了...  
使用的是下面这个库  
```bash  
git clone --branch feat-init --depth 1 https://gh-proxy.com/https://github.com/nelvko/clash-for-linux-install.git \  
  && cd clash-for-linux-install \  
  && bash install.sh  
```  
不得不说，这个库确实比较简单易上手，可以无脑用，强推。特别是它这个版本可以兼容普通用户，感觉很棒！  

记得提前安装好网络相关的库就可以：  
```bash  
apt-get update && apt-get install -y net-tools  
```  
