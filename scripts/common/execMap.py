from subprocess import call

class ExecRule(Rule):
    def __init__(self, commandMap):
        self.commandMap = commandMap

    def commandTriggered(self, command):
        oh.logInfo("ExecRule", "PLEASE overload, command triggered:" + command)

    def getEventTrigger(self):
        events = []

        for x in self.commandMap.iterkeys():
            events.append(CommandEventTrigger(x, None))

        return events

    def execute(self, event):
        item_map = self.commandMap[event.item.name]
        triggered = str(event.command)
        cmd = item_map[triggered]
        self.commandTriggered(cmd)


class IrTransmitter(ExecRule):
    def __init__(self, device, irmap):
        ExecRule.__init__(self, irmap)
        self.device = device

    def commandTriggered(self, command):
        oh.logInfo("IrTransmitter", "device: {}, command: {}".format(self.device, command))
        callList = ["irsend", "SEND_ONCE", self.device, command]
        call(callList)
