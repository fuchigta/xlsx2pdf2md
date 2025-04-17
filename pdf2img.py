import os
import sys
from pdf2image import convert_from_path
import argparse
from pathlib import Path

def convert_pdf_to_images(pdf_path, output_dir=None, dpi=300, fmt="png"):
    """
    PDFの各ページを画像として保存する関数
    
    Args:
        pdf_path (str): PDFファイルのパス
        output_dir (str, optional): 出力ディレクトリ。指定がなければPDFと同名のディレクトリを作成
        dpi (int, optional): 画像の解像度。デフォルトは300
        fmt (str, optional): 出力画像の形式。デフォルトは"png"
    
    Returns:
        str: 画像が保存されたディレクトリのパス
    """
    # 入力PDFのパスを処理
    pdf_path = Path(pdf_path)
    
    # 出力ディレクトリの設定
    if output_dir is None:
        output_dir = pdf_path.stem  # PDFのファイル名（拡張子なし）
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # PDFを画像に変換
    try:
        # Windowsの場合はpopplerのパスを指定する必要があるかもしれない
        # その場合は以下のようにパスを指定してください
        # images = convert_from_path(pdf_path, dpi=dpi, poppler_path=r"C:\path\to\poppler\bin")
        images = convert_from_path(pdf_path, dpi=dpi)
        
        # 各ページを画像として保存
        for i, image in enumerate(images):
            image_path = output_dir / f"page_{i+1:03d}.{fmt}"
            image.save(str(image_path), fmt.upper())
            print(f"ページ {i+1}/{len(images)} を保存: {image_path}")
        
        print(f"\n変換完了: {len(images)}ページのPDFを画像に変換し、{output_dir}に保存しました。")
        return str(output_dir)
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def main():
    """
    コマンドラインからの実行用のメイン関数
    """
    parser = argparse.ArgumentParser(description="PDFを画像に変換するスクリプト")
    parser.add_argument("pdf_path", help="変換するPDFファイルのパス")
    parser.add_argument("-o", "--output", help="出力ディレクトリ（指定しない場合はPDFと同名のディレクトリ）")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="出力画像の解像度（デフォルト: 300）")
    parser.add_argument("-f", "--format", default="png", choices=["png", "jpg", "jpeg", "tiff"], 
                        help="出力画像の形式（デフォルト: png）")
    
    args = parser.parse_args()
    
    # PDFの存在確認
    if not os.path.exists(args.pdf_path):
        print(f"エラー: 指定されたPDFファイル '{args.pdf_path}' が見つかりません。")
        sys.exit(1)
    
    # 変換実行
    convert_pdf_to_images(args.pdf_path, args.output, args.dpi, args.format)

if __name__ == "__main__":
    main()