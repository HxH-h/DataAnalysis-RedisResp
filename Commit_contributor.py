# 历史提交贡献者的统计
from Commit_num import request_branch_commit
from datetime import datetime
from collections import defaultdict

# 获取每个人的提交数 第一次提交和最近一次提交时间 返回字典列表
# 获取unstable分支每个人的贡献数
def get_commit_info(data , threshold = 25) -> list:
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

    # 设置合并阈值
    threshold = threshold

    # 合并较少的作者到 Others
    others_commit_count = 0
    contributors = []

    for author, info in author_info.items():
        if info['commit_count'] >= threshold and author is not None:
            contributors.append({
                'name': author,
                'value': info['commit_count'],
                'first_time': info['first_time'],
                'last_time': info['last_time']
            })
        elif author is not None:
            others_commit_count += info['commit_count']

    # 如果有 Others，添加到贡献者列表
    if others_commit_count > 0:
        contributors.append({
            'name': 'Others',
            'value': others_commit_count
        })

    return contributors


# 获取每个月提交数最多的人 返回字典列表
def get_max_commit_monthly(data) -> list:
    # 使用defaultdict来存储每个月每个作者的提交数
    yearly_contributions = defaultdict(lambda: defaultdict(int))

    # 遍历数据
    for entry in data:
        date = datetime.strptime(entry['date'], '%b %d, %Y')
        year = date.strftime('%Y')
        for author in entry['authors']:
            yearly_contributions[year][author] += 1

    # 找出每个月提交数最多的人
    yearly_top_contributors = []

    for year, authors in yearly_contributions.items():
        top_contributor = max(authors, key=authors.get)
        yearly_top_contributors.append({
            'year': year,
            'name': top_contributor,
            'value': authors[top_contributor]
        })

    return yearly_top_contributors


# 获取每个贡献者跟踪该分支的占比
def get_duration_intervals(contributors):
    intervals = {
        '0-30': 0,
        '31-90': 0,
        '91-180': 0,
        '181-365': 0,
        '366+': 0
    }

    def calculate_durations(contributors):
        for contributor in contributors:
            contributor['duration'] = (contributor['last_time'] - contributor['first_time']).days
        return contributors

    for contributor in calculate_durations(contributors):
        duration = contributor['duration']
        if duration <= 30:
            intervals['0-30'] += 1
        elif 31 <= duration <= 90:
            intervals['31-90'] += 1
        elif 91 <= duration <= 180:
            intervals['91-180'] += 1
        elif 181 <= duration <= 365:
            intervals['181-365'] += 1
        else:
            intervals['366+'] += 1
    print(intervals)
    return intervals


# 每月净增长人数
def get_monthly_new_contributors(contributors):
    annual_contributors = defaultdict(int)
    previous_year_contributors = defaultdict(int)

    for contributor in contributors:
        if contributor['first_time'] is not None:
            year = contributor['first_time'].year
            annual_contributors[year] += 1

    # 计算每个年份的贡献者人数
    sorted_years = sorted(annual_contributors.keys())
    for i, year in enumerate(sorted_years):
        if i > 0:
            annual_contributors[year] += annual_contributors[sorted_years[i - 1]]
        previous_year_contributors[year] = annual_contributors[year]

    # 将 defaultdict 转换为排序后的列表
    sorted_annual_contributors = sorted(previous_year_contributors.items())
    return sorted_annual_contributors

