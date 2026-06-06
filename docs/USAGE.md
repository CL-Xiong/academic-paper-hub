# Academic Paper Hub - 使用指南

## 快速开始

### 1. 安装

```bash
git clone https://github.com/CL-Xiong/academic-paper-hub.git
cd academic-paper-hub
pip install -r requirements.txt
```

### 2. 基本用法

#### Python API 使用

```python
from core.retriever import PaperRetriever

# 初始化检索器
retriever = PaperRetriever()

# 搜索论文
papers = retriever.search(
    keyword="geodesy positioning",
    source="arxiv",  # 或 'wos', 'cnki'
    limit=50
)

# 查看结果
for paper in papers[:5]:
    print(f"标题: {paper['title']}")
    print(f"作者: {', '.join(paper['authors'])}")
    print(f"日期: {paper['publication_date']}")
    print()

# 批量下载
result = retriever.batch_download(papers)
print(f"下载成功: {result['success']}/{result['total']}")

# 查看统计信息
retriever.show_library_stats()
```

#### 命令行使用

```bash
# arXiv 搜索
python cli.py search -k "geodesy positioning" -s arxiv -l 50

# 中文论文搜索 (CNKI)
python cli.py search -k "大地测量定位" -s cnki -l 50

# 多源搜索
python cli.py multi-search -k "GNSS navigation" -l 30 -s arxiv cnki

# 查看本地论文
python cli.py list -l 20

# 查看统计信息
python cli.py stats

# 查看论文详情
python cli.py info <paper_id>
```

## 支持的数据源

### 1. arXiv
- **覆盖领域**: 物理学、计算机科学、数学等
- **相关分类**: 
  - `physics.geo-ph` - 地球物理
  - `cs.SY` - 计算机系统
  - `eess.SY` - 电气工程
- **优势**: 免费、API稳定、包含最新预印本

```python
# arXiv 高级搜索
papers = retriever.search(
    keyword="navigation systems",
    source="arxiv",
    limit=50,
    filters={
        'date_from': '2023-01-01',
        'date_to': '2024-12-31'
    }
)
```

### 2. Web of Science (WOS)
- **覆盖**: 全球学术文献的核心收录库
- **特点**: 被引次数、高质量期刊
- **注意**: 需要官方API密钥（付费订阅）

```python
# WOS 搜索（需要 API key）
papers = retriever.search(
    keyword="satellite positioning",
    source="wos",
    limit=50,
    filters={
        'api_key': 'YOUR_WOS_API_KEY',
        'year_from': 2020,
        'year_to': 2026
    }
)
```

### 3. CNKI (中国知网)
- **覆盖**: 中文学术文献（期刊、学位论文）
- **优势**: 中文资源全面、学位论文丰富
- **分类**: 支持按学科分类

```python
# CNKI 中文搜索
papers = retriever.search(
    keyword="大地测量 定位",
    source="cnki",
    limit=50,
    filters={
        'year_from': 2020,
        'year_to': 2026,
        'subject': 'geodesy'  # 或 'navigation', 'positioning'
    }
)

# 高级搜索
papers = retriever.sources['cnki'].search_advanced(
    keyword="北斗导航",
    subject="navigation",
    year_from=2021,
    year_to=2026,
    limit=100
)
```

## 功能详解

### 1. 多源搜索

一次搜索从多个数据源获取论文：

```python
results = retriever.batch_search(
    keyword="GNSS navigation",
    sources=['arxiv', 'cnki'],  # 指定源或使用所有启用的源
    limit=50
)

# 按源查看结果
for source, papers in results.items():
    print(f"{source}: {len(papers)} 篇论文")
```

### 2. 批量下载

智能下载管理：
- 自动去重（基于DOI或标题）
- 并发下载（可配置线程数）
- 自动重试（可配置重试次数）
- 进度显示

```python
# 搜索论文
papers = retriever.search(
    keyword="positioning algorithms",
    source="arxiv",
    limit=100
)

# 批量下载
result = retriever.batch_download(papers)

print(f"成功: {result['success']}")
print(f"失败: {result['failed']}")
print(f"跳过: {result['skipped']}")

# 查看下载详情
for detail in result['details']:
    print(f"{detail['title']}: {detail['status']}")
    if detail['status'] == 'failed':
        print(f"  原因: {detail['message']}")
```

### 3. 本地库管理

```python
# 列出所有论文
papers = retriever.list_local_papers(limit=50)

# 按来源过滤
arxiv_papers = retriever.list_local_papers(limit=50, source='arxiv')
cnki_papers = retriever.list_local_papers(limit=50, source='cnki')

# 获取论文详细信息
paper = retriever.get_paper_info('paper_id')
print(paper['title'])
print(paper['authors'])
print(paper['pdf_path'])  # 本地PDF路径

# 查看统计
stats = retriever.storage.get_stats()
print(f"总论文数: {stats['total_papers']}")
print(f"已下载: {stats['downloaded_papers']}")
print(f"总大小: {stats['total_size_gb']} GB")
print(f"按来源: {stats['by_source']}")
```

## 配置说明

编辑 `config/settings.json` 自定义设置：

```json
{
  "storage": {
    "base_path": "./papers",      // 论文存储目录
    "organize_by": "year",         // 按年份组织（待实现）
    "max_local_papers": 10000,     // 最大本地论文数
    "auto_cleanup": false          // 自动清理过期文件
  },
  "sources": {
    "arxiv": {
      "enabled": true,
      "timeout": 10,
      "category": "physics.geo-ph",  // 默认分类
      "max_results": 1000
    },
    "wos": {
      "enabled": true,
      "timeout": 15,
      "requires_login": true
    },
    "cnki": {
      "enabled": true,
      "timeout": 10,
      "database": "CJFQ"  // 期刊
    }
  },
  "download": {
    "max_workers": 5,      // 并发下载数
    "retry_times": 3,      // 重试次数
    "timeout": 30,         // 超时时间
    "chunk_size": 8192     // 分块大小
  }
}
```

## 目录结构

```
papers/
├── pdfs/              # 下载的PDF文件
├── metadata/          # 论文元数据（JSON）
├── logs/              # 操作日志
└── papers.db          # SQLite数据库
```

## 常见问题

### Q: 如何配置Web of Science API？
A: 需要从WOS官网申请API密钥，然后在filters中传入：
```python
retriever.search(
    keyword="...",
    source="wos",
    filters={'api_key': 'YOUR_KEY'}
)
```

### Q: CNKI能否下载全文PDF？
A: CNKI的全文下载通常需要登录或付费。此系统目前支持获取元数据和下载地址。

### Q: 如何加速下载？
A: 修改config.json中的`max_workers`（增加并发数）和调整`timeout`。

### Q: 数据库存储在哪里？
A: 在`papers/papers.db`，是一个SQLite数据库，包含所有论文元数据。

## 开发指南

添加新数据源：

1. 在 `sources/` 目录创建新文件（如 `new_source.py`）
2. 继承基类并实现 `search()` 方法
3. 在 `core/retriever.py` 中注册新源

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
