from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from NetworkTopology.settings import RouterA, RouterB, RouterC
from command_util.command_util import get_conf, get_commands
from model.executetelnet import login_2nd, execute_command

from NetworkTopology import settings


class TopologyConfigScript(APIView):
    # 发送配置文件内容（字符串）执行
    @staticmethod
    def post(request, *args, **kwargs):
        # 检查登录
        login_2nd()
        script = request.POST.get('script')
        settings.CONF = get_conf(script)
        commands = get_commands(settings.CONF)
        return_info = execute_command(commands)
        return HttpResponse(status=200, content=return_info)
        # return Response(status=200, data=commands)


class TopologyConfigLists(APIView):
    # 发送配置文件内容（字符串），返回命令列表
    @staticmethod
    def post(request, *args, **kwargs):
        # 检查登录
        login_2nd()
        script = request.POST.get('script')
        settings.CONF = get_conf(script)
        commands = get_commands(settings.CONF)
        return Response(status=200, data=commands)


class TopologyConfigList(APIView):
    # 发送配置文件内容（字符串），返回命令列表
    @staticmethod
    def post(request, *args, **kwargs):
        # 检查登录
        login_2nd()
        script = request.POST.get('script')
        settings.CONF = get_conf(script)
        commands = get_commands(settings.CONF)
        return Response(status=200, data=commands)


class TopologyConfigLines(APIView):
    # 前端交互执行（发送命令列表）
    @staticmethod
    def post(request, *args, **kwargs):
        login_2nd()
        router_name = request.POST.get('router')
        command = request.POST.get('command')
        password = request.POST.get('password')
        print('here!')

        router = RouterA
        if router_name == 'RouterB':
            router = RouterB
        elif router_name == 'RouterC':
            router = RouterC

        return_msg = None
        if command == 'enable':
            router.input('enable')
            if password:
                router.tn.read_until(b'Password:')
                print('password read done')
                return_msg = router.exec_cmd(password)
        elif command == 'reload':
            router.input('reload')
            router.tn.read_until(b"[yes/no]: ")
            router.input('no')
            router.tn.read_until(b"[confirm]")
            return_msg = router.exec_cmd("")
        else:
            return_msg = router.exec_cmd(command)

        return HttpResponse(status=200, content=return_msg)

