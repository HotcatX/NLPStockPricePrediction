API：Alpha Vantage 天级数据
SQL 数据库：PostgreSQL
NoSQL 数据库：MongoDB

大数据工具：PySpark
整体 pipeline

Alpha Vantage 拉取股票新闻和行情数据。

原始 JSON 先落到 MongoDB。
清洗后的结构化数据写入 PostgreSQL。
PySpark 读取 MongoDB/PostgreSQL 数据，做批量 NLP 和聚合分析。
最后用 Flask 或 FastAPI 做一个简单展示层，展示情绪趋势、热点词、股票对比结果。