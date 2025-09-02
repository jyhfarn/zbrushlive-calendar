import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def fetch_schedule():
    url = "https://pixologic.com/zbrushlive/calendar/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # TODO: 解析 ZBrushLIVE 的表格
    # 範例結構：找出含講者名字的 <td> 或 <a>
    events = []
    for ev in soup.find_all("div", class_="eventBox"):
        title = ev.get_text(strip=True)
        if any(name in title for name in ["Pavlovich", "Shane Olson", "Narukawa"]):
            # TODO: 抓日期 & 時間
            events.append({
                "title": "ZBrushLive " + title,
                "start": datetime.utcnow(),  # TODO: 轉換時區
                "end": datetime.utcnow() + timedelta(hours=2)
            })

    return events

def build_ics(events):
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ZBrushLIVE to iCal//EN\n"
    for i, ev in enumerate(events):
        ics += f"""BEGIN:VEVENT
UID:{i}@zbrushlive
DTSTAMP:{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{ev['start'].strftime("%Y%m%dT%H%M%SZ")}
DTEND:{ev['end'].strftime("%Y%m%dT%H%M%SZ")}
SUMMARY:{ev['title']}
END:VEVENT
"""
    ics += "END:VCALENDAR"
    return ics

if __name__ == "__main__":
    events = fetch_schedule()
    ics_content = build_ics(events)
    with open("zbrushlive.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)
