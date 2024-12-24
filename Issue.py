
import requests
import random
from collections import defaultdict
import re

# GitHub API 基础 URL
GITHUB_API_URL = "https://api.github.com"

# 目标仓库：此处以 "redis/redis" 为例
repo_owner = "redis"
repo_name = "redis"

# GitHub 访问令牌列表
token_lst = [
    # 你可以添加更多的 token''

]

# 功能: 随机选择一个 GitHub API 令牌并返回带有认证信息的请求头（headers）。此函数允许绕过 GitHub API 请求的限制，因为 GitHub 对于每个 IP 地址的请求数量有限制，可以通过多个令牌进行轮换
# 返回一个字典，其中包含用于 GitHub API 请求的请求头 Authorization 和 Accept
def get_headers():
    access_token = random.choice(token_lst)
    return {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

# 获取仓库的所有 Issue，并按创建时间降序排序
#功能: 获取指定页面的仓库 Issues。支持分页请求，最多每次返回 100 条 Issue
# 参数:
# page: 当前请求的页面编号，用于分页请求 GitHub API
# 返回值:
# 返回一个包含 Issues 的列表（字典格式），如果请求成功；如果请求失败，返回空列表
def get_issues(page):
    # 修改 URL，采用新的格式
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=all&per_page=100&page={page}'
    headers = get_headers()
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching issues: {response.status_code}")
        return []

# 获取 Issue 的评论
# 功能: 获取指定 Issue 的评论。一次最多请求 100 条评论
# 参数:
# issue_number: 需要获取评论的 Issue 的编号
# 返回值:
# 返回包含评论的列表，每个评论是一个字典。如果请求失败，返回空列表
def get_comments(issue_number):
    url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
    params = {"page": 1, "per_page": 100}  # 获取最多 100 个评论
    headers = get_headers()
    response = requests.get(url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching comments for issue {issue_number}: {response.status_code}")
        return []
# 获取仓库的所有 Issues 和评论，只进行一次请求
# 功能: 获取所有 Issue 及其评论。采用分页获取所有 Issue，并为每个 Issue 获取评论数据
# 返回值:
# 返回一个包含所有 Issue 和评论数据的列表，每个 Issue 都会包含相关的评论数据（通过 comments_data 键）
def get_all_issues_and_comments():
    issues = []
    page = 1
    issue_count = 0  # 用于记录总 Issue 数量
    while True:
        # 获取当前页的 Issues
        page_issues = get_issues(page)
        if not page_issues:  # 如果没有更多 Issues，停止循环
            break

        # 过滤掉 Pull Requests，只保留真正的 Issues
        filtered_issues = [issue for issue in page_issues if 'pull_request' not in issue]

        issues.extend(filtered_issues)

        # 输出当前页的 Issue 标题
        for issue in filtered_issues:
            issue_count += 1
            print(f"Issue #{issue_count}: {issue['title']} (Author: {issue['user']['login']})")

            # 获取当前 Issue 的评论
            comments = get_comments(issue['number'])
            issue['comments_data'] = comments  # 将评论数据添加到 Issue 中

            # 输出每条评论的信息
            for comment_idx, comment in enumerate(comments, start=1):
                print(f"    Comment #{comment_idx}: {comment['user']['login']} - {comment['body'][:50]}...")

        page += 1

    return issues

# 获取提问者的统计分析：统计每个人的提问数和参与讨论的问题数
def get_contributor_count(issues):
    contributor_stats = defaultdict(lambda: {"ask_num": 0, "discuss_num": 0})

    # 遍历所有 Issues
    for idx, issue in enumerate(issues, start=1):
        # 显示问题的序号和标题
        print(f"Processing Issue {idx}: {issue['title']}")

        creator = issue["user"]["login"]  # 提问者即为问题的创建者
        contributor_stats[creator]["ask_num"] += 1

        # 获取评论者列表
        comments = issue['comments_data']
        for comment in comments:
            commenter = comment["user"]["login"]
            if commenter != creator:  # 排除提问者本身
                contributor_stats[commenter]["discuss_num"] += 1

    # 返回按字典排序的列表
    contributor_count = [{"name": name, "ask_num": stats["ask_num"], "discuss_num": stats["discuss_num"]}
                         for name, stats in contributor_stats.items()]

    return contributor_count

# 获取人之间的关系：分析用户之间的互动关系
def get_relation(issues):
    relations = defaultdict(int)

    # 获取每个 Issue 中评论者之间的互动
    for issue in issues:
        creator = issue["user"]["login"]  # 获取问题的发起者
        commenters = set([creator])  # 使用集合确保每个评论者只计算一次
        interacted = set()  # 用来追踪每个问题中发起者与评论者之间的互动是否已经计数过

        # 获取评论者列表
        comments = issue['comments_data']
        for comment in comments:
            commenter = comment["user"]["login"]
            commenters.add(commenter)  # 将评论者加入集合

        # 建立关系（用户之间的互动），并确保每个互动仅计算一次
        for commenter in commenters:
            if commenter != creator:  # 排除提问者本身
                user1, user2 = sorted([creator, commenter])  # 确保对称互动不会重复计算
                if (user1, user2) not in interacted:
                    relations[(user1, user2)] += 1  # 增加互动次数
                    interacted.add((user1, user2))  # 记录这对用户已经互动过

    # 转换为字典列表格式
    relation_data = [{"source": user1, "target": user2, "num": num}
                     for (user1, user2), num in relations.items()]

    return relation_data

# 获取所有 Issue 和评论数据（一次性请求）
issues = get_all_issues_and_comments()

# 获取提问者的统计数据
contributor_data = get_contributor_count(issues)

# 获取关系数据
relation_data = get_relation(issues)

# 将数据输出到指定路径
file_path = r"C:\Users\lenovo\Desktop\开源软件基础\data.txt"  # 使用原始字符串来处理路径
with open(file_path, "w") as file:
    # 写入 Contributor Data
    file.write("Contributor Data:\n")
    for contributor in contributor_data:
        file.write(
            f"name: {contributor['name']}, ask_num: {contributor['ask_num']}, discuss_num: {contributor['discuss_num']}\n")

    # 写入 Relation Data
    file.write("\nRelation Data:\n")
    for relation in relation_data:
        file.write(
            f"source: {relation['source']}, target: {relation['target']}, num: {relation['num']}\n")

print(f"Data has been written to {file_path}")
