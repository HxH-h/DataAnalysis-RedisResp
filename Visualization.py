#  数据可视化
import webbrowser
import pyecharts.options as opts
from pyecharts.charts import Line , Bar ,  Page
from Commit_num import *

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

#同时渲染多个图表
(
    Page(layout=Page.SimplePageLayout)
        .add(
            branch_bar
        )
        .render("visualization.html")
)







# 自动打开渲染好的html文件
webbrowser.open("visualization.html")
