#!/bin/bash

# 复制文件夹 IMG 到目标路径
cp -r /e/1BIMU.github.io/source/_posts/IMG /e/1BIMU.github.io/source

# 添加所有更改
git add .

# 提交更改
git commit -am "new Posts"

# 推送到远程仓库
git push
