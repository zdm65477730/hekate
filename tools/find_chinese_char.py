#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
from typing import Set, List
import argparse

# 编译正则表达式，使其只匹配中文字符和中文标点
# 这是最关键的一步，确保了提取的纯净性
CHINESE_CHAR_PATTERN = re.compile(
    r'[\u4e00-\u9fff]|'          # CJK统一汉字 (常用汉字)
    r'[\u3400-\u4dbf]|'          # CJK扩展A (生僻字)
    r'[\u20000-\u2a6df]|'        # CJK扩展B
    r'[\u2a700-\u2b73f]|'        # CJK扩展C
    r'[\u2b740-\u2b81f]|'        # CJK扩展D
    r'[\u2b820-\u2ceaf]|'        # CJK扩展E
    r'[\u2ceb0-\u2ebef]|'        # CJK扩展F
    r'[\u3000-\u303f]|'          # CJK标点符号 (全角)
    r'[\uff00-\uffef]'           # 半角及全角形式的标点符号和字母
)

# 常用中文标点符号集合，可根据需要扩展
COMMON_CHINESE_PUNCTUATION: Set[str] = {"。", "，", "、", "；", "：", "？", "！", "（", "）", "【", "】", "『", "』", "《", "》", "…", "—", "‘", "’", "“", "”"}

# --- 脚本默认配置 ---
DEFAULT_DIRECTORIES = ["./nyx/nyx_gui/frontend", "./bdk/usb"]
DEFAULT_EXTENSIONS = ['.c']
DEFAULT_INCLUDE_PUNCTUATION = True
DEFAULT_LINE_LENGTH = 50

def is_pure_chinese(char: str) -> bool:
    """
    检查一个字符是否为纯中文字符或中文标点。
    这是一个辅助函数，作为双重保险。
    """
    if len(char) != 1:
        return False
    # 使用Unicode编码范围进行判断
    code_point = ord(char)
    # CJK统一汉字
    if 0x4E00 <= code_point <= 0x9FFF:
        return True
    # CJK扩展A
    if 0x3400 <= code_point <= 0x4DBF:
        return True
    # CJK标点
    if 0x3000 <= code_point <= 0x303F:
        return True
    # 全角标点
    if 0xFF01 <= code_point <= 0xFF0F or \
       0xFF1A <= code_point <= 0xFF20 or \
       0xFF3B <= code_point <= 0xFF40 or \
       0xFF5B <= code_point <= 0xFF65:
        return True
    return False

def extract_chinese_chars_from_file(file_path: str) -> Set[str]:
    """
    从单个文件中提取所有中文字符和中文标点。
    """
    chinese_chars: Set[str] = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                for match in CHINESE_CHAR_PATTERN.finditer(line):
                    char = match.group()
                    # 双重保险：再次检查，确保万无一失
                    if is_pure_chinese(char):
                        chinese_chars.add(char)
    except FileNotFoundError:
        print(f"警告: 文件未找到 - {file_path}", file=sys.stderr)
    except PermissionError:
        print(f"警告: 权限不足，无法读取 - {file_path}", file=sys.stderr)
    except Exception as e:
        print(f"错误: 读取文件 {file_path} 时发生意外 - {e}", file=sys.stderr)

    return chinese_chars

def extract_chinese_chars_from_directory(directory: str, extensions: List[str]) -> Set[str]:
    """
    从指定目录及其子目录中提取所有特定扩展名文件中的中文字符。
    """
    if not os.path.isdir(directory):
        print(f"警告: 目录不存在或不是一个有效目录 - {directory}", file=sys.stderr)
        return set()

    all_chars: Set[str] = set()
    
    for root, _, files in os.walk(directory):
        for filename in files:
            if any(filename.lower().endswith(ext.lower()) for ext in extensions):
                file_path = os.path.join(root, filename)
                file_chars = extract_chinese_chars_from_file(file_path)
                all_chars.update(file_chars)
                
    return all_chars

def setup_argparse() -> argparse.Namespace:
    """
    设置并解析命令行参数。
    """
    parser = argparse.ArgumentParser(
        description="从指定目录的源文件中提取所有唯一的中文字符和中文标点符号。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        'directories',
        metavar='DIR',
        type=str,
        nargs='*',
        default=DEFAULT_DIRECTORIES,
        help=f'要扫描的一个或多个目录路径。\n默认: {DEFAULT_DIRECTORIES}'
    )
    
    parser.add_argument(
        '-e', '--extensions',
        type=str,
        nargs='+',
        default=DEFAULT_EXTENSIONS,
        help=f'需要处理的文件扩展名 (例如: -e .c .h .cpp)。\n默认: {DEFAULT_EXTENSIONS}'
    )
    
    parser.add_argument(
        '-np', '--no-punctuation',
        action='store_true',
        help=f'如果设置此项，则不添加内置的常用中文标点符号。\n默认: 添加标点 ({DEFAULT_INCLUDE_PUNCTUATION})'
    )
    
    parser.add_argument(
        '-l', '--line-length',
        type=int,
        default=DEFAULT_LINE_LENGTH,
        help=f'输出时每行显示的字符数量。\n默认: {DEFAULT_LINE_LENGTH}'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='安静模式，只输出最终的字符列表。'
    )

    return parser.parse_args()

def main():
    """主执行函数。"""
    args = setup_argparse()

    if not args.quiet:
        print(f"使用配置:")
        print(f"  扫描目录: {args.directories}")
        print(f"  文件扩展名: {args.extensions}")
        print(f"  包含标点符号: {not args.no_punctuation}")
        print(f"  每行显示字符数: {args.line_length}")
        print("-" * 40)

    all_chinese_chars: Set[str] = set()

    for directory in args.directories:
        if not args.quiet:
            print(f"正在扫描目录: {directory} ...")
        chars = extract_chinese_chars_from_directory(directory, args.extensions)
        new_chars_count = len(chars - all_chinese_chars)
        all_chinese_chars.update(chars)
        if not args.quiet:
            print(f"  从该目录中找到 {new_chars_count} 个新的唯一字符。")

    if not args.no_punctuation:
        initial_count = len(all_chinese_chars)
        all_chinese_chars.update(COMMON_CHINESE_PUNCTUATION)
        added_count = len(all_chinese_chars) - initial_count
        if not args.quiet:
            print(f"\n添加了 {added_count} 个常用中文标点符号。")

    sorted_chars: List[str] = sorted(all_chinese_chars)
    
    if not args.quiet:
        print("\n" + "="*50)
        print(f"扫描完成！总共找到 {len(sorted_chars)} 个唯一中文字符。")
        print("="*50)

    if sorted_chars:
        for i in range(0, len(sorted_chars), args.line_length):
            line = ''.join(sorted_chars[i:i + args.line_length])
            print(line)
    elif not args.quiet:
        print("未找到任何中文字符。")

if __name__ == "__main__":
    main()