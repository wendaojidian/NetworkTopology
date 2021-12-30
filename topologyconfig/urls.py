from django.urls import path
from .views.topologyfile import TopologyFile
from .views.topologyconfig import TopologyConfigLines, TopologyConfigScript, TopologyConfigLists, TopologyConfig
from .views.topologygraph import TopologyGraph, TopologyRoute
from .views.topologytest import TopologyTest, TopologyTestInput

urlpatterns = [
    # 上传配置文件，返回配置文件内容
    path('topology-file', TopologyFile.as_view()),
    # 输入配置文件内容，返回命令列表
    path('config-list', TopologyConfigLists.as_view()),
    # 执行单条命令
    path('config-command', TopologyConfigLines.as_view()),
    # 获取拓扑图
    path('topology-graph', TopologyGraph.as_view()),
    # 上传执行测试文件
    path('topology-test', TopologyTest.as_view()),
    # 获取路由器信息（brief）
    path('topology-route/<str:router_name>', TopologyRoute.as_view()),
    # 输入配置文件内容，执行命令（前端不需用）
    path('config-script', TopologyConfigScript.as_view()),
    # 写入测试文件（前端不需用）
    path('topology-write', TopologyTestInput.as_view())
]
"""
TopologyConfigLists
"""