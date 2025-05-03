import os
import re
from datetime import datetime

# 配置参数
POSTS_DIR = "./"               # 要处理的目录
DEFAULT_CATEGORY = "计算机"     # 固定分类
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"  # 日期格式

def get_folder_name(file_path):
    """获取文件所在文件夹名称"""
    dir_path = os.path.dirname(file_path)
    folder_name = os.path.basename(dir_path)
    
    # 忽略根目录的特殊情况
    if dir_path == POSTS_DIR.rstrip('/'):
        return "未分类"
    return folder_name

def generate_front_matter(title, folder_name, file_path):
    """生成 front matter 模板"""
    # 获取文件创建时间
    ctime = os.path.getctime(file_path)
    date_str = datetime.fromtimestamp(ctime).strftime(DATE_FORMAT)
    
    return f"""---
title: {title}
date: {date_str}
categories:
  - {DEFAULT_CATEGORY}
tags:
  - {folder_name}
---

"""

def process_file(file_path):
    """处理单个文件"""
    with open(file_path, 'r+', encoding='utf-8') as f:
        content = f.read()
        
        # 跳过已有 front matter 的文件
        if content.startswith('---\n'):
            print(f"⚠️ 跳过已有 front matter 的文件: {file_path}")
            return

        # 获取元数据
        file_name = os.path.basename(file_path)
        title = os.path.splitext(file_name)[0]
        folder_name = get_folder_name(file_path)

        # 生成新内容
        front_matter = generate_front_matter(title, folder_name, file_path)
        new_content = front_matter + content

        # 写入文件
        f.seek(0)
        f.write(new_content)
        f.truncate()
        print(f"✅ 已处理: {file_path}")

def main():
    print("🚀 开始添加 Front Matter...")
    for root, dirs, files in os.walk(POSTS_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                process_file(file_path)
    print("🎉 全部处理完成！")

if __name__ == "__main__":
    main()