import json
from typing import List, Dict


def extract_reservable_slots(html_content: str) -> Dict[str, List[str]]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')
    reservable_days = {}

    # red-ok クラスの日付のみ取得
    special_days = soup.find_all('a', class_='red-ok')

    for day in special_days:
        date_str = day.get('onclick').split("'")[1]
        hidden_input = day.find_next('input', type='hidden')

        if hidden_input:
            slot_data = json.loads(hidden_input.get('value'))
            reservable_times = [
                slot['name'] for slot in slot_data[0]['comas']
                if slot.get('reservable', False)
            ]

            reservable_days[date_str] = reservable_times

    return reservable_days


# 使用例


def main():
    with open('test_calendar.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    reservations = extract_reservable_slots(html_content)
    for date, times in reservations.items():
        print(f"{date}: {times}")


if __name__ == '__main__':
    main()
    # 2025年2月9日: ['11:45', '12:00', '12:15', '12:30', '12:45', '13:15',
    # '13:30',  '13:45', '14:00', '14:15', '14:30', '14:45
    # ', '15:00', '15:15', '15:30', '15:45', '16:00', '16:15', '16:30',
    # '16:45', '17:00', '17:15', '17:30', '17:45', '18:00',
    # '18:15', '18:30', '18:45']
    # 2025年2月20日: ['10:00', '10:15', '10:30', '10:45', '11:00', '11:15',
    # '11:30', '11:45', '12:00', '12:15', '12:30', '12:45', '13:00', '13:15',
    # '13:30', # '13:45', '14:00', '14:15', '14:45', '15:00', '15:15', '15:30',
    # '15:45', '16:00', '16:15',
    #  '16:30', '16:45', '17:00', '17:15', '17:30', '17:45', '18:00', '18:15',
    # '18:30', '18:45']
