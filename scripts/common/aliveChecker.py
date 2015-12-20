import os

class AliveChecker(Rule):
    def __init__(self, devices):
        self.devices = {}
        for x in devices:
            self.devices[x[0]] = { "rc": -1, "item": x[1] }

    def getEventTrigger(self):
        return [ StartupTrigger(), TimerTrigger("0/50 * * * * ?") ]

    def execute(self, event):
        for device in self.devices.iteritems():
            res = os.system("ping -c 1 "+device[0]+" > /dev/null")

            dev = device[1]
            if res != dev["rc"]:
                dev["rc"] = res
                oh.postUpdate(dev["item"], "ON" if res == 0 else "OFF")
