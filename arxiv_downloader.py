#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import arxiv
import requests
import os
import sys
import time
import csv
import argparse
import datetime
from pathlib import Path
from urllib.parse import urlparse

def search_arxiv(keywords, max_results=1000, use_or=False, date_from=None, date_to=None):
    """
    arXivで指定されたキーワードを使用して論文を検索します。
    
    Args:
        keywords (list): 検索キーワードのリスト
        max_results (int): 取得する最大論文数
        use_or (bool): キーワードをORで結合するかどうか
        date_from (str): この日付以降の論文を検索 (YYYYMM形式)
        date_to (str): この日付以前の論文を検索 (YYYYMM形式)
    
    Returns:
        list: 検索結果の論文リスト
    """
    print(f"キーワード '{' '.join(keywords)}' でarXivを検索中...")
    
    # 検索クエリを作成
    if use_or:
        query = ' OR '.join(keywords)
    else:
        query = ' AND '.join(keywords)
    
    # 日付フィルタを追加
    date_filter = []
    if date_from:
        date_filter.append(f"submittedDate:[{date_from} TO 999912]")
    if date_to:
        # すでにdate_fromが設定されている場合は上書き
        if date_from:
            date_filter = [f"submittedDate:[{date_from} TO {date_to}]"]
        else:
            date_filter.append(f"submittedDate:[000001 TO {date_to}]")
    
    # 日付フィルタがある場合、クエリに追加
    if date_filter:
        query = f"({query}) AND {' AND '.join(date_filter)}"
    
    print(f"検索クエリ: {query}")
    
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
    
    # 日付フィルタが指定されている場合、結果を日付でさらにフィルタリング
    if date_from or date_to:
        filtered_results = []
        date_from_obj = None
        date_to_obj = None
        
        if date_from:
            year = int(date_from[:4])
            month = int(date_from[4:6])
            date_from_obj = datetime.datetime(year, month, 1)
        
        if date_to:
            year = int(date_to[:4])
            month = int(date_to[4:6])
            # 月の最終日を設定
            if month == 12:
                next_year = year + 1
                next_month = 1
            else:
                next_year = year
                next_month = month + 1
            date_to_obj = datetime.datetime(next_year, next_month, 1) - datetime.timedelta(days=1)
        
        print("日付フィルタリングを適用中...")
        
        for paper in results:
            # paper.publishedはタイムゾーン情報を持つ可能性があるため、
            # タイムゾーン情報を削除して比較する
            paper_date = paper.published
            if hasattr(paper_date, 'tzinfo') and paper_date.tzinfo is not None:
                # タイムゾーン情報を削除（ローカル時間に変換）
                paper_date = paper_date.replace(tzinfo=None)
            
            include_paper = True
            
            if date_from_obj and paper_date < date_from_obj:
                include_paper = False
            
            if date_to_obj and paper_date > date_to_obj:
                include_paper = False
            
            if include_paper:
                filtered_results.append(paper)
        
        results = filtered_results
    
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

def _get_arxiv_id(paper):
    """
    論文オブジェクトからarXiv ID（バージョン付き、例：2401.12345v1）を取得します。
    """
    parsed_url = urlparse(paper.entry_id)
    return parsed_url.path.split('/')[-1]

def _escape_bibtex(text):
    """
    BibTeXの特殊文字をエスケープします。
    """
    if text is None:
        return ""
    text = str(text)
    # バックスラッシュは一旦プレースホルダに退避する。
    # 先に \textbackslash{} へ変換すると、後続の { } エスケープが
    # 挿入した波括弧まで壊してしまうため。
    placeholder = '\x00BACKSLASH\x00'
    text = text.replace('\\', placeholder)
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    # 退避していたバックスラッシュを最終形に戻す
    text = text.replace(placeholder, r'\textbackslash{}')
    # 改行・連続する空白を1つのスペースにまとめる
    return ' '.join(text.split())

def _make_bibtex_key(paper, arxiv_id):
    """
    BibTeXのエントリキーを 著者名_年_arXivID 形式で生成します。
    """
    if paper.authors:
        # 筆頭著者の姓（最後の単語）を使用
        first_author = paper.authors[0].name.split()[-1]
    else:
        first_author = "unknown"
    # キーとして安全な文字のみを残す
    first_author = ''.join(c for c in first_author if c.isalnum())
    year = paper.published.year if paper.published else "nd"
    # arXiv IDのドット・スラッシュをアンダースコアに変換
    safe_id = arxiv_id.replace('.', '_').replace('/', '_')
    return f"{first_author}{year}_{safe_id}"

def export_metadata(papers, download_dir, export_format):
    """
    検索結果の書誌情報をBibTeXおよび/またはCSV形式で出力します。

    Args:
        papers (list): 論文オブジェクトのリスト
        download_dir (str): 出力先ディレクトリ
        export_format (str): 'bib', 'csv', または 'both'
    """
    want_bib = export_format in ('bib', 'both')
    want_csv = export_format in ('csv', 'both')

    if want_bib:
        bib_path = os.path.join(download_dir, "metadata.bib")
        with open(bib_path, 'w', encoding='utf-8') as f:
            for paper in papers:
                arxiv_id = _get_arxiv_id(paper)
                key = _make_bibtex_key(paper, arxiv_id)
                authors = ' and '.join(a.name for a in paper.authors)
                # バージョン情報を除いた純粋なID（eprint用）
                eprint = arxiv_id.split('v')[0] if 'v' in arxiv_id else arxiv_id
                year = paper.published.year if paper.published else ""

                f.write(f"@article{{{key},\n")
                f.write(f"  title = {{{_escape_bibtex(paper.title)}}},\n")
                f.write(f"  author = {{{_escape_bibtex(authors)}}},\n")
                f.write(f"  year = {{{year}}},\n")
                f.write(f"  eprint = {{{eprint}}},\n")
                f.write(f"  archivePrefix = {{arXiv}},\n")
                if paper.primary_category:
                    f.write(f"  primaryClass = {{{paper.primary_category}}},\n")
                if paper.doi:
                    f.write(f"  doi = {{{_escape_bibtex(paper.doi)}}},\n")
                if paper.journal_ref:
                    f.write(f"  journal = {{{_escape_bibtex(paper.journal_ref)}}},\n")
                f.write(f"  url = {{{paper.entry_id}}}\n")
                f.write("}\n\n")
        print(f"BibTeXメタデータを出力しました: {bib_path}")

    if want_csv:
        csv_path = os.path.join(download_dir, "metadata.csv")
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'arxiv_id', 'title', 'authors', 'published', 'doi',
                'categories', 'pdf_url', 'abstract'
            ])
            for paper in papers:
                arxiv_id = _get_arxiv_id(paper)
                authors = '; '.join(a.name for a in paper.authors)
                published = paper.published.strftime('%Y-%m-%d') if paper.published else ""
                categories = '; '.join(paper.categories) if paper.categories else ""
                # 要約内の改行をスペースに変換（CSVの可読性のため）
                abstract = ' '.join(paper.summary.split()) if paper.summary else ""
                writer.writerow([
                    arxiv_id, paper.title, authors, published, paper.doi or "",
                    categories, paper.pdf_url, abstract
                ])
        print(f"CSVメタデータを出力しました: {csv_path}")

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
        default=1000,
        help='取得する最大論文数（デフォルト: 1000）'
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
    parser.add_argument(
        '--date-from',
        help='この日付以降に投稿された論文を検索（YYYYMM形式、例：202410）'
    )
    parser.add_argument(
        '--date-to',
        help='この日付以前に投稿された論文を検索（YYYYMM形式、例：202503）'
    )
    parser.add_argument(
        '--export',
        choices=['bib', 'csv', 'both'],
        help='書誌情報を出力する形式（bib: BibTeX, csv: CSV, both: 両方）。'
             'ZoteroやMendeleyなどの文献管理ソフトに取り込めます。'
    )

    # 引数を解析
    args = parser.parse_args()
    
    # キーワードを取得
    keywords = args.keywords
    
    # ダウンロードディレクトリを確認
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dl")
    os.makedirs(download_dir, exist_ok=True)
    
    # arXivを検索
    papers = search_arxiv(
        keywords,
        args.max_results,
        args.use_or,
        args.date_from,
        args.date_to
    )
    
    if not papers:
        print("論文が見つかりませんでした。")
        sys.exit(0)
    
    # 論文情報を表示
    print("\n検索結果:")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title} ({paper.published.year})")

    # 書誌情報をエクスポート（指定された場合）
    # PDFのダウンロード成否に関わらず、検索できた全件を対象に出力する
    if args.export:
        print("\n書誌情報をエクスポート中...")
        export_metadata(papers, download_dir, args.export)

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
