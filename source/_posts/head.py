#!/usr/bin/env python3
# ensure_blank_before_headings.py

import sys
import os
import re

def process_file(path):
    """在文件中每个 '### ' 前确保有一个空行。"""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        if re.match(r'^(###\s)', line):
            # 如果不是文件第一行，且上一行不是空行，则先补一行空行
            if new_lines and new_lines[-1].strip() != '':
                new_lines.append('\n')
        new_lines.append(line)

    # 只在内容有变化时才写回
    if new_lines != lines:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f'  ✔ updated: {path}')
    else:
        print(f'  – no change: {path}')

def walk_and_process(root_dir):
    """遍历所有 .md 文件并处理。"""
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith('.md'):
                full_path = os.path.join(dirpath, fname)
                process_file(full_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'用法: {sys.argv[0]} /path/to/markdown/root')
        sys.exit(1)
    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f'错误：{root} 不是有效目录')
        sys.exit(1)
    print(f'Processing Markdown files under: {root}')
    walk_and_process(root)
    print('Done.')
