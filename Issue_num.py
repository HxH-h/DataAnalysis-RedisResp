import requests
import os
import csv
import re
import numpy as np
import pandas as pd
from collections import Counter


# GitHub Token 列表
TOKENS = [
    '替换成你的 GitHub Token',
]
TOKEN_INDEX = 0  # 当前使用的 token 索引
TOKEN_USAGE_COUNT = 0  # 当前 token 的使用次数
TOKEN_LIMIT = 2000  # 每个 token 最大使用次数


def get_headers():
    """
    获取当前 token 的 headers。每当 token 使用次数超过限制时，会切换到下一个 token。
    """
    global TOKEN_INDEX, TOKEN_USAGE_COUNT
    TOKEN_USAGE_COUNT += 1
    # 检查是否需要更换 token
    if TOKEN_USAGE_COUNT > TOKEN_LIMIT:
        TOKEN_INDEX = (TOKEN_INDEX + 1) % len(TOKENS)
        TOKEN_USAGE_COUNT = 1  # 重置计数
        print(f"Switching to token {TOKEN_INDEX + 1}")
    return {'Authorization': f'token {TOKENS[TOKEN_INDEX]}'}


def get_issues_list(repo_name):
    """
    获取指定 GitHub 仓库的所有 issue 列表，过滤掉 pull requests。
    该函数支持分页获取更多问题。
    """
    issues_list = []
    url = f'https://api.github.com/repos{repo_name}/issues?state=all&per_page=100'
    while url:
        response = requests.get(url, headers=get_headers())
        if response.status_code != 200:
            print(f"Failed to fetch issues: {response.status_code}, {response.text}")
            break
        page_source = response.json()

        # 过滤掉 pull requests
        for issue in page_source:
            if 'pull_request' in issue:
                continue
            issues_list.append(issue)

        # 获取下一页链接
        url = response.links.get('next', {}).get('url', None)

    return issues_list


def get_issue_content(comments_url):
    """
    获取指定 issue 的评论内容，并进行清洗。去除无关的统计数据、日志等内容。
    """
    response = requests.get(comments_url, headers=get_headers())
    if response.status_code != 200:
        print(f"Failed to fetch comments: {response.status_code}, {response.text}")
        return 'none'

    comments = response.json()
    if not comments:
        return 'none'  # 如果没有评论，则返回 'none'

    issue_content = []
    # 获取 issue 的正文和评论
    for comment in comments:
        body = comment.get('body', 'none')

        # 过滤掉无关的统计数据、日志等内容
        if body.startswith(('total:', 'active:', 'mapped:', 'retained:', 'base:')):
            continue

        # 其他清洗逻辑：去除数字、特殊字符等
        body = re.sub(r'\d+', '', body)  # 去除所有数字
        issue_content.append(body.strip())  # 清除多余空格

    return '\n'.join(issue_content) or 'none'  # 如果没有正文内容，则返回 'none'


def escape_for_csv(text):
    """
    对文本进行转义，确保能够正确存储到 CSV 文件中。处理逗号、换行符、双引号等特殊字符。
    """
    # 如果是字符串，进行清理
    if isinstance(text, str):
        # 过滤掉某些特殊的无关内容
        text = re.sub(r'\b(total:|active:|mapped:|retained:|base:)\b.*', '', text)  # 去除特定字段行

        # 处理文本中的双引号：CSV 格式要求双引号中的双引号要被转义
        text = text.replace('"', '""')

        # 如果文本中包含逗号或换行符，则加上引号包围
        if ',' in text or '\n' in text:
            text = f'"{text}"'

    return text


def save_content_to_file(issue_id, body_content, comments_content):
    """
    将 issue 的正文和评论内容保存到本地文件中。每个 issue 会生成一个对应的 markdown 文件。
    """

    # 创建文件路径
    md_file_path = f'./content/issues_{issue_id}.md'

    with open(md_file_path, mode='w', encoding='utf-8') as file:
        # 写入正文和评论内容
        file.write(f"# Issue {issue_id} Content\n\n")
        file.write(f"## Body\n\n{body_content}\n\n")
        file.write(f"## Comments\n\n{comments_content}\n")

    return md_file_path

def spider():
    """
    主爬虫函数，负责从 GitHub 获取 issue 数据并保存到本地 CSV 和 Markdown 文件。
    """
    result_path = r'./content'
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    # 定义 CSV 文件路径
    csv_file_path = r'./issues.csv'

    # 写入 CSV 文件的表头
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['URL', 'Created At', 'Closed At', 'Content File'])

        repo_name = '/redis/redis'  # 要爬取的仓库
        print(f"Fetching issues from {repo_name}")

        # 获取项目的 issues 列表
        issues_list = get_issues_list(repo_name)

        stopflag = 14000  # 设定爬取的最大 issue 数量
        issue_counter = 0

        # 获取每个 issue 的内容
        for issue in issues_list:
            try:
                issue_url = issue['html_url']
                created_at = issue['created_at']
                closed_at = issue.get('closed_at', 'none')

                comments_url = issue['comments_url']
                body_content = issue.get('body') or 'none'
                content = get_issue_content(comments_url)

                # 生成保存内容的文件
                issue_id = issue['id']
                md_file_path = save_content_to_file(issue_id, body_content, content)

                issue_counter += 1
                print(f"Fetching issue {issue_counter}: {issue_url}")

                # 将文件路径和其他信息写入 CSV
                writer.writerow([issue_url, created_at, closed_at, md_file_path])
                print(f"Saved issue {issue_url} to {md_file_path}")

                if issue_counter >= stopflag:
                    break
            except KeyError as e:
                print(f"KeyError: Missing field {e} in issue: {issue}")
            except Exception as e:
                print(f"Unexpected error: {e}")

    print('The end!')


# 获取每月问题的提交数和解决数。
# 返回格式：[{'date': 'year-month', 'commit_num': , 'solve_num'}]
def get_issue_num(df) -> list:
    # 创建年月字段
    df['Created YearMonth'] = df['Created At'].dt.to_period('M')
    df['Closed YearMonth'] = df['Closed At'].dt.to_period('M')

    # 获取提交数和解决数
    # 提交数按 Created YearMonth 统计
    submitted_count = df.groupby('Created YearMonth').size().reset_index(name='commit_num')
    # 解决数按 Closed YearMonth 统计（非空的 Closed At）
    resolved_count = df[df['Closed At'].notna()].groupby('Closed YearMonth').size().reset_index(name='solve_num')

    # 合并提交数和解决数
    result = pd.merge(submitted_count, resolved_count, left_on='Created YearMonth', right_on='Closed YearMonth',
                      how='outer')

    # 将结果转换为字典列表的形式
    result_list = []
    for index, row in result.iterrows():
        result_list.append({
            'date': str(row['Created YearMonth']),
            'commit_num': row['commit_num'] if pd.notna(row['commit_num']) else 0,
            'solve_num': row['solve_num'] if pd.notna(row['solve_num']) else 0
        })

    return result_list




# 获取问题提交到解决的间隔,返回两个参数:最短的5个和最长的5个
# 返回格式：[{'date': 'year-month' , 'issue_name':  ,'interval': }]
def get_issue_interval(df) -> (list, list):
    # 计算从提交到解决的时间间隔，保持以秒为单位
    df['Time to Resolve (seconds)'] = (df['Closed At'] - df['Created At']).dt.total_seconds()

    df['Time to Resolve (seconds)'] = df['Time to Resolve (seconds)'] .fillna(0)

    df['Time to Resolve (seconds)'] = df['Time to Resolve (seconds)'].astype(int)

    # 计算最长的时间间隔并转换为天数
    df['Time to Resolve (days)'] = df['Time to Resolve (seconds)'] / 86400

    # 先处理缺失值，填充为0
    df['Time to Resolve (days)'] = df['Time to Resolve (days)'].fillna(0)

    # 向下取整最长时间间隔（天数）
    df['Time to Resolve (days)'] = np.floor(df['Time to Resolve (days)']).astype(int)

    # 过滤已解决的 issue（Closed At 非空）
    resolved_issues = df[df['Closed At'].notna()]

    # 获取最短的5个间隔（秒为单位）
    shortest_5 = resolved_issues.nsmallest(5, 'Time to Resolve (seconds)')[['URL', 'Created YearMonth', 'Time to Resolve (seconds)']]
    shortest_5 = shortest_5.rename(
        columns={'URL': 'issue_name', 'Created YearMonth': 'date', 'Time to Resolve (seconds)': 'interval'})

    # 获取最长的5个间隔（天为单位，已向下取整）
    longest_5 = resolved_issues.nlargest(5, 'Time to Resolve (days)')[['URL', 'Created YearMonth', 'Time to Resolve (days)']]
    longest_5 = longest_5.rename(
        columns={'URL': 'issue_name', 'Created YearMonth': 'date', 'Time to Resolve (days)': 'interval'})

    # 将结果转换为字典列表的形式
    shortest_list = shortest_5.to_dict(orient='records')
    longest_list = longest_5.to_dict(orient='records')

    return shortest_list, longest_list


def load_stopwords(file_path='stopwords.txt'):
    """
    从文件加载停用词列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            stopwords = set(word.strip() for word in file.readlines())
        return stopwords
    except FileNotFoundError:
        print(f"Error: Stopwords file '{file_path}' not found.")
        return set()




# 获取问题提交到解决的间隔,返回两个参数:最短的5个和最长的5个
# 返回格式：[{'date': 'year-month' , 'issue_name':  ,'interval': }]
def get_issue_keyword(content_folder='content', stopwords_file='stopwords.txt', freq_threshold=10000) -> list:
    # 加载停用词
    stopwords = load_stopwords(stopwords_file)
    all_words = []

    # 遍历 content 文件夹中的所有 md 文件
    for filename in os.listdir(content_folder):
        if filename.endswith('.md'):
            file_path = os.path.join(content_folder, filename)

            # 打开并读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # 文本预处理：去掉非字母字符（包括标点符号），并转为小写
                cleaned_content = re.sub(r'[^a-zA-Z\s]', '', content).lower()

                # 将内容按空格分割成单词列表
                words = cleaned_content.split()

                # 去除停用词，并筛选长度大于2的词
                filtered_words = [word for word in words if word not in stopwords and len(word) > 2]

                # 将处理后的单词加入总单词列表
                all_words.extend(filtered_words)

    # 使用 Counter 来统计每个词的出现次数
    word_count = Counter(all_words)

    # 将结果转换为字典列表格式
    result = [(keyword, num) for keyword, num in word_count.items()]

    # 过滤掉频次过高的词
    filtered_result = [item for item in result if item[1] <= freq_threshold]

    # 按照词频（num）从高到低排序
    filtered_result = sorted(filtered_result, key=lambda x: x[1], reverse=True)

    return filtered_result


def get_result():
    # 读取 CSV 文件
    df = pd.read_csv('issues.csv')

    # 转换日期列为 datetime 类型，并考虑时区
    # 使用 pd.to_datetime() 直接解析 ISO 8601 格式时间
    df['Created At'] = pd.to_datetime(df['Created At'], errors='coerce', utc=True)
    df['Closed At'] = pd.to_datetime(df['Closed At'], errors='coerce', utc=True)

    return df













