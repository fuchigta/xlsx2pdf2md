import argparse
from pathlib import Path
from typing import Optional
import base64
import io

from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def encode_image_to_base64(image_path: str, max_size: int = 2000) -> str:
    """画像をbase64エンコードする"""
    img = Image.open(image_path)
    
    # 画像が大きすぎる場合はリサイズ
    width, height = img.size
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 画像をバイトストリームに変換
    buffered = io.BytesIO()
    img.convert('RGB').save(buffered, format="JPEG", quality=85)
    
    # Base64エンコード
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def convert_image_to_markdown(image_path: str, model_name: str = "gemini-2.0-flash") -> str:
    """単一の画像をマークダウンに変換する"""
    # 画像をBase64エンコード
    base64_image = encode_image_to_base64(image_path)
    
    # LLMを初期化
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
    )
    
    # シンプルにメッセージを作成
    messages = [
        {
            "role": "system",
            "content": """
あなたはPDF画像をマークダウンに変換する専門家です。画像内のテキスト、表、その他の要素を識別し、整形されたマークダウンに変換してください。

次の点に注意してください：
1. 表は正確にマークダウン表形式に変換してください
2. 見出しは適切なマークダウン見出し (#, ##, ###) で表現してください
3. 箇条書きリストや番号付きリストを保持してください
4. テキストの配置や基本的な書式を保持してください
5. 可能であれば画像内の図表を説明してください

変換したマークダウンのみを返し、画像についての説明や分析などは含めないでください。
            """
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "この画像をマークダウンに変換してください："},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    # LLMに直接リクエスト
    response = llm.invoke(messages)
    return response.content

def convert_images_to_markdown(
    image_dir: str,
    output_file: Optional[str] = None,
    model_name: str = "gpt-4-vision-preview"
) -> str:
    """ディレクトリ内の画像ファイルをマークダウンに変換する"""
    # 画像ファイルのパスを取得（昇順でソート）
    image_dir = Path(image_dir)
    image_files = sorted([
        str(f) for f in image_dir.glob("*") 
        if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    ])
    
    if not image_files:
        raise ValueError(f"画像ファイルが {image_dir} に見つかりませんでした")
    
    print(f"{len(image_files)} 個の画像ファイルが見つかりました")
    
    all_markdown = []
    
    # 各画像を処理
    for i, image_path in enumerate(image_files):
        print(f"処理中 {i+1}/{len(image_files)}: {image_path}")
        
        # 画像をマークダウンに変換
        markdown_text = convert_image_to_markdown(image_path, model_name)
        
        # ページ区切りを追加（最後のページを除く）
        if i < len(image_files) - 1:
            markdown_text += "\n\n---\n\n"
        
        all_markdown.append(markdown_text)
    
    # すべてのマークダウンを結合
    final_markdown = "".join(all_markdown)
    
    # ファイルに出力（指定がある場合）
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_markdown)
        print(f"マークダウンを {output_file} に保存しました")
    
    return final_markdown

def main():
    """コマンドラインからの実行用のメイン関数"""
    parser = argparse.ArgumentParser(description="画像をマークダウンに変換するスクリプト")
    parser.add_argument("image_dir", help="変換する画像ファイルが含まれるディレクトリ")
    parser.add_argument("-o", "--output", help="出力マークダウンファイルのパス")
    parser.add_argument("--model", default="gemini-2.0-flash", 
                        help="使用するLLMモデル名（デフォルト: gemini-2.0-flash）")
    
    args = parser.parse_args()
    
    # 変換実行
    convert_images_to_markdown(
        args.image_dir, 
        args.output, 
        args.model
    )

if __name__ == "__main__":
    main()