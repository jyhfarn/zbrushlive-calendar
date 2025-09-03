import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# 指定講者名稱關鍵字
TARGET_NAMES = ["Pavlovich", "Shane Olson", "Narukawa", "Sakaki"]

# 美國西岸時間偏移為 UTC-7
TZ_OFFSET = timedelta(hours=7)

def fetch_schedule():
    url = "https://pixologic.com/zbrushlive/calendar/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []
    for header in soup.find_all("h3"):
        text = header.get_text(strip=True)
        if any(name in text for name in TARGET_NAMES):
            # 找日期 <p>（通常包含 Tue, Sep 02 格式）
            date_tag = header.find_next_sibling(
                lambda tag: tag.name == "p" and re.search(r"\w{3},", tag.get_text(strip=True))
            )
            # 找時間 <p>（通常包含 am/pm）
            time_tag = None
            if date_tag:
                time_tag = date_tag.find_next_sibling(
                    lambda tag: tag.name == "p" and re.search(r"\d{1,2}:\d{2}\s*(am|pm)", tag.get_text(strip=True))
                )

            if not date_tag or not time_tag:
                # 如果缺資料就跳過
                continue

            date_str = date_tag.get_text(strip=True)
            time_str = time_tag.get_text(strip=True)

            try:
                # 預設年份 2025
                dt = datetime.strptime(f"{date_str} 2025", "%a, %b %d %Y")
            except ValueError:
                # 格式不符就跳過
                continue

            # 時間格式如 "4:00 am - 6:00 am"
            m = re.match(
                r"(\d{1,2}:\d{2})\s*(am|pm)\s*-\s*(\d{1,2}:\d{2})\s*(am|pm)",
                time_str,
                re.IGNORECASE,
            )
            if not m:
                continue

            start_str, start_ap, end_str, end_ap = m.groups()

            # 處理開始時間
            start_dt = datetime.strptime(start_str, "%I:%M")
            if start_ap.lower() == "pm" and start_dt.hour != 12:
                start_dt = start_dt.replace(hour=start_dt.hour + 12)
            if start_ap.lower() == "am" and start_dt.hour == 12:
                start_dt = start_dt.replace(hour=0)

            # 處理結束時間
            end_dt = datetime.strptime(end_str, "%I:%M")
            if end_ap.lower() == "pm" and end_dt.hour != 12:
                end_dt = end_dt.replace(hour=end_dt.hour + 12)
            if end_ap.lower() == "am" and end_dt.hour == 12:
                end_dt = end_dt.replace(hour=0)

            # 合併成完整 datetime
            start = datetime(dt.year, dt.month, dt.day, start_dt.hour, start_dt.minute)
            end = datetime(dt.year, dt.month, dt.day, end_dt.hour, end_dt.minute)

            events.append({
                "title": "ZBrushLive " + text,
                "start": start,
                "end": end
            })
    return events


def build_ics(events):
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ZBrushLIVE to iCal//EN\n"
    for ev in events:
        # 轉成 UTC
        start_utc = ev["start"] + TZ_OFFSET
        end_utc = ev["end"] + TZ_OFFSET
        ics += (
            "BEGIN:VEVENT\n"
            f"UID:{ev['title'].replace(' ', '')}-{start_utc.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTSTART:{start_utc.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTEND:{end_utc.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"SUMMARY:{ev['title']}\n"
            "END:VEVENT\n"
        )
    ics += "END:VCALENDAR"
    return ics


if __name__ == "__main__":
    evs = fetch_schedule()
    ics_content = build_ics(evs)
    with open("zbrushlive.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)
    print(f"Generated {len(evs)} events → zbrushlive.ics")
