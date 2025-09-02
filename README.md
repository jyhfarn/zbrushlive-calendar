# ZBrushLive iCal Feeds

自動從 [ZBrushLIVE Calendar](https://pixologic.com/zbrushlive/calendar/) 抓取指定藝術家的直播排程，轉換成 `.ics` 檔案，方便匯入行事曆。

目前支援：
- Pavlovich Workshop
- Shane Olson
- Daisuke Narukawa
- Sakaki

ICS 會透過 GitHub Actions 自動更新。

---

## 📥 訂閱方式

你可以直接訂閱 `.ics` 網址（會自動更新），或是下載匯入一次。

### 1. Apple Calendar (macOS / iOS)
1. 複製以下網址：https://yourname.github.io/zbrushlive-ics/zbrushlive.ics
2. 打開 **行事曆 (Calendar)**。
3. 在上方選單選擇 **檔案 > 新增行事曆訂閱…**。
4. 貼上網址，點選「訂閱」。
5. 建議設定「自動更新」為每天或每週。

### 2. Google Calendar
1. 打開 [Google Calendar](https://calendar.google.com/)。
2. 在左側 **其他行事曆 > 加號 > 從網址新增**。
3. 貼上 `.ics` 訂閱網址：https://yourname.github.io/zbrushlive-ics/zbrushlive.ics
4. 點選「新增行事曆」。

---

## ⚙️ 自動更新

本專案使用 **GitHub Actions**，每天自動抓取 ZBrushLIVE 網站最新排程並更新 `zbrushlive.ics`。

更新流程：
1. `update_calendar.py` 抓取資料並生成 `.ics`。
2. GitHub Actions 定期執行並 commit 更新檔案。
3. `.ics` 透過 GitHub Pages 提供下載 / 訂閱。

---

## 📌 備註

- 時區：已轉換為 **UTC**，Apple Calendar / Google Calendar 會自動換算成你的本地時間。
- 如果 ZBrushLIVE 網站更新格式改變，可能需要調整爬蟲程式。

