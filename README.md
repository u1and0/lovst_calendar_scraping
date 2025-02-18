Lovstモデルオーディション応募フォームから、予約された枠の数をカウントする。

例えば[Lovst勝どき店モデルオーディション応募フォーム](https://reserve.lovstmade.com/reserve/calendar/115/202/261)

以下のような形式でLINEに投稿される
ただし、前回との投稿差分があったときのみ。
前回との投稿は `/tmp/lovst_reserve.txt` に保存される。

```
勝どきリバーサイド:
  2025-02-09: 12
  2025-02-20: 3
  合計: 15
ガーデン西葛西:
  2025-02-04: 11
  2025-02-15: 10
  合計: 21
マリンアンドウォークヨコハマ:
  2025-02-01: 18
  2025-02-13: 10
  2025-02-23: 21
  合計: 49
たまプラーザ:
  2025-02-08: 18
  2025-02-25: 5
  合計: 23
新宿高島屋:
  2025-02-04: 19
  2025-02-22: 20
  合計: 39
池袋東武:
  2025-02-08: 24
  2025-02-15: 26
  2025-02-25: 13
  合計: 63
武蔵小杉:
  2025-02-04: 13
  2025-02-15: 12
  合計: 25
亀戸:
  2025-02-05: 13
  2025-02-22: 14
  合計: 27
ららぽーと福岡:
  2025-02-02: 12
  2025-02-13: 4
  2025-02-22: 12
  合計: 28
```

# Setup

```
$ git clone https://github.com/u1and0/lovst_calendar_scraping
$ git clone https://github.com/u1and0/link_forest_calendar
```

# Requirements
requests, BeautifulSoup4, aio-httpが必要です。
Ubuntuの場合以下のコマンドでインストールします。

```
$ apt install python3-bs4 python3-requests python3-aiohttp
```

# Run

```
$ export PYTHONPATH=/home/your_name/your_python_path
$ python lovst_calendar_scraping/main.py
```

