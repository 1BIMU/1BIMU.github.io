#!/usr/bin/env python3
# process_markdown.py

import sys
import os
import re # Import the regular expression module

def process_markdown_file(filepath):
    """
    处理单个 Markdown 文件：
    1. 确保 H3 标题 (### ) 前有空行。
    2. 为 '![](IMG/...' 格式的图片链接路径添加前导 '/' -> '![](/IMG/...'。
    3. 为需要硬换行的非空行添加两个尾随空格。

    Args:
        filepath (str): 要处理的 Markdown 文件的路径。

    Returns:
        bool: 如果文件被修改则返回 True，否则返回 False。
    """
    try:
        # --- 读取原始文件内容 ---
        with open(filepath, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()

        current_lines = list(original_lines) # Start with a copy

        # --- 步骤 1: 确保 H3 标题前有空行 ---
        lines_after_heading_fix = []
        for i, line in enumerate(current_lines):
            is_h3 = re.match(r'^(###\s)', line)
            needs_blank_before_h3 = (
                is_h3 and
                lines_after_heading_fix and
                lines_after_heading_fix[-1].strip() != ''
            )
            if needs_blank_before_h3:
                lines_after_heading_fix.append('\n')
            lines_after_heading_fix.append(line)
        current_lines = lines_after_heading_fix # Update current lines

        # --- 步骤 2: 修正图片路径 (添加前导斜杠) ---
        lines_after_image_fix = []
        # Regex explanation:
        # (!\[      # Capture group 1: Start with '!['
        # [^\]]* # Match any character except ']' (alt text) zero or more times
        # \]       # Match the closing ']'
        # \()      # Match and capture the opening parenthesis '('
        # (IMG/)   # Capture group 2: Match the literal string 'IMG/'
        img_pattern = re.compile(r'(!\[[^\]]*\]\()(IMG/)')
        for line in current_lines:
            # Replace occurrences of '![](IMG/' with '![](/IMG/'
            modified_line = img_pattern.sub(r'\1/\2', line) 
            lines_after_image_fix.append(modified_line)
        current_lines = lines_after_image_fix # Update current lines

        # --- 步骤 3: 添加行尾双空格 ---
        final_lines = []
        for line in current_lines: # Process lines after heading and image fixes
            original_newline = ''
            if line.endswith('\r\n'):
                original_newline = '\r\n'
            elif line.endswith('\n'):
                original_newline = '\n'
            
            stripped_line = line.rstrip('\r\n')

            if not stripped_line.strip():
                final_lines.append(line) # Keep blank/whitespace lines as is
            else:
                if stripped_line.endswith('  '):
                    final_lines.append(line) # Keep lines already ending with '  '
                else:
                    content_part = stripped_line.rstrip() # Remove any existing trailing whitespace
                    final_lines.append(content_part + '  ' + original_newline) # Add '  ' and newline

        # --- 步骤 4: 检查是否有变化并写回文件 ---
        if final_lines != original_lines:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(final_lines)
            print(f'  ✔ updated: {filepath}')
            return True
        else:
            # print(f'  – no change: {filepath}') # Optional: uncomment to see unchanged files
            return False

    except Exception as e:
        print(f"处理文件时出错 {filepath}: {e}", file=sys.stderr)
        return False

def walk_and_process(root_dir):
    """
    遍历指定目录及其子目录，处理所有 .md 文件。

    Args:
        root_dir (str): 要处理的根目录路径。
    """
    print(f'Processing Markdown files under: {root_dir}')
    processed_count = 0
    modified_count = 0

    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith('.md'):
                full_path = os.path.join(dirpath, fname)
                processed_count += 1
                if process_markdown_file(full_path):
                    modified_count += 1
    
    print(f'\nFinished processing.')
    print(f"Total files checked: {processed_count}")
    print(f"Files modified:      {modified_count}")

# --- 主程序入口 ---
if __name__ == '__main__':
    if len(sys.argv) != 2:
        script_name = os.path.basename(sys.argv[0]) 
        print(f'用法: python {script_name} /path/to/markdown/root')
        print(f'例如: python {script_name} _posts')
        sys.exit(1)
    
    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f'错误：\'{root}\' 不是一个有效的目录', file=sys.stderr)
        sys.exit(1)
        
    walk_and_process(root)