#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage examples for Academic Paper Hub
"""

from core.retriever import PaperRetriever
import json


def example_basic_search():
    """基本検索示例"""
    print("\n=== Example 1: Basic Search ===")
    
    retriever = PaperRetriever()
    
    # arXiv検索
    papers = retriever.search(
        keyword="geodesy positioning",
        source="arxiv",
        limit=10
    )
    
    print(f"Found {len(papers)} papers from arXiv:")
    for paper in papers[:3]:
        print(f"  - {paper['title'][:60]}...")


def example_multi_source_search():
    """多源検索示例"""
    print("\n=== Example 2: Multi-Source Search ===")
    
    retriever = PaperRetriever()
    
    # 从多个源検索
    results = retriever.batch_search(
        keyword="GNSS navigation",
        sources=['arxiv', 'cnki'],
        limit=20
    )
    
    for source, papers in results.items():
        print(f"\n{source.upper()}: {len(papers)} papers found")
        for paper in papers[:2]:
            print(f"  - {paper['title'][:60]}...")


def example_advanced_search():
    """高级検索示例"""
    print("\n=== Example 3: Advanced Search (CNKI) ===")
    
    retriever = PaperRetriever()
    
    # 中文论文検索（知网）
    papers = retriever.search(
        keyword="大地测量定位",
        source="cnki",
        limit=30,
        filters={
            'year_from': 2020,
            'year_to': 2026,
            'subject': 'positioning'
        }
    )
    
    print(f"\nFound {len(papers)} papers from CNKI (2020-2026):")
    for paper in papers[:3]:
        print(f"  - {paper['title']}")
        print(f"    Authors: {', '.join(paper['authors'][:2])}")


def example_batch_download():
    """批量下载示例"""
    print("\n=== Example 4: Batch Download ===")
    
    retriever = PaperRetriever()
    
    # 先搜索
    papers = retriever.search(
        keyword="positioning algorithms",
        source="arxiv",
        limit=5
    )
    
    # 批量下载
    if papers:
        print(f"\nDownloading {len(papers)} papers...")
        result = retriever.batch_download(papers)
        
        print(f"\nDownload Summary:")
        print(f"  Total: {result['total']}")
        print(f"  Success: {result['success']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Skipped: {result['skipped']}")


def example_library_stats():
    """查看本地库统计示例"""
    print("\n=== Example 5: Library Statistics ===")
    
    retriever = PaperRetriever()
    retriever.show_library_stats()


def example_list_papers():
    """列表本地论文示例"""
    print("\n=== Example 6: List Local Papers ===")
    
    retriever = PaperRetriever()
    
    # 列出所有论文
    papers = retriever.list_local_papers(limit=5)
    print(f"\nLocal papers (first 5):")
    for paper in papers:
        print(f"  - {paper['title']}")
        print(f"    Source: {paper['source']}, Date: {paper['publication_date']}")
    
    # 按来源列表
    arxiv_papers = retriever.list_local_papers(limit=5, source='arxiv')
    print(f"\narXiv papers (first 5):")
    for paper in arxiv_papers:
        print(f"  - {paper['title']}")


def example_get_paper_info():
    """获取论文信息示例"""
    print("\n=== Example 7: Get Paper Information ===")
    
    retriever = PaperRetriever()
    
    # 先搜索一篇论文
    papers = retriever.search(
        keyword="satellite navigation",
        source="arxiv",
        limit=1
    )
    
    if papers:
        paper_id = papers[0]['id']
        paper_info = retriever.get_paper_info(paper_id)
        
        if paper_info:
            print(f"\nPaper Information:")
            print(f"  Title: {paper_info['title']}")
            print(f"  Authors: {paper_info['authors']}")
            print(f"  Source: {paper_info['source']}")
            print(f"  Date: {paper_info['publication_date']}")
            print(f"  Downloaded: {'Yes' if paper_info['pdf_path'] else 'No'}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("📚 Academic Paper Hub - Usage Examples")
    print("="*70)
    
    # 运行示例
    try:
        example_basic_search()
        example_multi_source_search()
        example_advanced_search()
        # example_batch_download()  # 取消注释应下载有效下URL的论文
        example_library_stats()
        example_list_papers()
        example_get_paper_info()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70 + "\n")
