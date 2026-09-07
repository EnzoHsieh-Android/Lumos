# r2 intake — 接手視圖(代碼審驗收輪,外家 Codex,2026-09-07)

preflight-4: n/a(代碼審,非設計審)

材料:`r2-snapshot.diff`(r1 五條折入後、相對 HEAD 的 diff)、派工詞 `r2-codex-prompt.txt`(只做兩件事:驗收 r1 五條、只報 blocking 級新發現)、報告本體 `r2-外家codex.md`(從逐字稿最後一個 `severity:` 切出;完整逐字稿 `r2-外家codex-transcript.md`)。
席位宣告 severity: major。驗收:#1–#4 通過、#5 未通過;沒有新的 blocking 級發現。

## 逐條

- **#1–#4 通過**:席位各附 檔:行(輪次邊界測試、候選挑選、外層兜底、反引號路徑測試)。與我自己的翻紅釘結果一致,不重驗。
- **#5 未通過 — 觀察對,折**。席位說:那條「匯入純淨」測試只看 stdout/stderr 與 tmp 留檔,鎖不住「開程序、連網、讀別的檔、寫 tmp 以外的路徑」,跟測試自稱的「不產生任何外部動作」不符。對:原本的測試確實只是弱鎖。折法:探針改用 Python 稽核鉤子(`sys.addaudithook`)全程監看匯入——`open` 只准讀 hook 自己的原始碼與標準庫(其餘路徑或任何寫入模式都違規)、`os.listdir/scandir` 只准標準庫、子程序 / socket / http / urllib / shutil / os 改檔系統呼叫 / ctypes / tempfile / signal / glob 一律違規;違規事件以 JSON 印回,測試斷言為空。翻紅釘四種(print / subprocess.run / open 別的檔 / socket.socket)見下。
  - 席位的另一半「仍會執行可變 hook」是設計事實:不搬 hook 是範圍刀(hook 是 anchor 檔、另案在動它);同信任域的論點寫在計劃天花板。鎖住「執行了也做不了外部動作」是這個範圍內能給的最強答案;r3 請席位只驗這一條。

## 帳
- r2 報告沒有「引句:」行(驗收輪格式我沒要求),`quote-check` 回「抽不到引句」——**驗不了不等於通過**;r2 照記(severity major、findings 1、folded 5),r3 派工詞明寫每條要附引句。
