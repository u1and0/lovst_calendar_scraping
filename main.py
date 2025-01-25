import asyncio
from date_scraper import get_all_reservations, BASE_URL
from link_forest_calendar.line import line_post


async def main():
    all_reserve = await get_all_reservations(
        "https://reserve.lovstmade.com/reserve/calendar/115/202/261")
    # print("デバッグ用 repr:", repr(all_reserve))

    print(all_reserve)
    message = f"""
Lovst Photo Studio 予約フォーム {BASE_URL}
からモデルオーディション予約組数を集計しました。

{all_reserve}
"""
    line_post(message)


asyncio.run(main())
