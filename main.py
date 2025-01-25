"""lovs"""
import asyncio
from date_scraper import get_all_reservations, BASE_URL
from link_forest_calendar.line import line_post, is_message_updated

INIT_URL = "https://reserve.lovstmade.com/reserve/calendar/115/202/261"
TEMPFILE = "/tmp/lovst_reserve.txt"


async def main():
    while True:
        all_reserve = await get_all_reservations(INIT_URL)
        print(all_reserve)
        # print("デバッグ用 repr:", repr(all_reserve))

        is_update = is_message_updated(str(all_reserve), TEMPFILE)
        if not is_update:
            print("メッセージは送信されませんでした")
        response = line_post(f"""
        Lovst Photo Studio 予約フォーム {BASE_URL}
        からモデルオーディション予約組数を集計しました。

        {all_reserve}
        """)
        if response.status_code != 200:
            print("メッセージの送信に失敗しました")
        print("メッセージの送信に成功しました")
        await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
