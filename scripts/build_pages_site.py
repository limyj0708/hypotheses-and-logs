#!/usr/bin/env python3
"""Execute the public research notebook and export a code-free GitHub Pages page."""

from __future__ import annotations

import re
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from traitlets.config import Config


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "gmo_election_cycle_hypothesis_test.ipynb"
OUTPUT = ROOT / "docs" / "index.html"
CSS_PATH = "assets/site.css"
REPOSITORY_URL = "https://github.com/limyj0708/hypotheses-and-logs"
NOTEBOOK_URL = f"{REPOSITORY_URL}/blob/main/notebooks/{NOTEBOOK.name}"


def inject_site_chrome(html: str) -> str:
    head = f'''<meta name="description" content="미국 대통령 선거주기 가설을 공개 데이터로 재현하고 검정한 기록입니다.">
<meta property="og:title" content="대통령 선거주기의 7개월, 정말 유난히 좋았나 | 가설과 로그">
<meta property="og:description" content="겹치는 기간의 함정을 피하면서 공개된 시장 가설을 다시 확인해 본 기록">
<link rel="stylesheet" href="{CSS_PATH}">
<title>대통령 선거주기의 7개월, 정말 유난히 좋았나 | 가설과 로그</title>'''
    header = f'''<header class="site-header">
  <a class="brand" href="./">가설과 로그</a>
  <p>가설, 데이터, 삶</p>
  <nav aria-label="글 링크">
    <a href="{NOTEBOOK_URL}">원본 노트북</a>
    <a href="{REPOSITORY_URL}">GitHub</a>
  </nav>
</header>'''
    footer = f'''<footer class="site-footer">
  <p>이 글은 공개 데이터로 수행한 재현 분석입니다. 투자 권유가 아니며, 과거의 패턴은 미래 수익을 보장하지 않습니다.</p>
  <p><a href="{NOTEBOOK_URL}">원본 노트북 보기</a> · <a href="{REPOSITORY_URL}">재현 코드 보기</a></p>
</footer>'''
    html = html.replace("</head>", f"{head}\n</head>")
    html = re.sub(r"(<body[^>]*>)", r"\1\n" + header, html, count=1)
    return html.replace("</body>", f"{footer}\n</body>")


def main() -> None:
    if not NOTEBOOK.exists():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK}")
    if not (ROOT / "data" / "indices" / "us_price_indices_daily.csv").exists():
        raise FileNotFoundError("Price data is missing. Run scripts/fetch_index_price_history.py first.")

    notebook = nbformat.read(NOTEBOOK, as_version=4)
    client = NotebookClient(notebook, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}})
    client.execute()

    config = Config()
    config.HTMLExporter.exclude_input = True
    config.HTMLExporter.exclude_input_prompt = True
    config.HTMLExporter.exclude_output_prompt = True
    exporter = HTMLExporter(config=config)
    exporter.template_name = "lab"
    html, _ = exporter.from_notebook_node(notebook)

    public_html = inject_site_chrome(html)
    public_html = "\n".join(line.rstrip() for line in public_html.splitlines()) + "\n"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(public_html, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
