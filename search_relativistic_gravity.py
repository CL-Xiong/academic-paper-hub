#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
搜索"相对论重力位差测量"相关论文
Searching for "relativistic gravitational potential difference measurement" papers
"""

from core.retriever import PaperRetriever
import json
from datetime import datetime


def search_relativistic_gravity():
    """执行相对论重力位差测量相关论文的多源搜索"""
    
    print("\n" + "="*80)
    print("🔬 搜索主题：相对论重力位差测量")
    print("   Topic: Relativistic Gravitational Potential Difference Measurement")
    print("="*80)
    print(f"⏰ 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    retriever = PaperRetriever()
    
    # ===== 搜索策略 =====
    search_keywords = [
        ("相对论重力位差", "cnki", 100),           # 中文关键词 - 知网
        ("relativistic gravity measurement", "arxiv", 100),  # 英文关键词 - arXiv
        ("gravitational potential difference", "arxiv", 100),  # 英文关键词 - arXiv
        ("relativistic geodesy", "arxiv", 50),     # 相对论大地测量 - arXiv
        ("重力位差测量", "cnki", 50),              # 中文关键词 - 知网
    ]
    
    all_results = {
        'arxiv': [],
        'cnki': [],
        'search_summary': []
    }
    
    print("=" * 80)
    print("📝 开始多关键词、多源搜索...\n")
    
    for keyword, source, limit in search_keywords:
        try:
            print(f"🔍 搜索: '{keyword}' | 来源: {source.upper()} | 限制: {limit}")
            
            papers = retriever.search(
                keyword=keyword,
                source=source,
                limit=limit
            )
            
            print(f"   ✅ 找到 {len(papers)} 篇论文\n")
            
            if papers:
                all_results[source].extend(papers)
                all_results['search_summary'].append({
                    'keyword': keyword,
                    'source': source,
                    'count': len(papers),
                    'timestamp': datetime.now().isoformat()
                })
        
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}\n")
    
    # ===== 统计结果 =====
    print("=" * 80)
    print("📊 搜索结果统计\n")
    
    arxiv_count = len(all_results['arxiv'])
    cnki_count = len(all_results['cnki'])
    total_count = arxiv_count + cnki_count
    
    print(f"📄 arXiv 论文: {arxiv_count} 篇")
    print(f"📄 知网 论文:  {cnki_count} 篇")
    print(f"📄 总计:      {total_count} 篇\n")
    
    # ===== 显示 arXiv 结果 =====
    if all_results['arxiv']:
        print("=" * 80)
        print("🌍 arXiv 国际论文 (前15篇)\n")
        
        for i, paper in enumerate(all_results['arxiv'][:15], 1):
            title = paper.get('title', 'N/A')
            authors = paper.get('authors', [])
            if isinstance(authors, str):
                authors = json.loads(authors)
            author_str = authors[0] if authors else 'Unknown'
            
            pub_date = paper.get('publication_date', 'N/A')
            doi = paper.get('doi', 'N/A')
            
            print(f"{i}. {title}")
            print(f"   👤 {author_str}")
            print(f"   📅 {pub_date} | DOI: {doi}")
            print(f"   🔗 {paper.get('url', 'N/A')[:80]}")
            print()
    
    # ===== 显示 CNKI 结果 =====
    if all_results['cnki']:
        print("=" * 80)
        print("🇨🇳 知网中文论文 (前15篇)\n")
        
        for i, paper in enumerate(all_results['cnki'][:15], 1):
            title = paper.get('title', 'N/A')
            authors = paper.get('authors', [])
            if isinstance(authors, str):
                authors = json.loads(authors)
            author_str = ', '.join(authors[:2]) if authors else 'Unknown'
            
            pub_date = paper.get('publication_date', 'N/A')
            journal = paper.get('journal', 'N/A')
            
            print(f"{i}. {title}")
            print(f"   👤 {author_str}")
            print(f"   📅 {pub_date} | 期刊: {journal}")
            print()
    
    # ===== 保存搜索结果 =====
    print("=" * 80)
    print("💾 保存搜索结果\n")
    
    results_file = "search_results_relativistic_gravity.json"
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 搜索结果已保存到: {results_file}")
        print(f"   • arXiv 论文: {arxiv_count} 篇")
        print(f"   • 知网论文: {cnki_count} 篇")
        print(f"   • 总计: {total_count} 篇\n")
    
    except Exception as e:
        print(f"❌ 保存失败: {e}\n")
    
    # ===== 显示本地库统计 =====
    print("=" * 80)
    print("📚 本地论文库统计\n")
    
    try:
        retriever.show_library_stats()
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}\n")
    
    # ===== 输出建议 =====
    print("=" * 80)
    print("💡 下一步建议\n")
    print("1️⃣  查看详细结果:")
    print("   • 搜索结果已保存在 search_results_relativistic_gravity.json")
    print()
    print("2️⃣  查看本地论文库:")
    print("   python cli.py list")
    print("   python cli.py stats")
    print()
    print("3️⃣  获取论文详情:")
    print("   python cli.py info <paper_id>")
    print()
    print("4️⃣  批量下载论文:")
    print("   • 修改 examples.py 中的下载函数")
    print("   • 运行: python examples.py")
    print()
    print("=" * 80 + "\n")
    
    return all_results


if __name__ == '__main__':
    results = search_relativistic_gravity()
