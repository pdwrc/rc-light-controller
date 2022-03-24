import uselect
import sys
from config import config
import json
import time

class CLI:
    
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.buf = ""
        self.spoll = uselect.poll()
        self.spoll.register(sys.stdin, uselect.POLLIN)

    def process(self):
        while self.spoll.poll(0):
            c = sys.stdin.read(1)
            self.buf += c
            if c == "\n":
                break

        while '\n' in self.buf:
            (cmd, self.buf) = self.buf.split('\n', 1)
            self.do_command(cmd.rstrip())


    def do_command(self, s):
        if " " in s:
            (cmd, params) = s.split(" ", 1)
        else:
            (cmd, params) = (s, None)
        if cmd == 'VERSION':
            print("VERSION %s" % config.version)
        elif cmd == 'DUMPCONFIG':
            print("DUMPCONFIG " + json.dumps(config.config_data()))
        elif cmd == 'MENUSPEC':
            print("MENUSPEC " + json.dumps(self.vehicle.menu.spec()))
        elif cmd == 'IDENT' and params is not None:
            try:
                i = int(params)
                self.vehicle.ident(i)
                print("IDENT")
            except ValueError:
                print("ERR")
        elif cmd == 'ON' and params is not None:
            try:
                x = params.split(' ',2)
                ch = int(x[0])
                val = int(x[1])
                self.vehicle.light_on(ch, val)
                print("ON")
            except ValueError:
                print("ERR")
        elif cmd == 'OFF' and params is not None:
            try:
                i = int(params)
                self.vehicle.light_off(i)
                print("OFF")
            except ValueError:
                print("ERR")
        elif cmd == 'SET' and params is not None:
            args = params.split(' ')
            if len(args) != 2:
                print("ERR")
            else:
                (path, value) = args
                if config.set_value(path, value):
                    print("SET")
                    self.vehicle.update(reconfig = True)
                    config.save()
                else:
                    print("ERR")

        else:
            print("ERR")
