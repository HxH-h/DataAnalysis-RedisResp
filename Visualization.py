#  数据可视化
import webbrowser
from collections import Counter
import pyecharts.options as opts
from pyecharts.charts import Line , Bar ,  Page , Grid ,Graph
from Commit_num import *
from Issue import *

#获取unstable分支下的每月的提交数
unstable_commit_num = get_all_commit_num()

# 绘制折线图
ustable_line =(
    Line(init_opts=opts.InitOpts(width="1500px"))
        .add_xaxis(list(unstable_commit_num.keys()))
        .add_yaxis("unstable",
                   list(unstable_commit_num.values()),
                   markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")])
                  )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts={"interval":"1" , "rotate":90}
            ),
            title_opts=opts.TitleOpts(title="unstable分支每月的提交数",
                                      title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
                                      pos_left="center",
                                      )
        )
)
# 获取每个分支的总提交数
branch = get_branch_commit_num()
# 绘制柱状图
branch_bar = (
    Bar(init_opts=opts.InitOpts(width="1200px" , height="2000px"))
    .add_xaxis([item['name'] for item in branch] )
    .add_yaxis("提交数", [item['num'] for item in branch],
               bar_width="5",
               category_gap="30%",
               yaxis_index = 0
               )
    .reversal_axis()
    .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts={"interval":"0"},

             ),
             title_opts=opts.TitleOpts(title="所有分支总提交数",
                                       title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
                                       pos_left="center",
                                       )
    )
)

# 获取issue的提问数和讨论数
ask_num_max = get_ask_num_max()
diss_num_max = get_discuss_num_max()


def create_bar_chart(data, title, x_axis_label, y_axis_label):
    names = [item[0] for item in data]
    values = [item[1] for item in data]
    names.reverse()
    values.reverse()
    bar = (
        Bar()
        .add_xaxis(names)
        .add_yaxis("", values)
        .reversal_axis()
        .set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=True,
            position="right",
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(name=x_axis_label , axislabel_opts={"interval": "0"},),
            yaxis_opts=opts.AxisOpts(name=y_axis_label)
        )
    )
    return bar

# 创建 ask_num 柱状图
ask_bar = create_bar_chart(ask_num_max, "", "User", "ask_num")

# 创建 discuss_num 柱状图
discuss_bar = create_bar_chart(diss_num_max, "", "User", "discuss_num")

grid = Grid(init_opts=opts.InitOpts(width="1600px", height="800px"))
grid.add(ask_bar, grid_opts=opts.GridOpts(pos_left="5%", pos_right="60%"))
grid.add(discuss_bar, grid_opts=opts.GridOpts(pos_left="60%", pos_right="5%"))

# 获取节点
nodes = extract_unique_nodes()

graph = (Graph(init_opts=opts.InitOpts(width="1600px", height='1000px'))
         .add(
    "",
    nodes,
    relation_data,
    repulsion=50,
    linestyle_opts=opts.LineStyleOpts(curve=0.2),
    label_opts=opts.LabelOpts(is_show=False),
)
         .set_global_opts(
    legend_opts=opts.LegendOpts(is_show=False),
    title_opts=opts.TitleOpts(title="issue关系图"),

).render('relation.html')

         )













#同时渲染多个图表
(
    Page(layout=Page.SimplePageLayout)
        .add(
        ustable_line,
            branch_bar,
            grid
        )
        .render("visualization.html")
)





# 自动打开渲染好的html文件
webbrowser.open("visualization.html")
webbrowser.open("relation.html")