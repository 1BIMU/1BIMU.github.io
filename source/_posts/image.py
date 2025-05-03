import os
import re
import shutil
from urllib.parse import quote  # 新增 URL 编码模块

# 配置参数
POSTS_DIR = "./"
IMAGE_PREFIX = "/IMG/"  # 保持与你实际存放图片的目录一致
BACKUP_SUFFIX = ".bak"

OBSIDIAN_IMAGE_PATTERN = re.compile(r'!\[\[(.*?)\]\]')

def fix_image_references_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    backup_path = file_path + BACKUP_SUFFIX
    shutil.copy(file_path, backup_path)

    def replace_match(match):
        original_filename = match.group(1)
        
        # 改进点1：对文件名进行URL编码（处理空格等特殊字符）
        encoded_filename = quote(original_filename)
        
        # 改进点2：添加显式的文件协议标识（可选）
        return f"![图片描述]({IMAGE_PREFIX}{encoded_filename})"

    new_content = OBSIDIAN_IMAGE_PATTERN.sub(replace_match, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated: {file_path}")

def process_all_md_files(directory):
    """递归处理所有 .md 文件"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                fix_image_references_in_file(file_path)

if __name__ == "__main__":
    print("🚀 开始修复 Markdown 图片引用...")
    process_all_md_files(POSTS_DIR)
    print("🎉 所有图片引用已修复！")