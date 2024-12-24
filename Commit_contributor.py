# 历史提交贡献者的统计
from datetime import datetime
from Commit_num import request_branch_commit
from collections import defaultdict

# 获取每个人的提交数 第一次提交和最近一次提交时间 返回字典列表
def get_commit_info(data) -> list:
    data = request_branch_commit('unstable')
    # 使用defaultdict来存储每个作者的信息
    author_info = defaultdict(lambda: {'commit_count': 0, 'first_time': None, 'last_time': None})

    # 遍历数据
    for entry in data:
        date = datetime.strptime(entry['date'], '%b %d, %Y')
        for author in entry['authors']:
            author_info[author]['commit_count'] += 1
            if author_info[author]['first_time'] is None or date < author_info[author]['first_time']:
                author_info[author]['first_time'] = date
            if author_info[author]['last_time'] is None or date > author_info[author]['last_time']:
                author_info[author]['last_time'] = date

    # 创建字典列表
    contributors = [
        {
            'name': author,
            'commit_count': info['commit_count'],
            'first_time': info['first_time'].strftime('%b %d, %Y'),
            'last_time': info['last_time'].strftime('%b %d, %Y')
        }
        for author, info in author_info.items()
    ]
    return contributors


# 获取每个月提交数最多的人 返回字典列表
def get_max_commit_monthly(data) -> list:
    # 使用defaultdict来存储每个月每个作者的提交数
    monthly_contributions = defaultdict(lambda: defaultdict(int))

    # 遍历数据
    for entry in data:
        date = datetime.strptime(entry['date'], '%b %d, %Y')
        month_year = date.strftime('%b %Y')
        for author in entry['authors']:
            monthly_contributions[month_year][author] += 1

    # 找出每个月提交数最多的人
    monthly_top_contributors = []

    for month_year, authors in monthly_contributions.items():
        top_contributor = max(authors, key=authors.get)
        monthly_top_contributors.append({
            'month': month_year,
            'name': top_contributor,
            'commit_count': authors[top_contributor]
        })

    return monthly_top_contributors

