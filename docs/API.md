# Academic Paper Hub - API 文档

## 核心模块

### PaperRetriever

主控制器，负责协调检索、下载和存储操作。

#### 初始化

```python
from core.retriever import PaperRetriever

retriever = PaperRetriever(config_path="config/settings.json")
```

#### 主要方法

##### search()

在单个数据源搜索论文。

**参数：**
- `keyword` (str): 搜索关键词
- `source` (str): 数据源，选择 'arxiv', 'wos', 'cnki'
- `limit` (int): 返回结果数（默认50）
- `filters` (Dict): 可选过滤条件

**返回：** List[Dict] - 论文列表

**示例：**
```python
papers = retriever.search(
    keyword="geodesy",
    source="arxiv",
    limit=100,
    filters={'year_from': 2020}
)
```

##### batch_search()

从多个数据源搜索论文。

**参数：**
- `keyword` (str): 搜索关键词
- `sources` (List[str]): 数据源列表（默认所有启用源）
- `limit` (int): 每个源的结果数

**返回：** Dict[str, List[Dict]] - 按源分组的论文

**示例：**
```python
results = retriever.batch_search(
    keyword="GNSS",
    sources=['arxiv', 'cnki'],
    limit=50
)
```

##### batch_download()

批量下载论文。

**参数：**
- `papers` (List[Dict]): 论文列表

**返回：** Dict - 包含下载统计信息

**返回值结构：**
```python
{
    'total': 100,
    'success': 95,
    'failed': 3,
    'skipped': 2,
    'details': [...]
}
```

**示例：**
```python
papers = retriever.search("positioning", "arxiv", limit=50)
result = retriever.batch_download(papers)
print(f"下载成功: {result['success']}/{result['total']}")
```

##### list_local_papers()

列出本地存储的论文。

**参数：**
- `limit` (int): 返回数量（默认20）
- `source` (str): 按数据源过滤（可选）

**返回：** List[Dict] - 论文列表

##### get_paper_info()

获取单篇论文的详细信息。

**参数：**
- `paper_id` (str): 论文ID

**返回：** Dict or None - 论文信息

##### show_library_stats()

显示本地库的统计信息。

**参数：** 无

**返回：** 无（打印到控制台）

---

### StorageManager

管理论文的本地存储和元数据。

#### 初始化

```python
from core.storage import StorageManager

storage = StorageManager(base_path="./papers")
```

#### 主要方法

##### add_paper()

添加论文到本地库。

**参数：**
- `paper_data` (Dict): 论文数据

**返回：** bool - 成功/失败

##### get_paper()

获取论文信息。

**参数：**
- `paper_id` (str): 论文ID

**返回：** Dict or None

##### list_papers()

列出论文（带分页）。

**参数：**
- `limit` (int): 每页数量
- `offset` (int): 偏移量
- `source` (str): 过滤源

**返回：** List[Dict]

##### check_duplicate()

检查论文是否已存在。

**参数：**
- `doi` (str): DOI号（可选）
- `title` (str): 标题（可选）

**返回：** bool

##### get_stats()

获取统计信息。

**返回：** Dict
```python
{
    'total_papers': 100,
    'downloaded_papers': 85,
    'by_source': {'arxiv': 50, 'cnki': 50},
    'total_size_bytes': 5000000000,
    'total_size_gb': 4.66,
    'recent_searches': [...]
}
```

##### record_search()

记录搜索历史。

**参数：**
- `keyword` (str): 搜索词
- `source` (str): 数据源
- `result_count` (int): 结果数

---

### PaperDownloader

处理论文下载和管理。

#### 初始化

```python
from core.downloader import PaperDownloader

downloader = PaperDownloader(
    storage_manager=storage,
    max_workers=5,
    timeout=30,
    retry_times=3
)
```

#### 主要方法

##### batch_download()

批量下载论文。

**参数：**
- `papers` (List[Dict]): 论文列表
- `progress_callback` (Callable): 进度回调（可选）

**返回：** Dict - 下载统计

##### get_download_history()

获取下载历史。

**参数：**
- `limit` (int): 返回条数

**返回：** List[Dict]

---

## 数据源模块

### ArxivSource

从arXiv检索论文。

```python
from sources.arxiv_source import ArxivSource

arxiv = ArxivSource(timeout=10)

# 基本搜索
papers = arxiv.search(
    keyword="positioning",
    limit=50,
    category='physics'  # 或 'cs', 'math'
)

# 按作者搜索
papers = arxiv.search_by_author(
    author="Jane Doe",
    limit=20
)

# 获取单篇
paper = arxiv.get_paper(arxiv_id="2101.12345")
```

**支持分类：**
- `physics`: physics.geo-ph（地球物理）
- `cs`: cs.SY（计算机系统）
- `math`: math.NA（数值分析）
- `eess`: eess.SY（电气工程）

### WebOfScienceSource

Web of Science数据源（需API密钥）。

```python
from sources.wos_source import WebOfScienceSource

wos = WebOfScienceSource(timeout=15)

papers = wos.search(
    keyword="satellite navigation",
    limit=50,
    filters={'api_key': 'YOUR_KEY'}
)
```

### CNKISource

中国知网论文源。

```python
from sources.cnki_source import CNKISource

cnki = CNKISource(timeout=10)

# 基本搜索
papers = cnki.search(
    keyword="大地测量",
    limit=50
)

# 高级搜索
papers = cnki.search_advanced(
    keyword="北斗定位",
    subject="navigation",
    year_from=2020,
    year_to=2026,
    limit=100
)

# 获取全文链接
full_text_url = cnki.get_full_text(paper_id)
```

---

## 数据结构

### Paper 对象

```python
{
    'id': 'unique_hash',
    'source_id': 'source_specific_id',
    'title': '论文标题',
    'authors': ['作者1', '作者2'],
    'abstract': '摘要文本...',
    'keywords': ['关键词1', '关键词2'],
    'source': 'arxiv',  # 或 'wos', 'cnki'
    'url': 'https://...',  # 下载链接
    'doi': '10.xxxx/xxxxx',
    'publication_date': '2023-01-15',
    'categories': ['cs.SY'],  # arXiv特定
    'journal': '期刊名',  # WOS/CNKI
    'volume': '12',
    'issue': '3',
    'pages': '123-145'
}
```

### Download Result 对象

```python
{
    'total': 100,
    'success': 95,
    'failed': 3,
    'skipped': 2,
    'details': [
        {
            'paper_id': 'id',
            'title': '标题',
            'status': 'success',  # 或 'failed', 'skipped'
            'message': '成功或错误信息'
        },
        ...
    ]
}
```

---

## 错误处理

```python
try:
    papers = retriever.search(
        keyword="positioning",
        source="arxiv",
        limit=50
    )
except ValueError as e:
    print(f"源不可用: {e}")
except Exception as e:
    print(f"搜索失败: {e}")
```

## 日志

日志文件存储在 `papers/logs/`：
- `download.log` - 下载日志

配置日志级别：
```python
import logging
logging.getLogger('core.downloader').setLevel(logging.DEBUG)
```
