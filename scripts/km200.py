km200_gateway_host = "KM200_IP"
km200_gateway_password = "GATEWAY_PW_ON_DEVICE"
km200_private_password = "PRIVATE_PW_SET_ON_APP"

needed_data = {
    "/system/healthStatus" : {"type": "string", "name": "Heizung_HealthStatus"},
    "/system/appliance/actualSupplyTemperature": {"type": "number", "name": "Heizung_ActualSupplyTemperature"},
    "/system/appliance/actualPower": {"type": "number", "name": "Heizung_ActualPower"},
    
    "/heatSources/actualPower": {"type": "number", "name": "Heizung_ActualPower_Total"},
    "/heatSources/actualCHPower": {"type": "number", "name": "Heizung_ActualPower_Heizung"},
    "/heatSources/actualDHWPower": {"type": "number", "name": "Heizung_ActualPower_HotWater"},
    
    "/system/sensors/temperatures/switch": {"type": "number", "name": "Heizung_Switch"},
    "/system/sensors/temperatures/outdoor_t1": {"type": "number", "name": "Heizung_Outdoor"},
    "/system/sensors/temperatures/supply_t1": {"type": "number", "name": "Heizung_SupplyGas"},
    "/system/sensors/temperatures/hotWater_t2": {"type": "number", "name": "Heizung_HotWater"},
    "/system/sensors/temperatures/supply_t1_setpoint": {"type": "number", "name": "Heizung_SollVorlauf"},

    "/solarCircuits/sc1/dhwTankTemperature": {"type": "number", "name": "Heizung_SolarCircuits_TankTemparture"},
    "/solarCircuits/sc1/solarYield": {"type": "number", "name": "Heizung_SolarCircuits_Yield"},
    "/solarCircuits/sc1/collectorTemperature": {"type": "number", "name": "Heizung_SolarCircuits_CollectorTemperatur"}
}

#########################################

import base64
import hashlib
import urllib2
import struct
import json

import javax.crypto.Cipher as Cipher
import javax.crypto.spec.SecretKeySpec as SecretKeySpec

class Buderus(object):
    SALT = struct.pack("B"*32,
                       0x86, 0x78, 0x45, 0xe9, 0x7c, 0x4e, 0x29, 0xdc,
                       0xe5, 0x22, 0xb9, 0xa7, 0xd3, 0xa3, 0xe0, 0x7b,
                       0x15, 0x2b, 0xff, 0xad, 0xdd, 0xbe, 0xd7, 0xf5,
                       0xff, 0xd8, 0x42, 0xe9, 0x89, 0x5a, 0xd1, 0xe4
                       )

    def __init__(self, gateway_host, gateway_password, private_password):
        self.host = gateway_host

        key1 = hashlib.md5()
        key1.update(gateway_password)
        key1.update(self.SALT)

        key2 = hashlib.md5()
        key2.update(self.SALT)
        key2.update(private_password)

        self.key = key1.digest() + key2.digest()

        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'TeleHeater/2.2.3'), ('Accept', 'application/json')]

        self.secretKey = SecretKeySpec(self.key, "AES")
        self.cipher = Cipher.getInstance("AES/ECB/NoPadding")



    def __decryption(self, encryptedString):
        PADDING = "{"
        self.cipher.init(Cipher.DECRYPT_MODE, self.secretKey)
        decrypted = self.cipher.doFinal(base64.b64decode(encryptedString))

        return decrypted.tostring()

    def get_data(self, path):
        resp = self.opener.open('http://'+km200_gateway_host+path)
        #text = self.__decryption("rBSVKLwPDuFypfXMvKaRjdw7kE+skfJCgU9nwBHPjxgE91xLeRZYq8G4HH5xVcpxLPVxsYIIciOrnAocK9vZbwkmzEF6igfa2VBhiffTw1ikISJsmYSNuXERpody8oCr")
        text = self.__decryption(resp.read())
        text = text[:text.rindex("}")+1]

        return text

    def get_json(self, path):
        return json.loads(self.get_data(path))

    def print_all_values(self):
        restree = [ "/system", "/gateway", "/recordings", "/heatingCircuits", "/solarCircuits"]

        for rest in restree:
            todo = [rest]
            for res in todo:
                try:
                    text = self.get_data(res)

                    try:
                        j = json.loads(text)

                        if "references" in j:
                            for ref in j["references"]:
                                todo.append(ref["id"])
                        else:
                            print j.pop("id"),"=", str(j.pop("value")), "            \t############", j
                    except Exception,e:
                        print res, "no json:", text, "error: ", e

                except Exception, e:
                    print "res", res, "Error", e




class BuderusUpdater(Rule):
    def __init__(self):
        self.__eventTrigger = [StartupTrigger(), TimerTrigger("30 * * * * ?")]
        self.buderus = Buderus(km200_gateway_host, km200_gateway_password, km200_private_password)


    def getEventTrigger(self):
        return self.__eventTrigger

    def execute(self, event):
        for path, target in needed_data.iteritems():
            data = self.buderus.get_json(path)
            status = None

            if target["type"] == "switch":
                status = "ON" if (data["value"] == "ACTIVE") else "OFF"
            else:
                status = str(data["value"])

            item = ItemRegistry.getItem(target["name"])
            if str(item.state) != status:
                oh.postUpdate(target["name"], str(status))

def getRules():
    return RuleSet([
        BuderusUpdater()
    ])
