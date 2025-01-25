import asyncio
from date_scraper import get_all_reservations
from link_forest_calendar.line import line_post


async def main():
    all_reserve = await get_all_reservations(
        "https://reserve.lovstmade.com/reserve/calendar/115/202/261")

    debug = False

    if debug:
        print("デバッグ用 repr:", repr(all_reserve))

    # 標準出力
    print(all_reserve)
    line_post(all_reserve)


asyncio.run(main())
