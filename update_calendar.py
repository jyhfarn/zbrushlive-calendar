import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

TARGET_NAMES = ["Pavlovich", "Shane Olson", "Narukawa", "Sakaki"]
TZ_OFFSET = timedelta(hours=7)  # PDT → UTC

def fetch_schedule():
    url = "https://pixologic.com/zbrushlive/calendar/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    events = []
    for header in soup.find_all("h3"):
        title_text = header.get_text(strip=True)
        if not any(name in title_text for name in TARGET_NAMES):
            continue

        # 找到日期與時間：定位 header 下一行文字
        next_sib = header.find_next_sibling(text=True)
        date_str, time_str = None, None

        while next_sib:
            line = next_sib.strip()
            if re.match(r"\w{3},\s*\w{3}\s*\d{1,2}", line):  # e.g., Fri, Sep 05
                date_str = line
            elif re.search(r"\d{1,2}:\d{2}\s*(am|pm)\s*-\s*\d{1,2}:\d{2}\s*(am|pm)", line, re.IGNORECASE):
                time_str = line
                break
            next_sib = next_sib.find_next_sibling(text=True)

        if not date_str or not time_str:
            print(f"⚠️ Skipped (no date/time found): {title_text}")
            continue

        try:
            dt = datetime.strptime(f"{date_str} 2025", "%a, %b %d %Y")
        except ValueError:
            print(f"⚠️ Date parse failed: {date_str}")
            continue

        m = re.match(
            r"(\d{1,2}:\d{2})\s*(am|pm)\s*-\s*(\d{1,2}:\d{2})\s*(am|pm)",
            time_str,
            re.IGNORECASE,
        )
        if not m:
            print(f"⚠️ Time parse failed: {time_str}")
            continue
        start_str, start_ap, end_str, end_ap = m.groups()

        def parse_component(timestr, ap):
            dtc = datetime.strptime(timestr, "%I:%M")
            h = dtc.hour
            if ap.lower() == "pm" and h != 12:
                h += 12
            if ap.lower() == "am" and h == 12:
                h = 0
            return h, dtc.minute

        sh, sm = parse_component(start_str, start_ap)
        eh, em = parse_component(end_str, end_ap)
        start = datetime(dt.year, dt.month, dt.day, sh, sm)
        end = datetime(dt.year, dt.month, dt.day, eh, em)

        print(f"✔ Found: {title_text} | {date_str} | {time_str}")
        events.append({
            "title": "ZBrushLive " + title_text,
            "start": start,
            "end": end
        })
    return events

def build_ics(events):
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ZBrushLIVE to iCal//EN\n"
    for ev in events:
        s = ev["start"] + TZ_OFFSET
        e = ev["end"] + TZ_OFFSET
        ics += (
            "BEGIN:VEVENT\n"
            f"UID:{ev['title'].replace(' ', '')}-{s.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTSTART:{s.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"DTEND:{e.strftime('%Y%m%dT%H%M%SZ')}\n"
            f"SUMMARY:{ev['title']}\n"
            "END:VEVENT\n"
        )
    ics += "END:VCALENDAR"
    return ics

if __name__ == "__main__":
    evs = fetch_schedule()
    print(f"Total events: {len(evs)}")
    for ev in evs:
        print(f"- {ev['title']} @ {ev['start']}–{ev['end']}")
    with open("zbrushlive.ics", "w", encoding="utf-8") as f:
        f.write(build_ics(evs))
    print("ICS file generated.")
