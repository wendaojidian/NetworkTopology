from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from NetworkTopology import settings
from NetworkTopology.settings import RouterA, RouterB, RouterC
from command_util.command_util import *
from model.executetelnet import login_1st, login_2nd, execute_command, execute_commands, execute_command2
import json


class TopologyTest(APIView):
    # 上传配置文件
    @staticmethod
    def post(request, *args, **kwargs):
        login_2nd()
        file = request.FILES.get('file')
        if not file:
            return HttpResponse(status=500, content='软件上传失败')

        test_dict = json.load(file)['test']
        print(test_dict)

        num_success = 0
        num_fail = 0
        router = RouterA

        commands = enable(settings.CONF)
        execute_command2(commands)

        test_result = ""
        for case, command_info in test_dict.items():
            test_result += "Router: " + command_info["router"] + "\nTestcommand: " + command_info[
                "input"] + "\nThe expect output is:\n" + command_info["output"] + "\n\nThe actual output is:\n"
            if command_info["router"] == "RouterA":
                router = RouterA
            elif command_info["router"] == "RouterB":
                router = RouterB
            elif command_info["router"] == "RouterC":
                router = RouterC

            actual_output = router.exec_cmd(command_info["input"])
            test_result += actual_output + "\n\n"
            if get_test_result(actual_output, command_info["output"], command_info["type"]):
                test_result += "Success/n" + "-"*30 + "\n"
                num_success += 1
            else:
                test_result += "fail/n" + "-" * 30 + "\n"
                num_fail += 1

        test_result += "Success: " + str(num_success) + " Fail: " + str(num_fail)

        return Response(status=200, data=test_result)


class TopologyTestInput(APIView):
    # 上传配置文件
    @staticmethod
    def post(request, *args, **kwargs):
        login_2nd()
        file = request.FILES.get('file')
        output_path = request.POST.get("output_path")

        if not file:
            return HttpResponse(status=500, content='软件上传失败')

        test_dict = json.load(file)['test']
        print(test_dict)

        commands = enable(settings.CONF)
        output_str = execute_command2(commands)

        router = RouterA
        for case, command_info in test_dict.items():
            if command_info["router"] == "RouterA":
                router = RouterA
            elif command_info["router"] == "RouterB":
                router = RouterB
            elif command_info["router"] == "RouterC":
                router = RouterC

            print("input: ", command_info["input"])

            test_dict[case]["output"] = router.exec_cmd(command_info["input"])
            print("output: ", test_dict[case]["output"])
        test_dict_save = {'test': test_dict}
        with open(output_path, 'w') as file:
            file.write(json.dumps(test_dict_save))

        return HttpResponse(status=200, content="ok")

