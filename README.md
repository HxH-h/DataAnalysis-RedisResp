# DataAnalysis-RedisResp
Analysis of historical commit information and issues in the Redis repository   

### 项目介绍 

---
对Redis仓库的unstable分支的历史提交信息和issues报告进行数据分析并进行可视化，包括历史提交数量分析，贡献者分析，issues分析和提问者分析。
包含 Commit_num.py, Commit_contributor.py, Issue.py , Issue_num.py, visualization.py 文件。  
### 项目依赖

---
* python3.11 
* requests
* lxml
* pandas
* numpy
* collections
* pyecharts  
### 目录结构

---
|- README.md 项目文档  
|- Commit_num.py 历史提交数量分析，爬取Redis仓库历史提交信息，并进行预处理  
|- Commit_contributor.py 贡献者分析，对Redis仓库历史提交信息进行贡献者分析预处理  
|- Issue.py issues分析，爬取Redis仓库issues信息，分析提问者信息  
|- Issue_num.py issues数量分析，爬取Redis仓库issues信息，分析issue数量和issue的关键词  
|- visualization.py 数据可视化，对数据进行可视化，生成图表
### 使用方法
```
python Issue.py # 运行Issue.py文件 
python Issue_num.py # 运行Issue_num.py文件
python Visualization.py # 运行visualization.py文件
```
最终会在当前目录下生成
* visualization.html 包含各种分析图表
* relation.html 包含issue中的提问者关系图
