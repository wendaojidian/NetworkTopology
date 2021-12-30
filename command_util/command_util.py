# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 19:11:08 2021

@author: querry.ton
"""

import re
import json


def get_raw_conf(file_path):
    '''
    Parameters
    ----------
    file_path : string
        yml配置文件的路径.

    Returns
    -------
    string
        配置文件的原始文本，与get_conf()生成的配置字典做区分.

    '''
    with open(file_path, 'r') as f:
        return f.read()


def get_conf(conf_str):
    '''
    根据配置文件生成配置字典.
    当配置文件格式正确时，返回对应的配置字典.
    当配置文件为空，或者配置文件格式错误时，返回空字典.
    
    Parameters
    ----------
    conf_str : string
        配置字符串
        
    Returns
    -------
    conf : dict()-{router_name:dict()}-{router_name:{ip:string, password:string, port:list(), command:list(), ping:list(), show:string, showtest:list()}}
        根据配置文件生成的dict()类型的结果.
        For Example:
            {
                'RouterA':{
                    'ip': '172.16.0.1', 
                    'password': 'CISCO', 
                    'port': ['s0/0/0:192.168.1.2 255.255.255.0', 'lo0:172.16.1.1 255.255.255.0', 'lo1:172.16.2.1 255.255.255.0', 'lo2:172.16.3.1 255.255.255.0'], 
                    'command': ['router ospf 1', 'network 192.168.1.0 0.0.0.255 area 0', 'network 172.16.0.0 0.0.255.255 area 1'], 
                    'ping': ['192.168.1.1', '192.168.2.1', '192.168.2.2'], 
                    'show': 'sh ip route ospf', 
                    'showtest': ['192.168.2.0 via 192.168.1.1']
                }, 
                'RouterB': {
                    'ip': '172.16.0.2', 
                    'password': 'CISCO', 
                    'port': ['s0/0/0:192.168.1.1 255.255.255.0', 's0/0/1:192.168.2.1 255.255.255.0'], 
                    'command': ['router ospf 1', 'network 192.168.1.0 0.0.0.255 area 0', 'network 192.168.2.0 0.0.0.255 area 51'], 
                    'ping': ['192.168.1.2', '192.168.2.2'], 'show': 'sh ip route ospf', 
                    'showtest': ['172.16.1.1 via 192.168.1.2', '172.16.2.1 via 192.168.1.2', '172.16.3.1 via 192.168.1.2']
                }, 
                'RouterC': {
                    'ip': '172.16.0.3', 
                    'password': 'CISCO', 
                    'port': ['s0/0/1:192.168.2.2 255.255.255.0', 'lo0:172.24.2.1 255.255.255.0'], 
                    'command': ['router ospf 1', 'network 192.168.2.0 0.0.0.255 area 51'], 
                    'ping': ['192.168.1.2', '192.168.1.1', '192.168.2.1'], 
                    'show': 'sh ip route ospf', 
                    'showtest': ['172.16.1.1 via 192.168.2.1', '172.16.2.1 via 192.168.2.1', '172.16.3.1 via 192.168.2.1', '192.168.1.0 via 192.168.2.1']
                }
            }

    '''
    if not check_conf_file(conf_str):
        # print("nofile")
        return dict()

    conf = dict()
    lines = read_line(conf_str)
    for line in lines:

        if line == "Apache":
            continue
        conf_segs = line.split('=')
        router_name = conf_segs[0].split('.')[0]
        router_prop = conf_segs[0].split('.')[1]
        router_value = conf_segs[1]
        if router_name not in conf.keys():
            conf[router_name] = dict()
        conf[router_name][router_prop] = router_value

    router_names = conf.keys()
    for router_name in router_names:
        props = conf[router_name].keys()
        for prop in props:
            if prop in ["port", "command", "ping", "showtest"]:
                conf[router_name][prop] = conf[router_name][prop].split(',')
    return conf


def save_conf(conf, file_path):
    '''
    Parameters
    ----------
    conf :  dict()-{router_name:dict()}-{router_name:{ip:string, password:string, port:list(), command:list(), ping:list(), show:string, showtest:list()}}
        需要保存的配置字典.
    file_path : string
        保存的文件路径，文件类型应为yml.

    Returns
    -------
    None.

    '''
    router_names = conf.keys()
    with open(file_path, 'w') as f:
        for router_name in router_names:
            props = conf[router_name].keys()
            for prop in props:
                if type(conf[router_name][prop]) == list:
                    value = ""
                    for v in conf[router_name][prop]:
                        value = value + v + ","
                    value = value[0:-1]
                else:
                    value = conf[router_name][prop]
                f.writelines(router_name + "." + prop + "=" + value + "\n")


def get_login_infos(conf):
    '''
    Parameters
    ----------
    conf :  dict()-{router_name:dict()}-{router_name:{ip:string, password:string, port:list(), command:list(), ping:list(), show:string, showtest:list()}}
        配置文件转化成的字典，由函数get_conf()生成.

    Returns
    -------
    init_infos : dict()
        telnet连接路由器所需要的信息，包括ip、password、username（可能没有）.
        
        For Example:
            {
                'RouterA': {'ip': '172.16.0.1', 'password': 'CISCO'}, 
                'RouterB': {'ip': '172.16.0.2', 'password': 'CISCO'}, 
                'RouterC': {'ip': '172.16.0.3', 'password': 'CISCO'}
            }

    '''
    login_infos = dict()
    router_names = conf.keys()
    for router_name in router_names:
        if router_name not in login_infos.keys():
            login_infos[router_name] = dict()
        login_infos[router_name]["ip"] = conf[router_name]["ip"]
        login_infos[router_name]["password"] = conf[router_name]["password"]
    return login_infos


def reload(conf):
    '''
    !!!在执行函数get_commands()函数提供的命令之前，需要重启路由器，即执行此函数提供的命令.
    !!!在执行完此函数返回的命令后，telnet会断开连接，等待路由器重启后才可重连.
    
    Parameters
    ----------
    conf :  dict()-{router_name:dict()}-{router_name:{ip:string, password:string, port:list(), command:list(), ping:list(), show:string, showtest:list()}}
        配置文件转化成的字典化成的字典，由函数get_conf()生成.

    Returns
    -------
    commands : list()-[(router_name, type, _)] | [(router_name, type, _, _)]-[(rouet_name, "command", command)] | [(rouet_name, "input", read_until, input)]
        列表项是一个三元组或四元组，
        元组的第一个位置是路由器名称，
        元组的第二个位置是命令类型，可选值"command" | "input"，
        当命令类型是"command"时，列表项时一个三元组，元组的第三个位置是命令，
        当命令类型是"input"时，列表项是一个四元组，
            元组的第三个位置是read_until，第四个位置是input，
            分别对应Python连接代码中的self.tn.read_until(string)和self.input(string)中的参数..
    '''
    commands = list()
    router_names = conf.keys()
    for router_name in router_names:
        commands.append((router_name, "input", b"[yes/no]: ", "reload"))
        commands.append((router_name, "input", b"[confirm]", "no"))
        commands.append((router_name, "command", ""))

    return commands


def enable(conf, router_name=None):
    '''
    此函数返回从初始状态进入特权模式的命令.
    Parameters
    ----------
    conf: 配置字典
    router_name: 需要进入特权模式的路由器名称; 当值为None时, 指的是所有路由器.

    Returns
    -------
    commands: 命令列表

    '''
    commands = list()
    if router_name:
        commands.append((router_name, "input", b"Password: ", "enable"))
        commands.append((router_name, "command", conf[router_name]["password"]))
    else:
        router_names = conf.keys()
        for router_name in router_names:
            commands.append((router_name, "input", b"Password: ", "enable"))
            commands.append((router_name, "command", conf[router_name]["password"]))
    return commands


def configure_terminal(conf, router_name=None):
    '''
    此函数返回从初始状态进入全局配置模式的命令.
    Parameters
    ----------
    conf: 配置字典
    router_name: 需要进入全局配置模式的路由器名称; 当值为None时, 指的是所有路由器.

    Returns
    -------
    commands: 命令列表

    '''
    commands = list()
    if router_name:
        commands.extend(enable(conf, router_name))
        commands.append((router_name, "command", "configure terminal"))
    else:
        router_names = conf.keys()
        for router_name in router_names:
            commands.extend(enable(conf, router_name))
            commands.append((router_name, "command", "configure terminal"))
    return commands


def get_commands(conf):
    '''
    !!!执行此函数获取命令之前，需要先执行reload()函数返回的命令，重启路由器.
    !!!在执行完reload()函数返回的命令后，telnet会断开连接，等待路由器重启后才可重连.
    
    Parameters
    ----------
    conf :  dict()-{router_name:dict()}-{router_name:{ip:string, password:string, port:list(), command:list(), ping:list(), show:string, showtest:list()}}
        配置文件转化成的字典化成的字典，由函数get_conf()生成.

    Returns
    -------
    commands : list()-[(router_name, type, _)] | [(router_name, type, _, _)]-[(rouet_name, "command", command)] | [(rouet_name, "input", read_until, input)]
        列表项是一个三元组或四元组，
        元组的第一个位置是路由器名称，
        元组的第二个位置是命令类型，可选值"command" | "input"，
        当命令类型是"command"时，列表项时一个三元组，元组的第三个位置是命令，
        当命令类型是"input"时，列表项是一个四元组，
            元组的第三个位置是read_until，第四个位置是input，
            分别对应Python连接代码中的self.tn.read_until(string)和self.input(string)中的参数.

        命令执行时，必须按照列表中的命令顺序执行.
    '''
    commands = list()
    router_names = conf.keys()
    for router_name in router_names:
        commands.append((router_name, "input", b"Password: ", "enable"))
        commands.append((router_name, "command", conf[router_name]["password"]))
        commands.append((router_name, "command", "configure terminal"))

    for router_name in router_names:
        props = conf[router_name].keys()
        if "port" in props:
            for command in get_command("port", conf[router_name]["port"]):
                commands.append((router_name, "command", command))
        if "command" in props:
            for command in get_command("command", conf[router_name]["command"]):
                commands.append((router_name, "command", command))

    for router_name in router_names:
        commands.append((router_name, "command", "exit"))

    for router_name in router_names:
        props = conf[router_name].keys()
        if "ping" in props:
            for command in get_command("ping", conf[router_name]["ping"]):
                commands.append((router_name, "command", command))

    for router_name in router_names:
        props = conf[router_name].keys()
        if "show" in props:
            for command in get_command("show", conf[router_name]["show"]):
                commands.append((router_name, "command", command))

    return commands


def regen_commands(commands):
    command_list = []
    for command in commands:
        if len(command) == 4:
            command_list.append({
                "router": command[0],
                "command": command[3],
                "input": command[2],
            })
        elif len(command) == 3:
            command_list.append({
                "router": command[0],
                "command": command[2],
            })
    return command_list


def get_interface_info(brief, detail=None):
    '''
    Parameters
    ----------
    brief : string
        在特权模式下用命令show ip interface brief可以获得此参数.
    detail : string | None
        在特权模式下用命令show ip interface可以获得此参数.
        需要此信息的原因是brief的IP-Address字段中没有子网掩码，需要从detail中获取.
        当值为None时，不会获取子网掩码.
    Returns
    -------
    interface_info : dict()
        {
            "title":list(), # 列表的列标题，即data字段中每一项的dict对应的key
            "data":list()   # list中每一项都是dict
        }
        For Example：
        {
            "title":['Interface', 'IP-Address', 'OK?', 'Method', 'Status', 'Protocol'],
            "data":[
                {
                    'Interface': 'FastEthernet0/0', 
                     'IP-Address': '172.16.0.1/16', 
                     'OK?': 'YES', 
                     'Method': 'manual', 
                     'Status': 'up', 
                     'Protocol': 'up'
                 },
                {
                    'Interface': 'FastEthernet1/0', 
                     'IP-Address': 'unassigned', 
                     'OK?': 'YES', 
                     'Method': 'unset', 
                     'Status': 'administratively down', 
                     'Protocol': 'down'
                 },
                ......
            ]
        }
    '''
    briefs = brief.replace('\r', '').split('\n')[2:-2]

    
    interface_info = {
        "title": list(),
        "data": list()
    }
    for i in range(len(briefs) - 1):
        interface_info["data"].append(dict())

    begin = 0
    flag = False
    for i in range(len(briefs[0])):
        if briefs[0][i] == ' ':
            flag = True
        if briefs[0][i] != ' ' and flag:
            title = briefs[0][begin:i].strip()
            interface_info["title"].append(title)
            for j in range(1, len(briefs)):
                interface_info["data"][j - 1][title] = briefs[j][begin:i].strip()
            flag = False
            begin = i;
        if i == len(briefs[0]) - 1:
            title = briefs[0][begin:].strip()
            interface_info["title"].append(title)
            for j in range(1, len(briefs)):
                interface_info["data"][j - 1][title] = briefs[j][begin:].strip()

    if detail is not None:
        details = detail.replace('\r', '').split('\n')
        useful_details = list()
        for idx, d in enumerate(details):
            if d[0] != ' ':
                useful_details.append(d)
                useful_details.append(details[idx + 1])

        for interface in interface_info["data"]:
            if interface["Interface"][0:2] == "Lo":
                continue;
            if interface["Status"] != "up" or interface["Protocol"] != "up":
                continue;
            for idx, ud in enumerate(useful_details):
                if ud.find(interface["Interface"]) != -1:
                    interface["IP-Address"] = useful_details[idx + 1].split("is ")[1]

    return interface_info


def construct_graph(conf, filtrate=True):
    '''
    Parameters
    ----------
    conf :  dict()-{router_name:dict()}-{router_name:{ip:string, password:string, port:list(), command:list(), ping:list(), show:string, showtest:list()}}
        配置字典，通过配置字典生成网络的逻辑拓扑.
        
    filtrate: 是否过滤只有一个端口的子网

    Returns
    -------
    graph : dict()-{subnet:list()}-{subnet:[tuple]}-{subnet:[(router_name, interface)]}
        路由器的interface之间的连接关系.
        
        For Example:
            graph={
                '192.168.1.0.': [('RouterA', 's0/0/0'), ('RouterB', 's0/0/0')], 
                '192.168.2.0.': [('RouterB', 's0/0/1'), ('RouterC', 's0/0/1')]
            }
            对应的图为: (RouterA:s0/0/0)<---192.168.1.0--->(s0/0/0:RouterB:s0/0/1)<---192.168.2.0--->(s0/0/1:RouterC)

    '''
    router_names = conf.keys()
    graph = dict()
    for router_name in router_names:
        ports = conf[router_name]["port"]
        for port in ports:
            if port[0:2] != 'lo':
                seg = port.split(':')
                ip, mask = tuple(seg[1].split(' '))
                ip, mask = ip.split('.'), mask.split('.')
                subnet = ""
                for i in range(4):
                    subnet = subnet + str(int(ip[i]) & int(mask[i])) + "."
                if subnet not in graph.keys():
                    graph[subnet] = list()
                graph[subnet].append((router_name, seg[0]))
                
    if filtrate:
        subnets = list(graph.keys())
        for subnet in subnets:
            if len(graph[subnet])==1:
                del graph[subnet]

    return graph


def get_test_cases(test_str):
    '''
    Parameters
    ----------
    test_str : string
        json测试字符串.

    Returns
    -------
    test_cases : dict()-{case_name:dict()}-{case_name:{input:string, output:string}}
        读取测试文件，转换成字典类型.

    '''
    test_cases = json.load(test_str)["test"]
    return test_cases


def get_test_result(actual_output, expect_output, test_type):
    if test_type==0:
        return actual_output==expect_output
    else:
        return actual_output.find(expect_output)!=-1;

# -----------------以下函数是上述函数的辅助函数----------------------------------
def read_line(conf_str):
    '''
    Parameters
    ----------
    conf_str : string
        配置字符串

    Yields
    ------
    string
        配置文件中的一行（过滤了多个连续空格、续行符、空行）
    '''
    lines = conf_str.replace('\\r', '').replace('\r', '').replace('\\n', '\n').split('\n')
    res_line = ""
    for line in lines:
        # 处理空行，空行只有一个换行符
        if len(line) == 0:
            continue
        # 处理前导空格
        res_line += line.lstrip()
        # 处理续行符
        if res_line[-1] != '\\':
            # 处理多个连续的空格
            yield re.sub(' +', ' ', res_line)
            res_line = ""
        res_line = res_line[0:-1]


def check_conf_file(conf_str):
    '''
    该函数只对配置文件的格式做一个简单的检查，保证get_commands()函数不抛出异常.
    
    Parameters
    ----------
    conf_str : string
        配置字符串.

    Returns
    -------
    bool
        配置文件格式符合要求，返回True.s
        否则，返回False.

    '''
    lines = read_line(conf_str)
    for line in lines:
        if line == "Apache":
            continue
        if line.find('=') == -1:
            return False
        conf_segs = line.split('=')
        if conf_segs[0].find('.') == -1:
            return False
        router_prop = conf_segs[0].split('.')[1]
        if router_prop not in ['ip', 'password', 'port', 'command', 'ping', 'show', 'showtest']:
            return False
        router_value = conf_segs[1]
        if router_prop in ["port", "command", "ping", "showtest"]:
            router_value = router_value.split(',')
        if router_prop == "port":
            for value in router_value:
                if value.find(':') == -1:
                    return False
                if value.split(':')[1].find(' ') == -1:
                    return False
    return True


def get_command(prop, values):
    '''
    Parameters
    ----------
    prop : string
        属性字段.
    values : list()
        值列表.
        
        For Example:
            
            Example 1.
            配置语句: RouterA.ip=172.16.0.1
            其: prop="ip", 
                values=["172.16.0.1"]
            
            Example 2.
            配置语句: RouterA.port=s0/0/0:192.168.1.2 255.255.255.0,lo0:172.16.1.1 255.255.255.0,lo1:172.16.2.1 255.255.255.0,lo2:172.16.3.1 255.255.255.0
            其: prop="port", 
                values=[
                    "s0/0/0:192.168.1.2",
                    "lo0:172.16.1.1",
                    "lo1:172.16.2.1",
                    "lo2:172.16.3.1"
                ]
    Returns
    -------
    commands : list()
        一条配置语句可能对应多个命令，
        因此返回的是命令列表，
        列表项的数据类型是字符串.
        
        For Example:
            配置语句: RouterA.port=s0/0/0:192.168.1.2 255.255.255.0,lo0:172.16.1.1 255.255.255.0,lo1:172.16.2.1 255.255.255.0,lo2:172.16.3.1 255.255.255.0
            commands=[
                "interface s0/0/0",
                "ip address 192.168.1.2 255.255.255.0",
                "no shutdown",
                "exit",
                "interface loopback 0",
                "ip address 172.16.1.1 255.255.255.0",
                "exit",
                "interface loopback 1",
                "ip address 172.16.2.1 255.255.255.0",
                "exit",
                "interface loopback 2",
                "ip address 172.16.3.1 255.255.255.0",
                "exit"
            ]

    '''
    commands = list()
    if prop == "port":
        for value in values:
            interface = value.split(':')[0].lstrip()
            ip = value.split(':')[1].split(' ')[0].lstrip()
            mask = value.split(':')[1].split(' ')[1].lstrip()
            commands.append("interface " + interface)
            commands.append("ip address " + ip + " " + mask)
            if interface[0] != 'l':
                commands.append("no shutdown")
            commands.append("exit")
    elif prop == "command":
        for value in values:
            commands.append(value.lstrip())

    elif prop == "ping":
        for ip in values:
            commands.append("ping " + ip.lstrip());
    elif prop == "show":
        commands.append(values.lstrip())

    return commands


# --------------------------------用作函数测试-----------------------------------
if __name__ == '__main__':

    raw_conf = get_raw_conf("conf2.yml")
    # print(raw_conf)
    conf = get_conf(raw_conf)
    # print(conf)
    if len(conf) == 0:
        print("配置文件为空，或者格式错误！")
    else:
        login_infos = get_login_infos(conf)
        # print(login_infos)
        reload_commands = reload(conf)
        # print(reload_commands)
        commands = get_commands(conf)
        command_list = regen_commands(commands)
        print(commands)
        # save_conf(conf, "test_save.yml")
        graph = construct_graph(conf)
        # check_conf_file("./conf1.yml")

    
    # with open("./conf1_test.json", 'r') as f:
    #     test_cases = get_test_cases(f)

    # with open("./interface_brief.txt") as f0:
    #     with open("./interface_detail.txt") as f1:
    #         interface_info=get_interface_info(f0.read(), f1.read())
