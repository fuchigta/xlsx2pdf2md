import os
import subprocess
import argparse
import shutil

class ExcelToPdfConverter:
    def __init__(self, image_name="excel-to-pdf"):
        """初期化

        Args:
            image_name: 作成するDockerイメージ名
        """
        self.image_name = image_name
        
        # カレントディレクトリのDockerfileを使用
        self.dockerfile_path = os.path.join(os.getcwd(), "Dockerfile")
            
        # Dockerイメージをビルド
        self._build_docker_image()
    
    def _build_docker_image(self):
        """Dockerイメージをビルド"""
        # ビルドコマンドを実行
        build_cmd = [
            "podman", "build", 
            "-t", self.image_name,
            "-f", self.dockerfile_path,
            os.getcwd()
        ]
        
        try:
            print(f"Dockerイメージをビルド中: {self.image_name}")
            subprocess.run(build_cmd, check=True)
            print(f"イメージのビルドに成功しました: {self.image_name}")
        except subprocess.CalledProcessError as e:
            print(f"イメージのビルドに失敗しました: {str(e)}")
            raise
    
    def convert_file(self, excel_file, pdf_file=None):
        """Excelファイルを1つPDFに変換

        Args:
            excel_file: 変換するExcelファイルのパス
            pdf_file: 出力PDFのパス (Noneの場合は同じ場所に同名で作成)
        
        Returns:
            出力されたPDFファイルのパス
        """
        # 絶対パスに変換
        excel_path = os.path.abspath(excel_file)
        
        # 出力PDFファイルのパスを決定
        if pdf_file is None:
            pdf_file = os.path.splitext(excel_path)[0] + '.pdf'
        pdf_path = os.path.abspath(pdf_file)
        
        # 入出力ディレクトリのパス
        input_dir = os.path.dirname(excel_path)
        output_dir = os.path.dirname(pdf_path)
        
        # ファイル名のみを取得
        excel_filename = os.path.basename(excel_path)
        
        # 実行コマンド
        cmd = [
            "podman", "run", "--rm",
            "-v", f"{input_dir}:/input",
            "-v", f"{output_dir}:/output",
            self.image_name,
            "--outdir", "/output", f"/input/{excel_filename}"
        ]
        
        try:
            print(f"変換中: {excel_file} -> {pdf_file}")
            subprocess.run(cmd, check=True)
            
            # LibreOfficeは元のファイル名を使用してPDFを出力
            expected_pdf = os.path.join(output_dir, os.path.splitext(excel_filename)[0] + '.pdf')
            
            # 必要に応じてリネーム
            if expected_pdf != pdf_path and os.path.exists(expected_pdf):
                shutil.move(expected_pdf, pdf_path)
                
            print(f"変換完了: {pdf_file}")
            return pdf_path
            
        except subprocess.CalledProcessError as e:
            print(f"変換に失敗しました: {str(e)}")
            raise
    
    def batch_convert(self, input_dir, output_dir=None, pattern=None):
        """ディレクトリ内のExcelファイルをまとめて変換

        Args:
            input_dir: Excelファイルがあるディレクトリ
            output_dir: PDF出力先ディレクトリ (Noneの場合は同じディレクトリ)
            pattern: 変換対象のファイル拡張子 (Noneの場合はデフォルト)
        
        Returns:
            変換されたPDFファイルのパスのリスト
        """
        # 入力ディレクトリの絶対パス
        input_dir = os.path.abspath(input_dir)
        
        # 出力ディレクトリの設定
        if output_dir is None:
            output_dir = input_dir
        else:
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
        
        # 対象拡張子
        if pattern is None:
            pattern = ('.xlsx', '.xls', '.xlsm')
        
        # 変換対象ファイルの取得
        excel_files = [f for f in os.listdir(input_dir) 
                      if f.lower().endswith(pattern)]
        
        # 結果のリスト
        converted_files = []
        
        # 各ファイルを変換
        for excel_file in excel_files:
            excel_path = os.path.join(input_dir, excel_file)
            pdf_file = os.path.splitext(excel_file)[0] + '.pdf'
            pdf_path = os.path.join(output_dir, pdf_file)
            
            try:
                result = self.convert_file(excel_path, pdf_path)
                converted_files.append(result)
            except Exception as e:
                print(f"ファイル {excel_file} の変換中にエラーが発生: {str(e)}")
        
        return converted_files


def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='ExcelファイルをPDFに変換')
    parser.add_argument('input', help='変換するExcelファイルまたはディレクトリのパス')
    parser.add_argument('--output', '-o', help='出力PDFファイルまたはディレクトリのパス')
    parser.add_argument('--image-name', '-i', default='excel-to-pdf', help='Dockerイメージ名')
    parser.add_argument('--batch', '-b', action='store_true', help='バッチモード (入力がディレクトリの場合)')
    args = parser.parse_args()
    
    try:
        # コンバーターの初期化
        converter = ExcelToPdfConverter(image_name=args.image_name)
        
        # パス確認
        input_path = os.path.abspath(args.input)
        
        # ディレクトリかファイルかを判定
        if os.path.isdir(input_path) or args.batch:
            # バッチモード
            output_dir = args.output
            converted = converter.batch_convert(input_path, output_dir)
            print(f"{len(converted)}個のファイルを変換しました")
        else:
            # 単一ファイルモード
            converter.convert_file(input_path, args.output)
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())