# 历史提交数的统计
import time

import requests
from lxml import etree
import json
import pandas as pd

BRANCH_URL = 'https://github.com/redis/redis/branches/all?page='
GITHUB_URL = 'https://github.com'
COMMIT_URL = 'https://github.com/redis/redis/commits/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}

# 解析响应的HTML文件 将script下的json字符串转为字典
# @Param resp 响应文本
def parseHTML(resp: str) -> dict:
    # xpath解析数据
    tree = etree.HTML(resp)
    script = tree.xpath('//turbo-frame[@id="repo-content-turbo-frame"]//script[@type="application/json"]')
    try:
        json_data = json.loads(script[0].text)
    except Exception:
        print(resp)
    return json_data

# 字符串转数字
def getNum(num: str) -> int:
    return int(num.replace(",", ""))

# 获取仓库unstable分支的按月的提交数  返回字典
# { year-month : num}  {2024-12:200 , 2024-11:100}
def get_all_commit_num() -> dict:
    ret = request_branch_commit('unstable')
    # 提取月份
    # 将字典转换为 DataFrame
    df = pd.DataFrame(list(ret.items()), columns=['date_str', 'value'])

    # 解析日期字符串为 datetime 对象
    df['date'] = pd.to_datetime(df['date_str'], format='%b %d, %Y')

    # 提取月份
    df['month'] = pd.to_datetime(df['date'].dt.strftime('%b %Y'))

    # 按月份分组并对值求和
    summed_df = df.groupby('month')['value'].sum().reset_index().sort_values(by='month')

    return dict(zip(summed_df['month'].dt.strftime('%b %Y'), summed_df['value']))

# 获取所有的提交数 最后一次提交时间
# 返回Branch列表
def get_branch_commit_num() -> list:
    ret = []
    keys = ['name', 'path', 'authoredDate']
    # 获取所有分支名
    page = 1
    while True:
        resp = requests.get(BRANCH_URL + str(page), headers=HEADERS , verify=False)
        # 解析出对象
        json_data = parseHTML(resp.text)
        # 获取分支名 和 最近一次提交时间
        branch_list = json_data['payload']['branches']
        # 处理数据保留部分键值对
        for i in range(len(branch_list)):
            branch_list[i] = {key: branch_list[i][key] for key in keys}
        ret.extend(branch_list)
        # 判断是否还有下一页
        if not json_data['payload']['has_more']:
            break
        page += 1
        # 等待30秒
        time.sleep(0.5)
    # 获取每个分支的提交数
    for i in range(len(ret)):
        branch_url = ret[i]['path']
        resp = requests.get(GITHUB_URL + branch_url, headers=HEADERS , verify=False)
        json_data = parseHTML(resp.text)
        # 获取提交数
        ret[i]['commit_num'] = getNum(json_data['props']['initialPayload']['overview']['commitCount'])
        time.sleep(0.5)

    return ret



# 发起请求获取一个分支下的commit数据
# @Param branch 分支名
# @return 每天的提交数
def request_branch_commit(branch: str) -> dict:
    ret = {}
    base_num = 34
    # 发起第一页的请求
    resp = requests.get(url=COMMIT_URL + branch, headers=HEADERS , verify=False)

    # 转为字典
    json_data = parseHTML(resp.text)
    datas = json_data['payload']['commitGroups']
    # 获取每天的提交数
    for data in datas:
        ret[data['title']] = len(data['commits'])
    # 解析出最近一次提交的oid
    base_oid = datas[0]['commits'][0]['oid']
    # 设置分页大小
    pagination = 35
    # 其后的请求都基于base_oid + base_num + pagination
    i = 0
    while True:
        url = COMMIT_URL + branch + '/?after=' + base_oid + '+' +str(base_num + pagination * i)
        resp = requests.get(url=url, headers=HEADERS , verify=False)
        json_data = parseHTML(resp.text)
        datas = json_data['payload']['commitGroups']
        # 获取每天的提交数
        for data in datas:
            ret[data['title']] = len(data['commits'])

        if not json_data['payload']['filters']['pagination']['hasNextPage']:
            break
        print(base_num + pagination * i)
        i += 1
        time.sleep(1)
    return ret

if __name__ == '__main__':
    print(get_all_commit_num())





