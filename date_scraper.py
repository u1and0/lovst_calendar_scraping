"""予約された枠の数をカウントする"""
import json
from datetime import datetime
import requests
from typing import Dict, List
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://reserve.lovstmade.com"


def extract_store_urls(html_content: str) -> Dict[str, str]:
    soup = BeautifulSoup(html_content, 'html.parser')

    container = soup.find(id='container')
    store_urls = {}

    if container:
        submenu_items = container.find_all('li', class_='submenu')

        for item in submenu_items:
            store_name_span = item.find('span')
            store_name = store_name_span.text.strip(
            ) if store_name_span else 'Unknown'

            noborder_item = item.find('li', class_='noborder')
            if noborder_item:
                link = noborder_item.find('a')
                if link and link.get('href'):
                    store_urls[store_name] = link.get('href')

    return store_urls


def count_reserved_slots(html_content: str) -> Dict[str, int]:
    soup = BeautifulSoup(html_content, 'html.parser')
    reserved_slots = {}

    special_days = soup.find_all('a', class_='red-ok')

    for day in special_days:
        date_str = day.get('onclick').split("'")[1]
        date_obj = datetime.strptime(date_str, "%Y年%m月%d日")
        hidden_input = day.find_next('input', type='hidden')

        if hidden_input:
            slot_data = json.loads(hidden_input.get('value'))
            reserved_count = sum(1 for slot in slot_data[0]['comas']
                                 if not slot.get('reservable', False))

            reserved_slots[date_obj] = reserved_count

    return reserved_slots


def main(initial_html_content: str):
    # 1. 店名とURLのディクショナリを取得
    store_urls = extract_store_urls(initial_html_content)

    # 2-5. すべてのURLをスクレイピング
    all_store_reservations = {}

    for store_name, url in store_urls.items():
        print(f"fetching {store_name}...")
        try:
            # 3. HTMLコンテンツ取得
            response = requests.get(BASE_URL + url)
            response.raise_for_status()  # エラー時に例外を発生

            # 4. 予約スロットをカウント
            store_reservations = count_reserved_slots(response.text)

            # 5. 結果を保存
            all_store_reservations[store_name] = store_reservations

        except requests.RequestException as e:
            print(f"Error fetching URL for {store_name}: {e}")

    return all_store_reservations


if __name__ == '__main__':
    # HTMLファイルを読み込む
    response = requests.get(
        "https://reserve.lovstmade.com/reserve/calendar/115/202/261")
    html_content = response.content
    # 全店舗の予約状況を取得
    results = main(html_content)
    print(results)
