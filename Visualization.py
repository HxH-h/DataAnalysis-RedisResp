#  数据可视化
import webbrowser
import pyecharts.options as opts
from pyecharts.charts import Line, Bar, Page, PictorialBar, Grid, Graph, Pie
from pyecharts.commons.utils import JsCode
from Commit_num import *
from Commit_contributor import *
from Issue import *

# 获取unstable分支下的提交数
unstable = request_branch_commit('unstable')
# 获取所有分支下的提交数
branch = request_branch_commit_num()

# 数据预处理
unstable_ret = get_all_commit_num(unstable)
branch_ret = get_branch_commit_num(branch)

# 获取unstable分支下的每月的提交数
# 绘制折线图
ustable_line = (
    Line(init_opts=opts.InitOpts(width="1500px"))
    .add_xaxis(list(unstable_ret.keys()))
    .add_yaxis("unstable",
               list(unstable_ret.values()),
               markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")])
               )
    .set_global_opts(
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts={"interval": "1", "rotate": 90}
        ),
        title_opts=opts.TitleOpts(title="unstable分支每月的提交数",
                                  title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
                                  pos_left="center",
                                  )
    )
)


contributors = get_commit_info(unstable, 0)
new_increase = get_monthly_new_contributors(contributors)

# 每年新增贡献者
unstable_new_line = (
    Line()
    .add_xaxis([str(item[0]) for item in new_increase])
    .add_yaxis("unstable",
               [item[1] for item in new_increase]
               )
    .set_global_opts(
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts={"interval": "0"}
        ),
        title_opts=opts.TitleOpts(title="unstable分支每年贡献者数",
                                  title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
                                  pos_left="center",
                                  )
    )
)
# 获取每个分支的总提交数
# 绘制柱状图
# 绘制柱状图
names = [item['name'] for item in branch_ret]

authored_dates = [item['authoredDate'] for item in branch_ret]

# 创建柱状图
branch_bar = (
    Bar(init_opts=opts.InitOpts(width="1200px", height="2000px"))
    .add_xaxis(names)
    .add_yaxis(
        "提交数",
        branch_ret,  # 包含 value 和 authoredDate
        bar_width="5",
        category_gap="30%",
        yaxis_index=0
    )
    .reversal_axis()
    .set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=True,
            position="right",
            formatter=JsCode(
                "function(x){return x.data.value + '    最近提交日期: ' + x.data.authoredDate;}"
            )
        )
    )
    .set_global_opts(
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts={"interval": "0"},
        ),
        title_opts=opts.TitleOpts(
            title="所有分支总提交数",
            title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
            pos_left="center",
        )
    )
)

commit_info = get_commit_info(unstable)

names = [item['name'] for item in commit_info]
values = [item['value'] for item in commit_info]
data_pair = [list(z) for z in zip(names, values)]
data_pair.sort(key=lambda x: x[1])

durations = get_duration_intervals(contributors)

pie = (Pie(init_opts=opts.InitOpts(width="1200px"))
.add("", data_pair=data_pair, center=["25%", "50%"], )
.add("", data_pair=[list(z) for z in zip(list(durations.keys()), list(durations.values()))], center=["75%", "50%"])
.set_global_opts(
    title_opts=opts.TitleOpts(title="unstable分支提交占比和关注时间占比",
                              title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
                              pos_left="center"
                              ),
    legend_opts=opts.LegendOpts(is_show=False),
)
.set_series_opts(
    tooltip_opts=opts.TooltipOpts(
        trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"
    )
)

)

max_commit = get_max_commit_monthly(unstable)

yearly_max = (
    Bar()
    .add_xaxis([item['year'] for item in max_commit])
    .add_yaxis(
        "提交数",
        max_commit,
        bar_width="5",
        category_gap="30%",
        yaxis_index=0
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=True,
            position="top",
            formatter=JsCode(
                "function(x){return x.data.name + '\\n' + x.data.value;}"
            )
        )
    )
    .set_global_opts(
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts={"interval": "0"},
        ),
        title_opts=opts.TitleOpts(
            title="每年提交数最多",
            title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
            pos_left="center",
        )
    )

)


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
            title_opts=opts.TitleOpts(title=title,
                                      title_textstyle_opts=opts.TextStyleOpts(font_family='Kaiti'),
                                      pos_left="center"
                                      ),
            xaxis_opts=opts.AxisOpts(name=x_axis_label, axislabel_opts={"interval": "0"}, ),
            yaxis_opts=opts.AxisOpts(name=y_axis_label)
        )
    )
    return bar

ask_num_max = get_ask_num_max()
diss_num_max = get_discuss_num_max()

# 创建 ask_num 柱状图
ask_bar = create_bar_chart(ask_num_max, "", "", "提问数")

# 创建 discuss_num 柱状图
discuss_bar = create_bar_chart(diss_num_max, "", "", "讨论数")

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

# 同时渲染多个图表
(
    Page(layout=Page.SimplePageLayout)
    .add(
        branch_bar,
        ustable_line,
        unstable_new_line,
        pie,
        yearly_max,
        grid,
    )
    .render("visualization.html")
)

# 自动打开渲染好的html文件
webbrowser.open("visualization.html")
webbrowser.open("relation.html")
