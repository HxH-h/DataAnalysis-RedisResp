#  提问者的统计分析

# TODO 获取每个人的提问数和参与讨论的问题数 返回字典的列表
# [{name: , ask_num: , discuss_num: }]
def get_contributor_count() -> list:
    pass


# TODO 获取人之间的关系，一个人在另一个人的issue下发言二者即存在关系 , 返回字典的列表
# {'source': , 'target': , 'num': }
# 最终绘制的是无向图
# {'source': 'zs' , 'target': 'ls' , 'num': 1} 和 {'source': 'ls' , 'target': 'zs' , 'num': 1} 相同
#                                   ||
# 应该改为 {'source': 'zs' , 'target': 'ls' , 'num': 2}
def get_relation() -> list:
    pass