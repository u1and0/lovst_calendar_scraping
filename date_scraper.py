"""Lovstの予約された枠の数をカウントする"""
import requests
import asyncio
import aiohttp
import json
from typing import Dict
from bs4 import BeautifulSoup

BASE_URL = "https://reserve.lovstmade.com"


def extract_store_urls(html_content: str) -> Dict[str, str]:
    """予約フォームのHTMLコンテンツ内のsubmenuクラスから
    各店舗の予約フォームのURLを取得する

    Params: 任意の予約フォームのHTML
    Returns: { 店舗名: 予約フォームのURL }
    """
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
    """予約している時間 = 予約組数を数える
    Returns: { 日付: 予約数 }
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    reserved_slots = {}

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


async def fetch_store_reservations(
    session: aiohttp.ClientSession,
    store_name: str,
    url: str,
) -> tuple[str, Dict[str, int]]:
    """店舗ごとの予約フォームURLから非同期に予約数をカウントする

    Params:
        session: セッション
        store_name: 店舗名
        url: 予約フォームのURL
    Returns: [ 店舗名, { 日付: 予約数 } ]
    """
    try:
        print(f"fetching {store_name}...")
        async with session.get(BASE_URL + url) as response:
            response.raise_for_status()
            html_content = await response.text()
            store_reservations = count_reserved_slots(html_content)
            return store_name, store_reservations
    except Exception as e:
        print(f"Error fetching URL for {store_name}: {e}")
        return store_name, {}


async def get_all_reservations(initial_url: str) -> Dict[str, Dict[str, int]]:
    """
    任意のLovst予約フォームからすべての店舗の予約フォームURLを収集し、
    それぞれの店舗の予約数をカウントしてdictで返す

    Params: 任意の予約フォームURL
    Returns: { 店舗名: { 日付: 予約数 } }
    """
    # HTMLファイルを読み込む
    print("すべての店舗の予約フォームを収集します")
    response = requests.get(initial_url)

    # 店名とURLのディクショナリを取得
    store_urls = extract_store_urls(response.content)

    # 非同期でURLをスクレイピング
    all_store_reservations = {}
    async with aiohttp.ClientSession() as session:
        # タスクを並列に実行
        tasks = [
            fetch_store_reservations(session, store_name, url)
            for store_name, url in store_urls.items()
        ]

        # すべてのタスクの結果を待つ
        results = await asyncio.gather(*tasks)

        # 結果を辞書に変換
        for store_name, reservations in results:
            all_store_reservations[store_name] = reservations

    return all_store_reservations


def display_reservations(all_reserve: Dict[str, Dict[str, int]]) -> str:
    """結果を整形して表示"""

    str_result = []
    for store, reservations in all_reserve.items():
        str_result.append(f"\n{store}:")
        for date, count in reservations.items():
            str_result.append(f"  {date}: {count} 組が予約しています")

    return "\n".join(str_result)


async def main():
    all_reserve = await get_all_reservations(
        "https://reserve.lovstmade.com/reserve/calendar/115/202/261")
    print("all_reserve:", all_reserve)

    print(display_reservations(all_reserve))


if __name__ == '__main__':
    asyncio.run(main())
