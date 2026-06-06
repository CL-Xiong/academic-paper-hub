"""
Command Line Interface for Academic Paper Hub
"""

import argparse
import sys
from pathlib import Path
import json

from core.retriever import PaperRetriever


class PaperHubCLI:
    """命令行界面"""

    def __init__(self):
        self.retriever = PaperRetriever()
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行分析器"""
        parser = argparse.ArgumentParser(
            description='Academic Paper Hub - 学术论文检索、下载一体化系统',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
例子:
  # arXiv検索
  python cli.py search -k "geodesy positioning" -s arxiv -l 20
  
  # 中文论文检索
  python cli.py search -k "大地测量" -s cnki -l 50
  
  # 多源検索
  python cli.py multi-search -k "GNSS navigation" -l 30
  
  # 下载论文
  python cli.py download -i paper_id1 paper_id2
  
  # 查看统计
  python cli.py stats
            '''
        )

        subparsers = parser.add_subparsers(dest='command', help='指令')

        # search指令
        search_parser = subparsers.add_parser('search', help='一个数据源検索')
        search_parser.add_argument('-k', '--keyword', required=True, help='検索关键词')
        search_parser.add_argument('-s', '--source', default='arxiv', 
                                 choices=['arxiv', 'wos', 'cnki'],
                                 help='数据源 (默认: arxiv)')
        search_parser.add_argument('-l', '--limit', type=int, default=50,
                                 help='返回数量 (默认: 50)')
        search_parser.add_argument('--year-from', type=int, help='年份范围起始')
        search_parser.add_argument('--year-to', type=int, help='年份范围结束')
        search_parser.add_argument('--subject', help='学科分类 (CNKI)')
        search_parser.set_defaults(func=self.cmd_search)

        # multi-search指令
        multi_search_parser = subparsers.add_parser('multi-search', help='多源検索')
        multi_search_parser.add_argument('-k', '--keyword', required=True, help='検索关键词')
        multi_search_parser.add_argument('-l', '--limit', type=int, default=50,
                                        help='每个源的结果数 (默认: 50)')
        multi_search_parser.add_argument('-s', '--sources', nargs='+',
                                        choices=['arxiv', 'wos', 'cnki'],
                                        help='数据源 (指定媒体或使用所有启用的源)')
        multi_search_parser.set_defaults(func=self.cmd_multi_search)

        # download指令
        download_parser = subparsers.add_parser('download', help='下载论文')
        download_parser.add_argument('-i', '--ids', nargs='+', required=True,
                                    help='论文IDs')
        download_parser.add_argument('-w', '--workers', type=int, default=5,
                                    help='并发下载workers数')
        download_parser.set_defaults(func=self.cmd_download)

        # list指令
        list_parser = subparsers.add_parser('list', help='列出本地论文')
        list_parser.add_argument('-l', '--limit', type=int, default=20,
                               help='返回数量 (默认: 20)')
        list_parser.add_argument('-s', '--source', help='按来源过滤')
        list_parser.set_defaults(func=self.cmd_list)

        # info指令
        info_parser = subparsers.add_parser('info', help='查看论文信息')
        info_parser.add_argument('paper_id', help='论文ID')
        info_parser.set_defaults(func=self.cmd_info)

        # stats指令
        stats_parser = subparsers.add_parser('stats', help='查看统计信息')
        stats_parser.set_defaults(func=self.cmd_stats)

        return parser

    def cmd_search(self, args):
        """执行検索指令"""
        filters = {}
        if args.year_from:
            filters['year_from'] = args.year_from
        if args.year_to:
            filters['year_to'] = args.year_to
        if args.subject:
            filters['subject'] = args.subject

        try:
            papers = self.retriever.search(
                keyword=args.keyword,
                source=args.source,
                limit=args.limit,
                filters=filters if filters else None
            )

            print(f"\n📄 Found {len(papers)} papers from {args.source.upper()}\n")
            self._print_papers(papers)

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def cmd_multi_search(self, args):
        """执行多源検索指令"""
        sources = args.sources if args.sources else ['arxiv', 'cnki']

        try:
            results = self.retriever.batch_search(
                keyword=args.keyword,
                sources=sources,
                limit=args.limit
            )

            print(f"\n" + "="*70)
            total = sum(len(papers) for papers in results.values())
            print(f"📄 Total {total} papers found across {len(results)} sources\n")

            for source, papers in results.items():
                if papers:
                    print(f"\n🔍 {source.upper()} ({len(papers)} papers):")
                    self._print_papers(papers[:10])  # 仅显示前10篇
                    if len(papers) > 10:
                        print(f"  ... and {len(papers) - 10} more")

            print("\n" + "="*70)

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def cmd_download(self, args):
        """执行下载指令"""
        print(f"\n⚠️  This command requires paper objects with URL information.")
        print(f"Please use: retriever.batch_download(papers)\n")

    def cmd_list(self, args):
        """执行列表指令"""
        try:
            papers = self.retriever.list_local_papers(
                limit=args.limit,
                source=args.source
            )

            if args.source:
                print(f"\n📄 Local papers from {args.source.upper()}:\n")
            else:
                print(f"\n📄 Local papers:\n")

            self._print_papers(papers)

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def cmd_info(self, args):
        """执行信息指令"""
        try:
            paper = self.retriever.get_paper_info(args.paper_id)

            if paper:
                print(f"\n📄 Paper Information:\n")
                print(f"Title:    {paper.get('title', 'N/A')}")
                print(f"Authors:  {', '.join(json.loads(paper.get('authors', '[]'))) if isinstance(paper.get('authors'), str) else ', '.join(paper.get('authors', []))}")
                print(f"Source:   {paper.get('source', 'N/A')}")
                print(f"Date:     {paper.get('publication_date', 'N/A')}")
                print(f"DOI:      {paper.get('doi', 'N/A')}")
                print(f"Downloaded: {'Yes' if paper.get('pdf_path') else 'No'}")
                if paper.get('pdf_path'):
                    print(f"PDF Path: {paper.get('pdf_path')}")
                print()
            else:
                print(f"❌ Paper not found")

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def cmd_stats(self, args):
        """执行统计指令"""
        try:
            self.retriever.show_library_stats()
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    @staticmethod
    def _print_papers(papers, limit=10):
        """打印论文列表"""
        for i, paper in enumerate(papers[:limit], 1):
            title = paper.get('title', 'N/A')[:70]
            authors = paper.get('authors', [])
            if isinstance(authors, str):
                authors = json.loads(authors)
            author_str = (authors[0] if authors else 'Unknown')[:30]

            print(f"{i}. {title}...")
            print(f"   👤 {author_str}")
            print(f"   📅 {paper.get('publication_date', 'N/A')} | Source: {paper.get('source', 'N/A')}")
            print()

    def run(self, args=None):
        """运行命令行接口"""
        if args is None:
            args = sys.argv[1:]

        parsed_args = self.parser.parse_args(args)

        if hasattr(parsed_args, 'func'):
            parsed_args.func(parsed_args)
        else:
            self.parser.print_help()


if __name__ == '__main__':
    cli = PaperHubCLI()
    cli.run()
