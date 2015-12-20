class AlarmClock(Rule):
    def __init__(self, itemActive, itemHours, itemMinutes, commandItem):
        self.timer = None

        self.itemActive = itemActive
        self.itemHours = itemHours
        self.itemMinutes = itemMinutes
        self.commandItem = commandItem

    def getEventTrigger(self):
        return [
            CommandEventTrigger(self.itemActive, None)
        ]

    def triggerAlarm(self):
        self.timer = None
        oh.postUpdate(self.itemActive, "OFF")
        oh.sendCommand(self.commandItem, "ON")

    def execute(self, event):
        if self.timer:
            self.timer.cancel()
            self.timer = None

        if event.command == OnOffType.ON:
            try:
                hours = ItemRegistry.getItem(self.itemHours).state.intValue()
                minutes = ItemRegistry.getItem(self.itemMinutes).state.intValue()

                today = DateTime.now().withTimeAtStartOfDay()
                atClock = today.plusHours(hours).plusMinutes(minutes)

                if atClock < DateTime.now():
                    atClock = atClock.plusDays(1)
                oh.logInfo("AlarmClock", "scheduled at {}", atClock)
                self.timer = oh.createTimer(atClock, self.triggerAlarm)
            except Exception, e:
                oh.logInfo("AlarmClock", "could not get hour and minutes")
                print e
