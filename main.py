"""Lovst予約フォームからすべての予約をカウントし、
前回と差分があったらLINEへ投稿

cronなどから一発で終わるように使う
"""
import asyncio
from date_scraper import get_all_reservations  # 予約組数のカウント
import message  # メッセージの整形と管理
from link_forest_calendar import line  # LINE投稿

INIT_URL = "https://reserve.lovstmade.com/reserve/calendar/115/202/261"
TEMPFILE = "/tmp/lovst_reserve.txt"


async def check_reserve_post():
    """
    Throws:
        - ValueError: 前回と同じメッセージなのでLINEに投稿されませんでした。
        - PermissionError: ファイル {path} にアクセス権限がありません。
        - IOError: ファイル操作中にIOエラーが発生しました
        - Exception: 予期せぬエラーが発生しました
    """
    try:
        all_reserve = await get_all_reservations(INIT_URL)
        print(all_reserve)
        # print("デバッグ用 repr:", repr(all_reserve))

        ok = message.is_updated(str(all_reserve), TEMPFILE)
        if not ok:
            raise ValueError("前回と同じメッセージなのでLINEに投稿されませんでした。")

        msg = all_reserve.format_message()
        response = line.post(msg)

        if response.status_code != 200:
            # ステータスコードが200以外ならHTTPErrorをraise
            response.raise_for_status()
    except (ValueError, PermissionError, IOError, Exception) as err:
        print(err)


async def loop():
    while True:
        try:
            check_reserve_post()
        finally:
            await asyncio.sleep(5)


if __name__ == '__main__':
    # 一回で終わらせるとき
    # 無限ループはcronやdaemonなどのLinuxの振る舞いに任せるとき
    asyncio.run(check_reserve_post())

    # 無限ループをこのスクリプトで行うとき
    # asyncio.run(loop())
