# これはなに？

Excel 方眼紙をいい感じにマークダウン化するための実験場

# 現状の処理

1. Excel 方眼紙を用意する（`test4.xlsx`）
   - 前提
     - 罫線は消してあって、ページ設定はキチンとしてあって、PDF できれいに印刷できる
2. Excel を PDF 化する（`xlsx2pdf.py` ⇒ `test4.pdf`）
   - libreoffice on docker で Excel を PDF 化する
3. PDF をページ単位で画像化する（`pdf2img.py` ⇒ `test4/page_001.png`）
   - 前提
     - `Poppler`の最新リリースを ↓ から取得して、解凍して PATH を通しておく
       - [Releases · oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
4. ページ単位の画像をマークダウン化する（`img2md.py` ⇒ `test4.md`）
   - 画像と合わせて原本である PDF も与えると OCR にミスった情報を PDF と突き合わせていい感じに解釈してくれるかも？

## なぜこの処理なのか？

- Excel 方眼紙を使うようなプロジェクトでは、最終納品物は PDF（さらにもしかすると紙）のはず。
  - 印刷物としてきれいに見えるようにレイアウトされているはず
  - Excel としては正しくない使い方でも、PDF 化すれば見た目は完璧になる。
  - ただ PDF には罫線の情報は残らないけどセルの情報は残る。
    - このまま markdownit でマークダウン化してもセル単位でテキストがバラバラになった表を出力するだけ（`test4_NG.md`）。
  - 画像として見た目を解釈する必要がある。
- マルチモーダルな LLM は画像を比較的高精度に OCR できる。
  - わざわざ PDF 化するのは OCR で文字の解析にミスった場合に、PDF をセットで与えるようにすれば良しなに解釈してくれるかもしれないから。
