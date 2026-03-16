#!/usr/bin/env python3
import markdown
import weasyprint
import sys
import os

CSS = """
@page {
    size: A4;
    margin: 20mm 18mm;
}
body {
    font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic", "Noto Sans CJK JP", "Meiryo", sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #222;
}
h1 {
    font-size: 18pt;
    border-bottom: 2px solid #333;
    padding-bottom: 4px;
    margin-bottom: 8px;
}
h2 {
    font-size: 13pt;
    color: #1a5276;
    border-bottom: 1px solid #aaa;
    padding-bottom: 3px;
    margin-top: 16px;
    margin-bottom: 8px;
}
h3 {
    font-size: 11pt;
    color: #2c3e50;
    margin-top: 12px;
    margin-bottom: 4px;
}
h4 {
    font-size: 10pt;
    color: #34495e;
    margin-top: 10px;
    margin-bottom: 4px;
}
hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 12px 0;
}
ul {
    margin: 4px 0;
    padding-left: 20px;
}
li {
    margin-bottom: 3px;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 9.5pt;
}
th, td {
    border: 1px solid #ccc;
    padding: 5px 8px;
    text-align: left;
}
th {
    background-color: #f0f4f8;
    font-weight: bold;
}
strong {
    color: #1a1a1a;
}
p {
    margin: 4px 0;
}
"""

def md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html}</body></html>"""

    weasyprint.HTML(string=full_html).write_pdf(pdf_path)
    print(f"Created: {pdf_path}")

if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    md_to_pdf(os.path.join(base, 'Takahiro_Oda_Resume_EN.md'),
              os.path.join(base, 'Takahiro_Oda_Resume_EN.pdf'))
    md_to_pdf(os.path.join(base, 'Takahiro_Oda_職務経歴書.md'),
              os.path.join(base, 'Takahiro_Oda_職務経歴書.pdf'))
