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
        if not any(name in text for name in TARGET_NAMES):
            continue

        # 找到 header 後，掃描接下來的 <p> 標籤
        p_tags = []
        nxt = header.find_next_sibling()
        while nxt and nxt.name == "p":
            p_tags.append(nxt)
            nxt = nxt.find_next_sibling()

        # 從 p_tags 裡找日期和時間
        date_tag = None
        time_tag = None
        for p in p_tags:
            t = p.get_text(strip=True)
            if re.search(r"\w{3},\s*\w{3}\s*\d{1,2}", t):  # Tue, Sep 02
                date_tag = p
            elif re.search(r"\d{1,2}:\d{2}\s*(am|pm).+-", t, re.IGNORECASE):  # 4:00 pm - 6:00 pm
                time_tag = p

        if not date_tag or not time_tag:
            print(f"⚠️ Skipped (missing date/time) → {text}")
            continue

        date_str = date_tag.get_text(strip=True)
        time_str = time_tag.get_text(strip=True)

        try:
            dt = datetime.strptime(f"{date_str} 2025", "%a, %b %d %Y")
        except ValueError:
            print(f"⚠️ Date parse failed: {date_str}")
            continue

        # 解析時間區段
        m = re.match(
            r"(\d{1,2}:\d{2})\s*(am|pm)\s*-\s*(\d{1,2}:\d{2})\s*(am|pm)",
            time_str,
            re.IGNORECASE,
        )
        if not m:
            print(f"⚠️ Time parse failed: {time_str}")
            continue

        start_str, start_ap, end_str, end_ap = m.groups()

        def parse_time(timestr, ap):
            dt = datetime.strptime(timestr, "%I:%M")
            if ap.lower() == "pm" and dt.hour != 12:
                dt = dt.replace(hour=dt.hour + 12)
            if ap.lower() == "am" and dt.hour == 12:
                dt = dt.replace(hour=0)
            return dt

        start_dt = parse_time(start_str, start_ap)
        end_dt = parse_time(end_str, end_ap)

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
    print(f"✅ Found {len(evs)} events")
    for e in evs:
        print(f" - {e['title']} {e['start']} → {e['end']}")
    ics_content = build_ics(evs)
    with open("zbrushlive.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)
    print(f"📅 Saved to zbrushlive.ics")
