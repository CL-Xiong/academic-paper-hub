"""
Paper Retriever Module - Search papers from multiple sources
"""

import json
from typing import List, Dict, Optional
from pathlib import Path
from tqdm import tqdm
import logging

from .storage import StorageManager
from .downloader import PaperDownloader
from sources.arxiv_source import ArxivSource
from sources.wos_source import WebOfScienceSource
from sources.cnki_source import CNKISource


class PaperRetriever:
    """论文检索引擎"""

    def __init__(self, config_path: str = "config/settings.json"):
        """
        初始化检索引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.storage = StorageManager(self.config['storage']['base_path'])
        self.downloader = PaperDownloader(
            self.storage,
            max_workers=self.config['download']['max_workers'],
            timeout=self.config['download']['timeout'],
            retry_times=self.config['download']['retry_times']
        )
        
        # 初始化数据源
        self.sources = {}
        if self.config['sources'].get('arxiv', {}).get('enabled'):
            self.sources['arxiv'] = ArxivSource(
                timeout=self.config['sources']['arxiv'].get('timeout', 10)
            )
        
        if self.config['sources'].get('wos', {}).get('enabled'):
            self.sources['wos'] = WebOfScienceSource(
                timeout=self.config['sources']['wos'].get('timeout', 15)
            )
        
        if self.config['sources'].get('cnki', {}).get('enabled'):
            self.sources['cnki'] = CNKISource(
                timeout=self.config['sources']['cnki'].get('timeout', 10)
            )
        
        # 设置日志
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _load_config(config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def search(self, keyword: str, source: str = 'arxiv', limit: int = 50, 
               filters: Optional[Dict] = None) -> List[Dict]:
        """
        检索论文
        
        Args:
            keyword: 检索关键词
            source: 数据源 ('arxiv', 'wos', 'cnki')
            limit: 返回结果数量
            filters: 额外过滤条件
            
        Returns:
            论文列表
        """
        if source not in self.sources:
            raise ValueError(f"Source '{source}' is not enabled or not found")
        
        self.logger.info(f"Searching '{keyword}' in {source}...")
        
        try:
            papers = self.sources[source].search(keyword, limit=limit, filters=filters)
            
            # 记录检索历史
            self.storage.record_search(keyword, source, len(papers))
            
            # 为每篇论文添加元数据
            for paper in papers:
                if not paper.get('id'):
                    paper['id'] = StorageManager._generate_id(paper)
                paper['source'] = source
            
            self.logger.info(f"Found {len(papers)} papers")
            return papers
        
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []

    def batch_search(self, keyword: str, sources: List[str] = None, 
                    limit: int = 50) -> Dict[str, List[Dict]]:
        """
        多源批量检索
        
        Args:
            keyword: 检索关键词
            sources: 数据源列表，不指定则使用所有启用的源
            limit: 每个源的结果数量
            
        Returns:
            按源分组的论文字典
        """
        if sources is None:
            sources = list(self.sources.keys())
        
        results = {}
        print(f"\n🔍 Multi-source search for: '{keyword}'\n")
        
        for source in sources:
            try:
                papers = self.search(keyword, source=source, limit=limit)
                results[source] = papers
                print(f"  ✓ {source.upper()}: {len(papers)} papers found")
            except Exception as e:
                print(f"  ✗ {source.upper()}: {str(e)}")
                results[source] = []
        
        return results

    def batch_download(self, papers: List[Dict]) -> Dict:
        """
        批量下载论文
        
        Args:
            papers: 论文列表
            
        Returns:
            下载统计
        """
        # 添加论文到本地库
        for paper in papers:
            self.storage.add_paper(paper)
        
        # 批量下载
        return self.downloader.batch_download(papers)

    def show_library_stats(self):
        """显示本地库统计信息"""
        stats = self.storage.get_stats()
        
        print("\n" + "="*70)
        print("📚 Academic Paper Hub - 本地库统计")
        print("="*70)
        print(f"📄 总论文数:           {stats.get('total_papers', 0)}")
        print(f"✅ 已下载:             {stats.get('downloaded_papers', 0)}")
        print(f"📦 总大小:             {stats.get('total_size_gb', 0)} GB")
        
        if stats.get('by_source'):
            print("\n按来源统计:")
            for source, count in stats['by_source'].items():
                print(f"  - {source.upper()}: {count}")
        
        if stats.get('recent_searches'):
            print("\n最近检索:")
            for search in stats['recent_searches']:
                print(f"  - '{search['keyword']}' ({search['source']}): {search['result_count']} 结果")
        
        print("="*70 + "\n")

    def list_local_papers(self, limit: int = 20, source: str = None) -> List[Dict]:
        """列出本地论文"""
        return self.storage.list_papers(limit=limit, source=source)

    def get_paper_info(self, paper_id: str) -> Optional[Dict]:
        """获取论文详细信息"""
        return self.storage.get_paper(paper_id)
