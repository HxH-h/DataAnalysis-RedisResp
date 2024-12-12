# 历史提交贡献者的统计

class Contributor:
    def __init__(self, name: str, commit_count: int , first_time: str, last_time: str):
        self.name = name
        self.commit_count = commit_count
        self.first_time = first_time
        self.last_time = last_time

# TODO 获取每个人的提交数 第一次提交和最近一次提交时间 返回Contributor类的列表
def get_commit_info() -> list:
    pass

# TODO 获取每个月提交数最多的人 返回字典
# {year-month: name} {'2024-12': 'hxh'}
def get_max_commit_monthly() -> dict:
    pass

