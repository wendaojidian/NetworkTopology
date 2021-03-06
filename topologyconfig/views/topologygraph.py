from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response

from NetworkTopology import settings
from NetworkTopology.settings import RouterA, RouterB, RouterC
from command_util.command_util import get_conf, construct_graph, enable, get_interface_info
from model.executetelnet import login_2nd, execute_command, execute_command2


class TopologyGraph(APIView):
    # 上传配置文件
    @staticmethod
    def get(request, *args, **kwargs):
        if settings.CONF == {}:
            return HttpResponse(status=500, content='配置文件未上传')
        topology_graph = construct_graph(settings.CONF)
        return Response(status=200, data=topology_graph)


class TopologyRoute(APIView):
    # 查看路由器信息
    @staticmethod
    def get(request, router_name, *args, **kwargs):
        if router_name == "RouterA":
            return Response(status=200, data=settings.RouterA_interface_brief)
        elif router_name == "RouterB":
            return Response(status=200, data=settings.RouterB_interface_brief)
        else:
            return Response(status=200, data=settings.RouterC_interface_brief)


# class TopologyRoute(APIView):
#     # 查看路由器信息
#     @staticmethod
#     def get(request, router_name, *args, **kwargs):
#         login_2nd()
#         commands = enable(settings.CONF, router_name)
#         commands.append((router_name, "command", "show ip interface brief"))
#         print(commands)
#
#         output_str = execute_command2(commands)
#         print("output_str:", output_str)
#         output = get_interface_info(output_str)
#
#         return Response(status=200, data=output)
