"""Lovstの予約された枠の数をカウントする"""
import json
from dataclasses import dataclass, field
from typing import Dict
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import datetime

BASE_URL = "https://reserve.lovstmade.com"


@dataclass
class StoreReservations:
    """店舗の予約情報を表現するデータクラス"""
    store_name: str
    reservations: Dict[datetime.date, int] = field(default_factory=dict)

    def __str__(self) -> str:
        """人間が読みやすい文字列表現を生成"""
        result = [f"{self.store_name}:"]
        for date, count in sorted(self.reservations.items()):
            result.append(f"  {date.strftime('%Y-%m-%d')}: {count}")
        return "\n".join(result)

    def __repr__(self) -> str:
        """開発者向けの詳細な文字列表現"""
        reservations = {
            k.strftime('%Y-%m-%d'): v
            for k, v in self.reservations.items()
        }
        return f"StoreReservations(store_name='{self.store_name}', reservations={reservations})"


@dataclass
class AllReservations:
    """すべての店舗の予約情報を保持するデータクラス"""
    stores: Dict[str, StoreReservations] = field(default_factory=dict)

    def __str__(self) -> str:
        """すべての店舗の予約情報を表示"""
        result = []
        for store in self.stores.values():
            result.append(str(store))
            # 店舗ごとの合計予約組数を追加
            total_reservations = sum(store.reservations.values())
            result.append(f"  合計: {total_reservations}")
        return "\n".join(result)

    def __repr__(self) -> str:
        """開発者向けの詳細な文字列表現"""
        return f"AllReservations(stores={list(self.stores.items())})"

    def add_store(self, store_name: str, reservations: Dict[datetime.date,
                                                            int]) -> None:
        """店舗の予約情報を追加"""
        self.stores[store_name] = StoreReservations(store_name, reservations)


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


def count_reserved_slots(html_content: str) -> Dict[datetime.date, int]:
    """予約している時間 = 予約組数を数える
    Returns: { 日付: 予約数 }
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    reserved_slots = {}
    special_days = soup.find_all('a', class_='red-ok')
    for day in special_days:
        date_str = day.get('onclick').split("'")[1]
        date_obj = datetime.datetime.strptime(date_str, '%Y年%m月%d日').date()
        hidden_input = day.find_next('input', type='hidden')
        if hidden_input:
            slot_data = json.loads(hidden_input.get('value'))
            reserved_count = sum(1 for slot in slot_data[0]['comas']
                                 if not slot.get('reservable', False))
            reserved_slots[date_obj] = reserved_count

    return reserved_slots


async def fetch_store_reservations(
    session: aiohttp.ClientSession,
    store_name: str,
    url: str,
) -> tuple[str, Dict[datetime.date, int]]:
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


async def get_all_reservations(initial_url: str) -> AllReservations:
    """
    任意のLovst予約フォームからすべての店舗の予約フォームURLを収集し、
    それぞれの店舗の予約数をカウントして返す
    Params: 任意の予約フォームURL
    Returns: AllReservations オブジェクト
    """
    print("最初の予約フォームを取得しています")
    response = requests.get(initial_url)
    initial_html_content = response.content.decode('utf-8')
    initial_soup = BeautifulSoup(initial_html_content, 'html.parser')
    # 初期の予約フォームからショップ名を取得
    initial_store_name = initial_soup.select_one(
        'div.entry-block h2.shopname').text.strip()
    # 初期の予約フォームから予約組数を取得
    initial_reservations = count_reserved_slots(initial_html_content)
    # すべての予約を入れるコンテナ
    all_reservations = AllReservations()
    all_reservations.add_store(initial_store_name, initial_reservations)
    # 店名とURLのディクショナリを取得
    print("すべての店舗の予約フォームを収集します")
    store_urls = extract_store_urls(response.content)

    # 非同期でURLをスクレイピング
    async with aiohttp.ClientSession() as session:
        # タスクを並列に実行
        tasks = [
            fetch_store_reservations(session, store_name, url)
            for store_name, url in store_urls.items()
        ]
        # すべてのタスクの結果を待つ
        results = await asyncio.gather(*tasks)

        # 結果をAllReservationsに追加
        for store_name, reservations in results:
            all_reservations.add_store(store_name, reservations)

    return all_reservations


async def main():
    all_reserve = await get_all_reservations(
        "https://reserve.lovstmade.com/reserve/calendar/115/202/261")
    # デバッグ用: repr出力
    print("デバッグ用 repr:", repr(all_reserve))
    # 標準出力
    print(all_reserve)


if __name__ == '__main__':
    asyncio.run(main())
