"""予約された枠の数をカウントする"""
import requests
import json
from typing import Dict
from bs4 import BeautifulSoup


def count_reserved_slots(html_content: str) -> Dict[str, int]:
    soup = BeautifulSoup(html_content, 'html.parser')
    reserved_slots = {}

    # red-ok クラスの日付のみ処理
    special_days = soup.find_all('a', class_='red-ok')

    for day in special_days:
        date_str = day.get('onclick').split("'")[1]
        hidden_input = day.find_next('input', type='hidden')

        if hidden_input:
            slot_data = json.loads(hidden_input.get('value'))
            reserved_count = sum(1 for slot in slot_data[0]['comas']
                                 if not slot.get('reservable', False))

            reserved_slots[date_str] = reserved_count

    return reserved_slots


# 使用例


def main():
    response = requests.get(
        "https://reserve.lovstmade.com/reserve/calendar/115/202/261")
    html_content = response.content
    # with open('test_calendar.html', 'r', encoding='utf-8') as f:
    #     html_content = f.read()

    reservations = count_reserved_slots(html_content)
    for date, count in reservations.items():
        print(f"{date}: {count} slots reserved")


if __name__ == '__main__':
    main()
