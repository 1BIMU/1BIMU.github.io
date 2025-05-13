#!/usr/bin/env python3
# process_markdown.py

import sys
import os
import re # Import the regular expression module

def process_content_section(content_lines):
    """
    对 Markdown 文件的内容部分执行处理：
    1. 确保 H3 标题 (### ) 前有空行。
    2. 为 '![](IMG/...' 格式的图片链接路径添加前导 '/' -> '![](/IMG/...'。
    3. 为需要硬换行的非空行添加两个尾随空格。

    Args:
        content_lines (list): Markdown 文件内容部分的行列表。

    Returns:
        list: 处理后的内容行列表。
    """
    if not content_lines:
        return []

    current_lines = list(content_lines) # Start with a copy

    # --- 步骤 1: 确保 H3 标题前有空行 ---
    lines_after_heading_fix = []
    for line in current_lines:
        is_h3 = re.match(r'^(###\s)', line)
        needs_blank_before_h3 = (
            is_h3 and
            lines_after_heading_fix and
            lines_after_heading_fix[-1].strip() != ''
        )
        if needs_blank_before_h3:
            lines_after_heading_fix.append('\n')
        lines_after_heading_fix.append(line)
    current_lines = lines_after_heading_fix

    # --- 步骤 2: 修正图片路径 (添加前导斜杠) ---
    lines_after_image_fix = []
    img_pattern = re.compile(r'(!\[[^\]]*\]\()(IMG/)')
    for line in current_lines:
        modified_line = img_pattern.sub(r'\1/\2', line)
        lines_after_image_fix.append(modified_line)
    current_lines = lines_after_image_fix

    # --- 步骤 3: 添加行尾双空格 ---
    final_content_lines = []
    for line in current_lines:
        original_newline = ''
        if line.endswith('\r\n'):
            original_newline = '\r\n'
        elif line.endswith('\n'):
            original_newline = '\n'

        stripped_line = line.rstrip('\r\n')

        if not stripped_line.strip():
            final_content_lines.append(line)
        else:
            if stripped_line.endswith('  '):
                final_content_lines.append(line)
            else:
                content_part = stripped_line.rstrip()
                final_content_lines.append(content_part + '  ' + original_newline)

    return final_content_lines


def process_markdown_file(filepath):
    """
    处理单个 Markdown 文件，跳过 front-matter 部分。
    对内容部分执行：H3 前空行、IMG 路径修正、行尾双空格。

    Args:
        filepath (str): 要处理的 Markdown 文件的路径。

    Returns:
        bool: 如果文件被修改则返回 True，否则返回 False。
    """
    try:
        # --- 读取原始文件内容 ---
        with open(filepath, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()

        if not original_lines:
            return False # 空文件，无需处理

        # --- 识别 front-matter ---
        front_matter_lines = []
        content_lines = []
        front_matter_end_index = -1

        # 检查第一行是否是 front-matter 开始分隔符
        if original_lines[0].strip() == '---':
            front_matter_lines.append(original_lines[0])
            # 从第二行开始查找结束分隔符
            for i, line in enumerate(original_lines[1:], start=1):
                front_matter_lines.append(line)
                if line.strip() == '---':
                    front_matter_end_index = i
                    break
            # 如果找到了结束分隔符，则其后的内容是 content
            if front_matter_end_index != -1:
                content_lines = original_lines[front_matter_end_index + 1:]
            else:
                # 如果只有开始没有结束，则认为整个文件都是 front-matter（异常情况）
                # 或者按原样处理整个文件？为安全起见，这里选择不处理内容
                 content_lines = [] 
                 # print(f"警告：文件 {filepath} 似乎有未闭合的 front-matter，跳过内容处理。", file=sys.stderr)
                 
        else:
            # 如果第一行不是 '---'，则认为没有 front-matter，所有行都是内容
            content_lines = original_lines

        # --- 处理内容部分 ---
        processed_content = process_content_section(content_lines)

        # --- 合并最终结果 ---
        final_lines = front_matter_lines + processed_content

        # --- 检查是否有变化并写回文件 ---
        if final_lines != original_lines:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(final_lines)
            print(f'  ✔ updated: {filepath}')
            return True
        else:
            # print(f'  – no change: {filepath}') # Optional
            return False

    except Exception as e:
        print(f"处理文件时出错 {filepath}: {e}", file=sys.stderr)
        return False

def walk_and_process(root_dir):
    """
    遍历指定目录及其子目录，处理所有 .md 文件。

    Args:
        root_dir (str): 要处理的根目录路径。 **应指向 _posts 目录**。
    """
    # 确保我们只在指定的 _posts 目录及其子目录下操作
    # (这个检查由调用者传入正确的 root_dir 参数来保证)
    print(f'Processing Markdown files under: {root_dir}')
    processed_count = 0
    modified_count = 0

    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            # 确保只处理 .md 文件
            if fname.lower().endswith('.md'):
                # 确保我们不会意外处理 _posts 之外的文件（虽然 os.walk 已经限制了）
                # 但为了更明确，可以检查 full_path 是否真的在 root_dir 下
                full_path = os.path.join(dirpath, fname)
                # 简单的检查： realpath确保路径规范化，防止 '..' 等问题
                if os.path.realpath(full_path).startswith(os.path.realpath(root_dir)):
                    processed_count += 1
                    if process_markdown_file(full_path):
                        modified_count += 1
                else:
                     print(f"警告: 跳过不在指定根目录下的文件: {full_path}", file=sys.stderr)


    print(f'\nFinished processing.')
    print(f"Total files checked in '{root_dir}': {processed_count}")
    print(f"Files modified:                     {modified_count}")

# --- 主程序入口 ---
if __name__ == '__main__':
    if len(sys.argv) != 2:
        script_name = os.path.basename(sys.argv[0])
        print(f'用法: python {script_name} /path/to/markdown/_posts') # 明确提示需要 _posts 目录
        print(f'例如: python {script_name} source/_posts')
        sys.exit(1)

    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f'错误：\'{root}\' 不是一个有效的目录', file=sys.stderr)
        sys.exit(1)

    # 添加一个额外的检查，看传入的目录名是否符合预期（可选，但更健壮）
    # if not os.path.basename(os.path.normpath(root)).endswith('_posts'):
    #    print(f"警告: 指定的目录 '{root}' 似乎不是一个 '_posts' 目录。", file=sys.stderr)
    #    # 可以选择在这里退出，或者继续执行 sys.exit(1)

    walk_and_process(root)