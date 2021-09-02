import requests
import os
from datetime import date, timedelta
from xml.etree import ElementTree as ET


def check_data(data_path):
    if os.path.exists(data_path):
        tree = ET.parse(data_path)
        root = tree.getroot()
        if root.attrib["Date"] == date.today().strftime("%d.%m.%Y"):
            return True
    return False


def download_data(data_path):
    if not check_data(data_path):
        print("Нет актуальных данных, идет скачивание с сайта")
        d = date.today()
        tree = ET.ElementTree(ET.fromstring(f'<ValCurses Date="{d.strftime("%d.%m.%Y")}" name="Database"></ValCurses>'))
        root = tree.getroot()
        for _ in range(90):
            params = {"date_req": d.strftime("%d/%m/%Y")}
            r = requests.get("http://www.cbr.ru/scripts/XML_daily.asp", params=params)
            child = ET.fromstring(r.text)
            root.append(child)
            d = d - timedelta(days=1)
        tree.write(data_path)
        print("Скачивание завершено")
        return
    print("Используются сохраненные данные")


def find_maximum(data):
    result = {
        "value": 0,
        "name": "",
        "date": ""
    }
    for day in data:
        d = day.attrib["Date"]
        for valute in day:
            value = float(valute[4].text.replace(",", "."))
            if value > result["value"]:
                result["value"] = value
                result["name"] = valute[3].text
                result["date"] = d
    return result


def find_minimum(data):
    result = {
        "value": float("inf"),
        "name": "",
        "date": ""
    }
    for day in data:
        d = day.attrib["Date"]
        for valute in day:
            value = float(valute[4].text.replace(",", "."))
            if value < result["value"]:
                result["value"] = value
                result["name"] = valute[3].text
                result["date"] = d
    return result


def count_median(data):
    counter = 0
    sum = 0
    for day in data:
        for valute in day:
            counter += 1
            sum += float(valute[4].text.replace(",", "."))
    return sum / counter


def main():
    cwd = os.getcwd()
    data_path = os.path.join(cwd, "data.xml")
    try:
        download_data(data_path)
    except requests.exceptions.ConnectionError:
        print("Не удается скачать данные с сайта")
        return
    data = ET.parse(data_path).getroot()
    maximum = find_maximum(data)
    minimum = find_minimum(data)
    median = count_median(data)


if __name__ == "__main__":
    main()
