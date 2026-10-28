"""manuscript.md -> manuscript.pdf (pandoc -> HTML/MathML -> WeasyPrint). Requires: pip install pypandoc_binary weasyprint"""
from pathlib import Path
import pypandoc, weasyprint

HERE = Path(__file__).resolve().parent
css = """
@page { size: A4; margin: 20mm 18mm; @bottom-center { content: counter(page); font-size: 9pt; } }
body { font-family: 'DejaVu Serif', serif; font-size: 10pt; line-height: 1.35; }
h1 { font-size: 16pt; } h2 { font-size: 12.5pt; margin-top: 1.2em; } code { font-size: 8.5pt; }
table { border-collapse: collapse; font-size: 7.5pt; width: 100%; margin: 6pt 0; }
th, td { border: 0.5pt solid #888; padding: 2pt 3pt; vertical-align: top; } th { background: #eee; }
img { max-width: 100%; display: block; margin: 6pt auto; } pre { font-size: 8pt; white-space: pre-wrap; }
"""
html = pypandoc.convert_text((HERE / "manuscript.md").read_text(), "html5", format="markdown+pipe_tables+tex_math_dollars",
                             extra_args=["--standalone", "--mathml", f"--resource-path={HERE}", "--metadata", "title= "])
html = html.replace("</head>", f"<style>{css}</style></head>", 1)
weasyprint.HTML(string=html, base_url=str(HERE)).write_pdf(str(HERE / "manuscript.pdf"))
print("manuscript.pdf written")
