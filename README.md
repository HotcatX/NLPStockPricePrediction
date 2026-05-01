
## 项目名称

股票新闻 NLP 与行情关联分析系统

## 项目目标

本项目围绕股票市场中的文本新闻与价格波动之间的关系，设计并实现一个端到端的数据管理与分析系统。系统同时满足课程对以下能力的要求：

- 使用外部 API 获取真实数据
- 使用 SQL 数据库存储结构化结果
- 使用 NoSQL 数据库存储原始半结构化数据
- 使用 Spark 处理大体量数据
- 使用 Python 完成 ETL、分析与展示

本项目当前采用“真实小批量在线数据 + 本地大规模基准数据”的混合方案：

- 在线部分使用 Alpha Vantage 获取真实股票行情与新闻数据
- 大数据部分使用本地生成并落盘的 1GB 以上股票历史数据集，通过 Spark 完成读取与聚合分析

这样做的原因是免费新闻 API 存在调用额度限制，而课程要求又需要展示大规模数据处理能力，因此项目将“真实数据接入能力”和“可扩展大数据处理能力”拆开验证。

## 与课程要求的对应关系

| 课程要求 | 本项目实现 |
| --- | --- |
| 1 个 API | Alpha Vantage 股票行情与新闻 API |
| 1 个 SQL 数据库 | Amazon Aurora MySQL |
| 1 个 NoSQL 数据库 | Amazon DynamoDB |
| 1 个大数据工具 | PySpark |
| Python 端到端实现 | `Project_Analysis.ipynb` |
| 数据集至少 1GB | 本地大文件 `massive_mock_dataset_500MB.csv`，当前实际体量约 1.5GB |

## 当前项目结构

- `Project_Analysis.ipynb`
  当前正式提交版 Notebook。包含数据获取、ETL、数据库写入、Spark 大文件读取、新闻 NLP 分析、结果展示与 requirement check。
- `create_nb.py`
  用于生成和维护 Notebook 内容的脚本。
- `generate_big_data.py`
  用于生成课程要求所需的大体量股票数据文件。
- `populate_bulk.py`
  用于批量写入或构造测试数据的辅助脚本。
- `requirements.txt`
  Notebook 和数据管线运行依赖。

## 数据源设计

### 1. 实时数据源

- Alpha Vantage `TIME_SERIES_DAILY`
  用于获取股票日级价格数据
- Alpha Vantage `NEWS_SENTIMENT`
  用于获取股票相关新闻、标题、摘要、发布时间与情绪标签

### 2. 大规模数据源

- 本地大文件 `massive_mock_dataset_500MB.csv`
  - 当前实际大小已超过 1GB
  - 用于满足课程中对大数据处理、Spark 读取、聚合与扩展性分析的要求
  - 数据字段覆盖 ticker、date、open、high、low、close、volume、headline、summary 等分析所需列

### 3. 降级与缓存策略

- 如果 Alpha Vantage 新闻接口因为免费额度限制无法返回足够数据，Notebook 会优先保留已拉取到的真实新闻结果
- 必要时可以回退到本地缓存新闻样本，保证 NLP 与数据库流程仍可演示

## 系统架构

### API 层

- Alpha Vantage 提供行情与新闻数据

### NoSQL 层

- DynamoDB 保存原始 API 返回结果
- 适合存放 JSON、嵌套字段和后续追溯所需的 raw payload

### SQL 层

- Aurora MySQL 保存结构化后的价格表与新闻表
- 便于后续查询、统计、联表和 API / 前端展示

### 大数据处理层

- PySpark 读取 1GB 以上大文件
- 对大量 ticker 的历史价格与文本字段进行分布式聚合和抽样 NLP 分析

### 分析层

- pandas 用于中小规模数据清洗与展示
- 基于关键词、标题、摘要和情绪字段完成初步 NLP 分析

## 当前 ETL Pipeline

本项目的实际处理流程如下：

1. 使用 Alpha Vantage 拉取目标股票的最新行情数据和相关新闻数据
2. 将原始响应写入 DynamoDB，保留原始 JSON 结构
3. 使用 pandas 将价格数据与新闻数据标准化为 DataFrame
4. 从 AWS Secrets Manager 读取 Aurora 凭证，并将清洗后的结构化数据写入 Aurora MySQL
5. 从 Aurora 回读样本数据，验证写入和查询是否成功
6. 使用 Spark 读取本地 1GB 以上股票大文件
7. 对大文件执行行数统计、ticker 数量统计、价格聚合、交易量聚合、文本字段抽样分析
8. 对新闻标题和摘要做初步 NLP 处理，输出关键词和情绪分布结果

## 当前 Notebook 已完成的验证

根据目前已经执行成功的 `Project_Analysis.ipynb`，以下链路已被验证：

- Alpha Vantage 行情接口可正常拉取实时数据
- Alpha Vantage 新闻接口可正常拉取新闻样本
- DynamoDB 可成功写入并读回原始数据
- Aurora MySQL 可成功写入并读回结构化价格表和新闻表
- Spark 可成功读取约 1.5GB 的本地大文件
- Spark 已完成对约 250 万行、500 个 ticker 的统计与聚合分析
- Notebook 最后已加入 requirement check，用于直接映射课程交付要求

## NLP 分析内容

当前 Notebook 中的 NLP 处理属于“初步可演示版本”，主要包括：

- 新闻标题与摘要清洗
- 高频关键词统计
- 基于接口返回字段的情绪标签整理
- 文本样本在 Spark 中的分词与词频展示

后续如果继续增强，可以加入：

- 更系统的情绪打分
- 新闻发布日期与股价波动窗口对齐
- ticker 级别的事件驱动分析
- 主题建模或 embedding 相似度分析

## 为什么采用混合数据策略

单纯依赖免费新闻 API 存在两个现实问题：

- 每日请求额度有限，难以支撑稳定的大规模实验
- 实时可拉取的数据量通常不足以直接满足“1GB 以上大数据处理”要求

因此本项目将问题拆分为两部分：

- 用真实 API 证明系统具备真实数据接入与在线 ETL 能力
- 用本地大文件证明系统具备 Spark 大数据处理能力

这比单纯伪造一套全离线流程更符合课程对“工程设计 + 可运行实现 + 可扩展性说明”的要求。

## 运行方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备环境变量

需要在本地 `.env` 或云环境中配置：

- Alpha Vantage API Key
- AWS Access Key / Secret Key
- AWS Region
- DynamoDB 表名
- Secrets Manager 中 Aurora 凭证对应的 secret name

### 3. 运行 Notebook

直接打开并执行：

```bash
Project_Analysis.ipynb
```

Notebook 会按顺序完成：

- API 数据拉取
- DynamoDB 写入与读取
- Aurora 写入与读取
- Spark 大文件读取与分析
- 新闻 NLP 初步分析

## 提交建议

课程提交时建议包含以下内容：

- `Project_Analysis.ipynb`
- 最终演示 PPT
- 本 README

如果 GitHub 仓库不适合直接提交超大 CSV 文件，建议：

- 在 README 中说明大文件生成方式
- 保留 `generate_big_data.py`
- 或将大文件放入 S3 / 云存储，仅在 Notebook 中读取路径

## 结论

当前项目已经形成一个完整的课程期末项目雏形，并且覆盖了课程要求中的关键技术栈：

- API：Alpha Vantage
- SQL：Aurora MySQL
- NoSQL：DynamoDB
- Big Data：PySpark
- Python ETL 与分析：Jupyter Notebook

下一步最值得继续增强的部分，是把新闻情绪结果与股价变化做更严格的时间对齐分析，并在最终 PPT 中明确说明数据质量、许可证、扩展性和成本权衡。
