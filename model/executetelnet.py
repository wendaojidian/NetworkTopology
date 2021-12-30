import threading
import time

from NetworkTopology.settings import RouterA, RouterB, RouterC
from command_util.command_util import reload, enable, regen_commands


def login_1st2(login_info):
    if RouterA.ip is not None and RouterB.ip is not None and RouterC.ip is not None:
        commands = reload(login_info)
        output = execute_command(commands)

    RouterA.set_ip_password(login_info["RouterA"]["ip"], login_info["RouterA"]["password"])
    RouterB.set_ip_password(login_info["RouterB"]["ip"], login_info["RouterB"]["password"])
    RouterC.set_ip_password(login_info["RouterC"]["ip"], login_info["RouterC"]["password"])

    if RouterA.state in ["reload", "has_login", "logout"]:
        threading.Thread(target=login, args=(RouterA,))
    if RouterB.state in ["reload", "has_login", "logout"]:
        threading.Thread(target=login, args=(RouterB,))
    if RouterC.state in ["reload", "has_login", "logout"]:
        threading.Thread(target=login, args=(RouterC,))

    if RouterA.state == "login" and RouterB.state == 'login' and RouterC.state == 'login':
        RouterA.state = "has_login"
        RouterB.state = "has_login"
        RouterC.state = "has_login"
        return True
    else:
        return False


def login_1st(login_info):
    # 登出状态，设置ip和密码，启动登录线程，状态改为登录中logging状态，返回false
    if RouterA.state == "logout":
        RouterA.set_ip_password(login_info["RouterA"]["ip"], login_info["RouterA"]["password"])
        RouterB.set_ip_password(login_info["RouterB"]["ip"], login_info["RouterB"]["password"])
        RouterC.set_ip_password(login_info["RouterC"]["ip"], login_info["RouterC"]["password"])

        threading.Thread(target=login, args=(RouterA,)).start()
        threading.Thread(target=login, args=(RouterB,)).start()
        threading.Thread(target=login, args=(RouterC,)).start()

        RouterA.state = "logging"
        RouterB.state = "logging"
        RouterC.state = "logging"
        return False

    # 登录中状态，返回false
    elif RouterA.state == "logging" or RouterB.state == "logging" or RouterC.state == "logging":
        return False

    # 已登录状态，判断是否包含配置
    elif RouterA.state == 'login' and RouterB.state == 'login' or RouterC.state == 'login':
        # 未配置，即第一次配置，修改状态为已配置，返回true
        if not RouterA.has_config:
            RouterA.has_config = True
            RouterB.has_config = True
            RouterC.has_config = True
            return True
        # 已配置，执行reload操作，状态改为logging。
        else:
            login(RouterA)
            login(RouterB)
            login(RouterC)

            commands = enable(login_info)
            commands.extend(reload(login_info))
            execute_command2(commands)
            # commands = regen_commands(commands)
            # print("command2:", commands)
            # output = execute_command(commands)

            threading.Thread(target=login, args=(RouterA,)).start()
            threading.Thread(target=login, args=(RouterB,)).start()
            threading.Thread(target=login, args=(RouterC,)).start()

            RouterA.state = "logging"
            RouterB.state = "logging"
            RouterC.state = "logging"

            RouterA.has_config = False
            RouterB.has_config = False
            RouterC.has_config = False
            return False


def login_2nd():
    login(RouterA)
    login(RouterB)
    login(RouterC)
    return True


def login(route):
    i = 1
    while 1:
        if route.login():
            route.state = "login"
            route.i += 1
            return
        else:
            print("第{}次尝试登录{}".format(i, route.name))
            i += 1
        time.sleep(1)


def execute_command2(commands):
    router = RouterA
    return_info = ''

    for info in commands:
        print(info)
        if info[0] == 'RouterA':
            router = RouterA
        elif info[0] == 'RouterB':
            router = RouterB
        elif info[0] == 'RouterC':
            router = RouterC
        if info[1] == 'input':
            print(info[3])
            router.input(info[3])
            router.tn.read_until(info[2])

            print("=" * 20)
            print(return_info)
            print()
        else:
            print(info[2])
            return_info += router.exec_cmd(info[2])
            print("=" * 20)
            print(return_info)
            print()
    return return_info


def execute_command(router_name, command, input_note=""):
    router = RouterA
    if router_name == 'RouterA':
        router = RouterA
    elif router_name == 'RouterB':
        router = RouterB
    elif router_name == 'RouterC':
        router = RouterC
    return_info = ""
    if input_note == "":
        print(command)
        return_info = router.exec_cmd(command)
        print(return_info)
    else:
        print(command)
        router.input(command)
        router.tn.read_until(bytes(input_note, encoding='utf-8'))
    return return_info


def execute_commands(commands):
    return_info = ""
    for command in commands:
        if len(list(command.keys())) == 3:
            return_info += execute_command(command['router'], command['command'], command['input'])
        else:
            return_info += execute_command(command['router'], command['command'])
    return return_info
