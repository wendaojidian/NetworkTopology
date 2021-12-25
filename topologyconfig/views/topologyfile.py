from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from NetworkTopology import settings
from command_util.command_util import *
from model.executetelnet import login_1st


class TopologyFile(APIView):
    # 上传配置文件
    @staticmethod
    def post(request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return HttpResponse(status=500, content='软件上传失败')

        conf_str = str(file.read(), encoding='utf-8')
        settings.CONF = get_conf(conf_str)
        login_info = get_login_infos(settings.CONF)
        print(login_info)
        if login_1st(login_info):
            return Response(status=200, data=conf_str)
        else:
            return HttpResponse(status=500, content="登录失败，正在尝试重连")

    @staticmethod
    def put(request, *args, **kwargs):
        pass

    @staticmethod
    def delete(request, *args, **kwargs):
        pass
