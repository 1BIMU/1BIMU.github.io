import os

def add_mathjax_to_front_matter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 检查是否存在Front Matter
    if len(lines) < 2 or lines[0].strip() != '---':
        return False

    # 查找Front Matter结束位置
    end_line = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_line = i
            break
    
    if not end_line:
        return False  # 没有闭合的Front Matter

    # 检查是否已包含mathjax
    has_mathjax = any(
        line.strip().startswith('mathjax:') 
        for line in lines[1:end_line]
    )

    if not has_mathjax:
        # 在闭合符前插入mathjax
        lines.insert(end_line, 'mathjax: true\n')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.md'):
            path = os.path.join(root, file)
            try:
                if add_mathjax_to_front_matter(path):
                    print(f'Updated: {path}')
                else:
                    print(f'No change needed: {path}')
            except Exception as e:
                print(f'Error processing {path}: {str(e)}')