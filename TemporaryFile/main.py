import plotly.offline as py_offline
import plotly.graph_objects as go
fig = go.Figure(data=[
    go.Bar(name='小明', x=["语文","数学","英语"], y=[120, 104, 93]),
    go.Bar(name='小红', x=["语文","数学","英语"], y=[101, 88, 109])
])

# 柱状图模式需要设置：4选1
fig.update_layout(barmode='group')  # ['stack', 'group', 'overlay', 'relative']
py_offline.plot(fig, filename='test')
fig.show()
