As I have some rather unusual scripts, I wanted to publish them in the hope they become handy for anyone. Even if you don't have the devices or setup itself, it might become handy the way they were scripted.

# Common Library
I build some scripts that are reusable in multiple script sets. For this reason I added a directory with common scripts which get sourced into the python script. For some reason it does not work with default import mechanism of python, but execfile is working fine.

The 


## Exec/CommandMap Rule
This Script consist of a general ExecRule class which does the general mapping. You simply define which items should be listened on and it will translate commands -> values.
In this example it maps commands to IR values, but it could map to a more complex object as well. It will call self.commandTriggered with this value.

In this example it is overloaded by the method in IrTransmitter which will call the appropiate command.

```
execfile("/opt/openhab/configurations/scripts/common/execMap.py")

def getRules():
    irTransmit = IrTransmitter("DENON", {
        "ReceiverPowerCmd": { "ON": "ON", "OFF": "OFF" },
        "ReceiverVolumeCmd": { "ON": "VOL+", "OFF": "VOL-" },
        "ReceiverChannel": { "PC": "4", "PI": "5" }
    })

    return RuleSet([irTransmit])
```

## Alive Checker
This checks devices/PCs by simple ICMP messages if they are online.

```
execfile("/opt/openhab/configurations/scripts/common/aliveChecker.py")

def getRules():
    return RuleSet([
        AliveChecker([("simon", "SimonPC")]),
	])
```

## CountdownTimer
This is a configurable timer. It will use three items to show its states:

- timerItem: activates/deactives the timer
- timerCurrent: the current remaining time (in minutes), before the commandItem will receive "OFF" command
- timerDuration: the initial duration until OFF is sent
- commandItem: the command receiving item

item config:
```
Switch ReceiverPower "Receiver Power" <socket>
Switch Receiver_TimerActive <clock> (livingroom)
Number Receiver_TimerDuration <clock> (livingroom)
Number Receiver_TimerCurrent <clock> (livingroom)
```

sitemap config:
```
Frame label="Multimedia Timer" {
    Switch item=Receiver_TimerActive label="timer activ" icon="clock"
    Setpoint item=Receiver_TimerDuration label="duration [%d]" icon="clock" minValue=1 maxValue=59 step=1
    Setpoint item=Receiver_TimerCurrent label="remaining [%d]" icon="clock" minValue=1 maxValue=59 step=1 
}
```

script: 
```
execfile("/opt/openhab/configurations/scripts/common/countdownTimer.py")

def getRules():
    return RuleSet([
        CountdownTimer("Receiver_TimerActive", "Receiver_TimerCurrent", "Receiver_TimerDuration", "ReceiverPower")
	])
```

## AlarmClock
This is a configurable clock alarm. You can configure hours and minutes of the next alarm and activate it by items.


- itemActive: activate/deactivate alarm
- itemHours: hours of next alarm
- itemMinutes: minutes of next alarm
- commandItem: item which will receive "ON"

items:

```
Switch Receiver_WeckerActive <clock> (bedroom)
Number Receiver_WeckerHours <clock> (bedroom)
Number Receiver_WeckerMinutes <clock> (bedroom)
```

sitemap:
```
Frame label="Multimedia Wecker" {
    Switch item=Receiver_WeckerActive label="alarm active" icon="clock"
    Setpoint item=Receiver_WeckerHours label="hours [%d]" icon="clock" minValue=0 maxValue=23 step=1
    Setpoint item=Receiver_WeckerMinutes label="minutes [%d]" icon="clock" minValue=0 maxValue=59 step=1 
}
```

script:

```
execfile("/opt/openhab/configurations/scripts/common/alarmClock.py")

def getRules():
    return RuleSet([
        AlarmClock("Receiver_WeckerActive", "Receiver_WeckerHours", "Receiver_WeckerMinutes", "Spotify"),
	])
```


# Miscellaneous

## Buderus KM200 "Binding"
This is more like a binding than a script, as it will connect to the KM200 device, receives its values and updates items in openhab based on that.

it uses:

- Java Crypto API (you have to change the [JCE policy](http://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html)
- Time trigger
