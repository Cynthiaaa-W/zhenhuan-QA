from graphviz import Digraph

# 创建流程图
dot = Digraph(comment='DeepSeek本地知识问答系统',
              graph_attr={'rankdir': 'LR', 'bgcolor': 'transparent'},
              node_attr={'style': 'filled', 'fontname': 'Microsoft YaHei'})

# 颜色方案
colors = {
    'deploy': '#FFD700',
    'process': '#87CEFA',
    'optimize': '#98FB98',
    'ui': '#FFA07A',
    'compare': '#EE82EE'
}

# 1. 模型部署阶段
dot.node('A', 'Ollama本地部署',
         shape='box3d', color=colors['deploy'])
dot.node('A1', '模型下载\nollama pull deepseek-r1:1.5b',
         shape='note', color=colors['deploy'])
dot.node('A2', '基础对话测试\nollama run ...',
         shape='note', color=colors['deploy'])
dot.edge('A', 'A1')
dot.edge('A', 'A2')

# 2. 知识库处理阶段
dot.node('B', '剧本知识库优化',
         shape='box3d', color=colors['process'])
dot.node('B1', '文本预处理\n正则提取场景/人物',
         shape='note', color=colors['process'])
dot.node('B2', '向量化处理\nChromaDB + BGE嵌入',
         shape='note', color=colors['process'])
dot.node('B3', '时序敏感检索\nMMR算法改进',
         shape='note', color=colors['optimize'])
dot.edge('B', 'B1')
dot.edge('B1', 'B2')
dot.edge('B2', 'B3')

# 3. UI配置阶段
dot.node('C', '交互界面开发',
         shape='box3d', color=colors['ui'])
dot.node('C1', 'Gradio框架\n宫廷风格CSS',
         shape='note', color=colors['ui'])
dot.node('C2', '提示工程优化\n角色扮演模板',
         shape='note', color=colors['optimize'])
dot.edge('C', 'C1')
dot.edge('C1', 'C2')

# 4. 对比验证阶段
dot.node('D', '效果对比验证',
         shape='box3d', color=colors['compare'])
dot.node('D1', '自动化测试脚本\n问题集比对',
         shape='note', color=colors['compare'])
dot.node('D2', '三维评估指标\n准确性/速度/引用率',
         shape='note', color=colors['compare'])
dot.edge('D', 'D1')
dot.edge('D1', 'D2')

# 连接主流程
dot.edge('A', 'B', label=' 模型准备 ')
dot.edge('B', 'C', label=' 知识库就绪 ')
dot.edge('C', 'D', label=' 系统验证 ')

# 创新点标注
with dot.subgraph(name='cluster_innovations') as c:
    c.attr(label='创新点', style='dashed', color='purple')
    c.node('I1', '时序敏感检索', color='#FF69B4')
    c.node('I2', '角色化提示工程', color='#FF69B4')
    c.node('I3', '场景化UI设计', color='#FF69B4')

    dot.edge('I1', 'B3', style='dashed', color='grey')
    dot.edge('I2', 'C2', style='dashed', color='grey')
    dot.edge('I3', 'C1', style='dashed', color='grey')

# 输出流程图
dot.format = 'png'
dot.render('deepseek_flowchart', view=True, cleanup=True)
print("流程图已生成：deepseek_flowchart.png")