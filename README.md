# ArXiv Downloader

## Overview
ArXiv Downloader is a Python-based command-line tool that allows you to search for academic papers on arXiv.org using specific keywords and automatically download their PDFs. The tool makes it easy to batch download multiple research papers, which is useful for literature reviews, research projects, or staying updated in your field of interest.

## Installation

### Prerequisites
- Python 3.6 or higher
- Git

### Steps
1. Clone the repository:
   ```
   git clone https://github.com/daishir0/arxiv-downloader
   ```

2. Navigate to the project directory:
   ```
   cd arxiv-downloader
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
The basic usage is as follows:

```
python arxiv_downloader.py KEYWORDS [OPTIONS]
```

### Arguments
- `KEYWORDS`: One or more search terms (required)

### Options
- `--max-results NUMBER`: Maximum number of papers to retrieve (default: 1000)
- `--use-or`: Use OR logic between keywords instead of AND (default: AND)
- `--force-download`: Download papers even if they already exist locally
- `--date-from YYYYMM`: Only retrieve papers submitted on or after the specified date (format: YYYYMM)
- `--date-to YYYYMM`: Only retrieve papers submitted on or before the specified date (format: YYYYMM)

### Examples
1. Search for papers about "quantum computing":
   ```
   python arxiv_downloader.py "quantum computing"
   ```

2. Search for papers about "machine learning" OR "deep learning" with a maximum of 50 results:
   ```
   python arxiv_downloader.py "machine learning" "deep learning" --use-or --max-results 50
   ```

3. Force re-download of papers about "neural networks":
   ```
   python arxiv_downloader.py "neural networks" --force-download
   ```

4. Search for papers about "transformer" submitted since October 2024:
   ```
   python arxiv_downloader.py "transformer" --date-from 202410
   ```

5. Search for papers about "large language models" submitted between January and March 2025:
   ```
   python arxiv_downloader.py "large language models" --date-from 202501 --date-to 202503
   ```

## Notes
- Downloaded PDFs are stored in a `dl` subdirectory within the project folder
- The tool automatically avoids downloading duplicate papers unless the `--force-download` option is used
- A small delay between downloads helps avoid hitting arXiv's API rate limits
- Papers are sorted by submission date, with the most recent papers first

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

# ArXiv Downloader

## 概要
ArXiv Downloaderは、arXiv.org上の学術論文を特定のキーワードで検索し、そのPDFを自動的にダウンロードできるPythonベースのコマンドラインツールです。このツールを使用すると、複数の研究論文を一括ダウンロードすることができ、文献レビュー、研究プロジェクト、または専門分野の最新情報の収集に役立ちます。

## インストール方法

### 前提条件
- Python 3.6以上
- Git

### 手順
1. リポジトリをクローンします:
   ```
   git clone https://github.com/daishir0/arxiv-downloader
   ```

2. プロジェクトディレクトリに移動します:
   ```
   cd arxiv-downloader
   ```

3. 必要な依存関係をインストールします:
   ```
   pip install -r requirements.txt
   ```

## 使い方
基本的な使用方法は次のとおりです:

```
python arxiv_downloader.py キーワード [オプション]
```

### 引数
- `キーワード`: 1つ以上の検索語（必須）

### オプション
- `--max-results 数値`: 取得する最大論文数（デフォルト: 1000）
- `--use-or`: キーワード間にOR論理を使用（デフォルト: AND）
- `--force-download`: ローカルに既に存在する論文も再ダウンロード
- `--date-from YYYYMM`: 指定した日付以降に投稿された論文のみを取得（形式: YYYYMM）
- `--date-to YYYYMM`: 指定した日付以前に投稿された論文のみを取得（形式: YYYYMM）

### 使用例
1. 「量子コンピューティング」に関する論文を検索:
   ```
   python arxiv_downloader.py "quantum computing"
   ```

2. 「機械学習」または「深層学習」に関する論文を最大50件検索:
   ```
   python arxiv_downloader.py "machine learning" "deep learning" --use-or --max-results 50
   ```

3. 「ニューラルネットワーク」に関する論文を強制的に再ダウンロード:
   ```
   python arxiv_downloader.py "neural networks" --force-download
   ```

4. 2024年10月以降に投稿された「トランスフォーマー」に関する論文を検索:
   ```
   python arxiv_downloader.py "transformer" --date-from 202410
   ```

5. 2025年1月から3月の間に投稿された「大規模言語モデル」に関する論文を検索:
   ```
   python arxiv_downloader.py "large language models" --date-from 202501 --date-to 202503
   ```

## 注意点
- ダウンロードされたPDFはプロジェクトフォルダ内の`dl`サブディレクトリに保存されます
- `--force-download`オプションを使用しない限り、ツールは重複した論文のダウンロードを自動的に回避します
- ダウンロード間の小さな遅延により、arXivのAPIレート制限に達するのを防ぎます
- 論文は投稿日でソートされ、最新の論文が最初に表示されます

## ライセンス
このプロジェクトはMITライセンスの下でライセンスされています。詳細はLICENSEファイルを参照してください。
