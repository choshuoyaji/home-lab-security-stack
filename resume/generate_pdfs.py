import markdown
from weasyprint import HTML

def md_to_pdf(md_path, pdf_path, css):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=['tables'])
    full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{css}</style></head>
<body>{html_content}</body></html>"""
    HTML(string=full_html).write_pdf(pdf_path)
    print(f"Generated: {pdf_path}")

css_en = """
@page { size: A4; margin: 2cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }
h1 { font-size: 22pt; color: #1a1a1a; border-bottom: 2px solid #2c5aa0; padding-bottom: 5px; margin-bottom: 5px; }
h2 { font-size: 14pt; color: #2c5aa0; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-top: 18px; }
h3 { font-size: 12pt; color: #444; margin-top: 12px; margin-bottom: 4px; }
h4 { font-size: 11pt; color: #555; margin-top: 8px; margin-bottom: 2px; }
ul { margin-top: 4px; margin-bottom: 4px; }
li { margin-bottom: 3px; }
strong { color: #1a1a1a; }
hr { border: none; border-top: 1px solid #ddd; margin: 10px 0; }
p { margin: 4px 0; }
"""

css_jp = """
@page { size: A4; margin: 2cm; }
body { font-family: "Hiragino Kaku Gothic Pro", "Yu Gothic", "Meiryo", sans-serif; font-size: 10.5pt; line-height: 1.6; color: #333; }
h1 { font-size: 20pt; color: #1a1a1a; border-bottom: 2px solid #2c5aa0; padding-bottom: 5px; margin-bottom: 5px; text-align: center; }
h2 { font-size: 13pt; color: #2c5aa0; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-top: 16px; }
h3 { font-size: 11.5pt; color: #444; margin-top: 10px; margin-bottom: 4px; }
h4 { font-size: 10.5pt; color: #555; margin-top: 8px; margin-bottom: 2px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; }
th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; font-size: 10pt; }
th { background-color: #f5f5f5; }
ul { margin-top: 4px; margin-bottom: 4px; }
li { margin-bottom: 2px; }
strong { color: #1a1a1a; }
hr { border: none; border-top: 1px solid #ddd; margin: 10px 0; }
p { margin: 4px 0; }
"""

base = "/Users/odatakahiro/.openclaw/workspace/resume"
md_to_pdf(f"{base}/Takahiro_Oda_Resume_2026.md", f"{base}/Takahiro_Oda_Resume_2026.pdf", css_en)
md_to_pdf(f"{base}/職務経歴書_小田孝浩_2026.md", f"{base}/職務経歴書_小田孝浩_2026.pdf", css_jp)
