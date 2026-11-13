import re
from pathlib import Path

readme = Path("README.md").read_text(encoding="utf-8")

def make_preview(theme, bg, card_border, text_col):
    content = readme
    if theme == "light":
        content = re.sub(r'assets/([a-zA-Z0-9_\-\/]+)-dark\.svg', r'assets/\1-light.svg', content)
        content = re.sub(r'assets/([a-zA-Z0-9_\-\/]+)-still-dark\.svg', r'assets/\1-still-light.svg', content)
    else:
        content = re.sub(r'assets/([a-zA-Z0-9_\-\/]+)-light\.svg', r'assets/\1-dark.svg', content)
        content = re.sub(r'assets/([a-zA-Z0-9_\-\/]+)-still-light\.svg', r'assets/\1-still-dark.svg', content)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<base href="../">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dexter Profile Preview ({theme.title()})</title>
<style>
  body {{
    margin: 0;
    padding: 32px 16px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: {bg};
    color: {text_col};
    display: flex;
    justify-content: center;
  }}
  .container {{
    max-width: 896px;
    width: 100%;
    background: {bg};
    border: 1px solid {card_border};
    border-radius: 8px;
    padding: 28px 24px;
    box-sizing: border-box;
  }}
  img {{ max-width: 100%; height: auto; }}
  a {{ text-decoration: none; }}
  h3 {{ margin-top: 36px; margin-bottom: 16px; }}
  p {{ margin: 18px 0; }}
</style>
</head>
<body>
<div class="container">
{content}
</div>
</body>
</html>"""
    out_path = Path(f"output/preview-{theme}.html")
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    make_preview("dark", "#0d1117", "#30363d", "#c9d1d9")
    make_preview("light", "#ffffff", "#e1e4e8", "#24292f")
