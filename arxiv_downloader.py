#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arxiv
import requests
import os
import sys
import time
import argparse
from pathlib import Path
from urllib.parse import urlparse

def search_arxiv(keywords, max_results=100, use_or=False):
    """
    arXivで指定されたキーワードを使用して論文を検索します。
    
    Args:
        keywords (list): 検索キーワードのリスト
        max_results (int): 取得する最大論文数
        use_or (bool): キーワードをORで結合するかどうか
    
    Returns:
        list: 検索結果の論文リスト
    """
    print(f"キーワード '{' '.join(keywords)}' でarXivを検索中...")
    
    # 検索クエリを作成
    if use_or:
        query = ' OR '.join(keywords)
    else:
        query = ' AND '.join(keywords)
    
    # arXivクライアントを作成
    client = arxiv.Client()
    
    # 検索オブジェクトを作成
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    # 結果を取得（非推奨のメソッドを避ける）
    results = list(client.results(search))
    
    print(f"{len(results)}件の論文が見つかりました。")
    return results

def download_pdf(paper, download_dir, force_download=False):
    """
    論文のPDFをダウンロードします。
    
    Args:
        paper (arxiv.Result): 論文情報
        download_dir (str): ダウンロード先ディレクトリ
        force_download (bool): 既存のファイルを上書きするかどうか
    
    Returns:
        bool: ダウンロードが成功したかどうか
    """
    # PDFのURLを取得
    pdf_url = paper.pdf_url
    
    # ファイル名を作成（arXiv IDを使用）
    parsed_url = urlparse(pdf_url)
    path_parts = parsed_url.path.split('/')
    arxiv_id = path_parts[-1]
    if not arxiv_id.endswith('.pdf'):
        arxiv_id = f"{arxiv_id}.pdf"
    
    # ダウンロード先のパスを作成
    download_path = os.path.join(download_dir, arxiv_id)
    
    # 既にファイルが存在する場合はスキップ（force_downloadがFalseの場合）
    if os.path.exists(download_path) and not force_download:
        print(f"ファイル {arxiv_id} は既に存在します。スキップします。")
        return True
    
    try:
        # PDFをダウンロード
        print(f"ダウンロード中: {paper.title} ({arxiv_id})")
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # ファイルに保存
        with open(download_path, 'wb') as f:
            f.write(response.content)
        
        print(f"ダウンロード完了: {download_path}")
        return True
    
    except Exception as e:
        print(f"ダウンロード失敗: {arxiv_id} - エラー: {str(e)}")
        return False

def main():
    """
    メイン関数
    """
    # コマンドライン引数のパーサーを設定
    parser = argparse.ArgumentParser(
        description='arXivから指定したキーワードで論文を検索し、PDFをダウンロードします。'
    )
    parser.add_argument(
        'keywords',
        nargs='+',
        help='検索キーワード（複数指定可能）'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=200,
        help='取得する最大論文数（デフォルト: 200）'
    )
    parser.add_argument(
        '--use-or',
        action='store_true',
        help='キーワードをORで結合する（デフォルトはAND）'
    )
    parser.add_argument(
        '--force-download',
        action='store_true',
        help='既にダウンロード済みのファイルも再ダウンロードする'
    )
    
    # 引数を解析
    args = parser.parse_args()
    
    # キーワードを取得
    keywords = args.keywords
    
    # ダウンロードディレクトリを確認
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dl")
    os.makedirs(download_dir, exist_ok=True)
    
    # arXivを検索
    papers = search_arxiv(keywords, args.max_results, args.use_or)
    
    if not papers:
        print("論文が見つかりませんでした。")
        sys.exit(0)
    
    # 論文情報を表示
    print("\n検索結果:")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title} ({paper.published.year})")
    
    # PDFをダウンロード
    print("\nPDFのダウンロードを開始します...")
    success_count = 0
    for paper in papers:
        if download_pdf(paper, download_dir, args.force_download):
            success_count += 1
        # arXivのAPIレート制限を回避するために少し待機
        time.sleep(1)
    
    print(f"\nダウンロード完了: {success_count}/{len(papers)}件のPDFをダウンロードしました。")
    print(f"ダウンロードディレクトリ: {download_dir}")

if __name__ == "__main__":
    main()
