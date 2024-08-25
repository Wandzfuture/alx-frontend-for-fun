#!/usr/bin/python3
"""
A script that converts a Markdown file to HTML.

Usage: ./markdown2html.py <input_file> <output_file>
"""

import sys
import os
import re
import hashlib


def md5_hash(text):
    """
    Convert text to MD5 hash (lowercase).
    """
    return hashlib.md5(text.encode()).hexdigest()


def remove_c(text):
    """
    Remove all 'c' characters (case insensitive) from the text.
    """
    return re.sub(r'[cC]', '', text)


def parse_inline_markdown(text):
    """
    Parse inline Markdown elements and convert them to HTML.
    """
    # Convert bold text (both ** and __ syntax)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)

    # Convert [[text]] to MD5 hash
    text = re.sub(r'\[\[(.*?)\]\]', lambda m: md5_hash(m.group(1)), text)

    # Convert ((text)) by removing all 'c' characters
    text = re.sub(r'\(\((.*?)\)\)', lambda m: remove_c(m.group(1)), text)

    return text


def parse_headings(line):
    """
    Parse Markdown headings and convert them to HTML.
    """
    heading_pattern = r'^(#{1,6})\s(.+)$'
    match = re.match(heading_pattern, line)
    if match:
        level = len(match.group(1))
        content = parse_inline_markdown(match.group(2))
        return f"<h{level}>{content}</h{level}>\n"
    return None


def parse_unordered_list(lines):
    """
    Parse Markdown unordered list and convert it to HTML.
    """
    if not lines or not lines[0].startswith('- '):
        return None

    html_list = ["<ul>"]
    for line in lines:
        if line.startswith('- '):
            item = parse_inline_markdown(line[2:].strip())
            html_list.append(f"<li>{item}</li>")
        else:
            break
    html_list.append("</ul>")
    return '\n'.join(html_list) + '\n', len(html_list) - 2


def parse_ordered_list(lines):
    """
    Parse Markdown ordered list and convert it to HTML.
    """
    if not lines or not lines[0].startswith('* '):
        return None

    html_list = ["<ol>"]
    for line in lines:
        if line.startswith('* '):
            item = parse_inline_markdown(line[2:].strip())
            html_list.append(f"<li>{item}</li>")
        else:
            break
    html_list.append("</ol>")
    return '\n'.join(html_list) + '\n', len(html_list) - 2


def parse_paragraph(lines):
    """
    Parse Markdown paragraph and convert it to HTML.
    """
    if not lines or lines[0].strip() == '':
        return None

    html_para = ["<p>"]
    for i, line in enumerate(lines):
        if line.strip() == '':
            break
        if i > 0:
            html_para.append("<br/>")
        html_para.append(parse_inline_markdown(line.strip()))
    html_para.append("</p>")
    return '\n'.join(html_para) + '\n', len(html_para) - 2


def convert_markdown_to_html(input_file, output_file):
    """
    Convert Markdown content to HTML.
    """
    with open(input_file, 'r') as md_file, open(output_file, 'w') as html_file:
        lines = md_file.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check for headings
            heading = parse_headings(line)
            if heading:
                html_file.write(heading)
                i += 1
                continue

            # Check for unordered list
            ul_result = parse_unordered_list(lines[i:])
            if ul_result:
                html_list, items_count = ul_result
                html_file.write(html_list)
                i += items_count
                continue

            # Check for ordered list
            ol_result = parse_ordered_list(lines[i:])
            if ol_result:
                html_list, items_count = ol_result
                html_file.write(html_list)
                i += items_count
                continue

            # Check for paragraph
            para_result = parse_paragraph(lines[i:])
            if para_result:
                html_para, lines_count = para_result
                html_file.write(html_para)
                i += lines_count
                continue

            # If not a special element, move to next line
            i += 1


def main():
    """
    Main function to handle the Markdown to HTML conversion process.
    """
    # Check if the correct number of arguments is provided
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if the input file exists
    if not os.path.exists(input_file):
        sys.stderr.write(f"Missing {input_file}\n")
        sys.exit(1)

    # Convert Markdown to HTML
    convert_markdown_to_html(input_file, output_file)

    sys.exit(0)


if __name__ == "__main__":
    main()
