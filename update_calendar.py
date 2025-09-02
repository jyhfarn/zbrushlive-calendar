import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# 指定講者名稱關鍵字（新增 Sakaki）
TARGET_NAMES = ["Pavlovich", "Shane Olson", "Narukawa", "Sakaki"]

# 美國西岸時間偏移為 UTC-7
TZ_OFFSET = timedelta(hours=7)

def fetch_schedule():
    url = "https://pixologic.com/zbrushlive/calendar/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []
    # 找所有活動區塊 (h3 標題)
    for header in soup.find_all("h3"):
        text = header.get_text(strip=True)
        if any(name in text for name in TARGET_NAMES):
            # 往下找日期與時間
            date_tag = header.find_next_sibling("p")
            time_tag = date_tag.find_next_sibling("p")
            if date_tag and time_tag:
                # 解析日期 e.g., "Tue, Sep 02"
                date_str = date_tag.get_text(strip=True)
                time_str = time_tag.get_text(strip=True)

                # 將日期解析為 datetime.date (2025 by default)
                dt = datetime.strptime(f"{date_str} 2025", "%a, %b %d %Y")

                # 時間格式如 "4:00 am - 6:00 am"
                m = re.match(r"(\d{1,2}:\d{2})\s*(am|pm)\s*-\s*(\d{1,2}:\d{2})\s*(am|pm)", time_str, re.IGNORECASE)
                if m:
                    start_str, start_ap, end_str, end_ap = m.groups()
                    start_dt = datetime.strptime(start_str, "%I:%M")
                    end_dt = datetime.strptime(end_str, "%I:%M")
                    if start_ap.lower() == "pm" and start_dt.hour != 12:
                        start_dt = start_dt.replace(hour=start_dt.hour + 12)
                    if start_ap.lower() == "am" and start_dt.hour == 12:
                        start_dt = start_dt.replace(hour=0)
                    if end_ap.lower() == "pm" and end_dt.hour != 12:
                        end_dt = end_dt.replace(hour=end_dt.hour + 12)
                    if end_ap.lower() == "am" and end_dt.hour == 12:
                        end_dt = end_dt.replace(hour=0)

                    # 加到同一天
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
