import json


def get_signals():
    with open("measure.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    result = []
    for exhauster in data:
        data = {"exhauster": exhauster["exhauster"], "signals": []}
        data["signals"].append(func("p7_vibration_horizontal", exhauster))

        result.append(data)
    return result


def func(key, exhauster):
    if (
        exhauster[key + "_warning_max"]
        < exhauster[key]
        < exhauster[key + "_warning_min"]
        and exhauster[key + "_alarm_min"]
        < exhauster[key]
        < exhauster[key + "_alarm_max"]
    ):
        return f"{key}_warning"
    elif exhauster[key + "_alarm_max"] < exhauster[key] < exhauster[key + "_alarm_min"]:
        return f"{key}_alarm"
