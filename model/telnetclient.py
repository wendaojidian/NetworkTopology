import telnetlib
import time


class TelnetClient:
    def __init__(self, route_name=None, ip=None, password=None):
        self.tn = telnetlib.Telnet()
        self.ip = ip
        self.password = password
        self.name = route_name
        self.state = "logout"
        self.has_config = False
        self.i = 0

    def set_ip_password(self, ip, password):
        self.ip = ip
        self.password = password

    def set_name(self, name):
        self.name = name

    def input(self, cmd):
        self.tn.write(cmd.encode('ascii') + b'\n')

    def get_output(self, sleep_seconds=2):
        time.sleep(sleep_seconds)
        return self.tn.read_very_eager().decode('ascii')

    def login(self):
        if self.ip is None or self.password is None:
            print(self.ip, self.password)
            return False
        login_result = None
        try:
            self.tn.open(self.ip)
            self.tn.read_until(b'Password: ')
            self.input(self.password)
            login_result = self.get_output()
            if 'Login incorrect' in login_result:
                print('用户名或密码错误')
                return False
        except:
            return False
        print(login_result)

        print('登陆成功')
        return True

    def logout(self):
        self.input('exit')

    def exec_cmd(self, cmd):
        self.input(cmd)

        try:
            res = self.get_output()
        except EOFError:
            raise EOFError("读写错误")
        print("===================")
        print(res)
        print("===================")
        return res

    def __str__(self):
        return self.ip + " " + self.password


if __name__ == '__main__':
    RouterA = TelnetClient(ip='172.16.0.1', password='CISCO')
    RouterA.login()
    tn = RouterA.input('enable')
    RouterA.tn.read_until(b'Password: ')
    RouterA.exec_cmd('CISCO')

    RouterA.input('show run')
    # print("read:", RouterA.tn.read_very_lazy())
    r = RouterA.tn.read_until(b' --More-- ')
    all = r[0:-10]
    while r[-10:]==b' --More-- ':
        print(str(r))
        RouterA.input('\r\n')
        RouterA.tn.read_until(b' --More-- ')
        r = RouterA.get_output()
        # print(RouterA.get_output())
        # print(r)
        # all += r

    # # time.sleep(1)
    # # print("yyy")
    # # RouterA.tn.read_until(b'Password: ')
    # print(RouterA.get_output())
    # RouterA.exec_cmd('CISCO')





