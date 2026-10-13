severity: minor

我的結論是:回滾與資料狀態這個鏡頭下,第一階段(行為不變)沒有 blocker 或 major。下面兩條都是 minor,不擋推。我沒改任何 repo 檔,實驗目錄已刪。

**1. 處置閘印給人照抄的診斷指令,路徑沒加引號**
severity: minor
blocking: 否
引句:「                    _qdiag = f"    診斷:lumos quote-check {rp} --spec {sp} --rule {_qrule}"」
file: `scripts/lumos:26504`
- 這行拿帳上的 `report_path` 和 `snapshot_path` 直接拼成指令。路徑含空白或 `$(…)` 時,照抄貼到終端機就會被 shell 當成別的意思。
- 同一支檔的回放過期提示(`golden 過期` 那段)已對編號與路徑用 `shlex.quote`,且註記寫明是資安席要求。這行漏了。
- 風險很低,路徑來自 repo 內帳本,不是外部輸入。⚠ 我沒找到實際含空白的卷證路徑。

**2. 還原後,舊版 `gov --stats` 會把 `quote-rule:` 擋下事件歸錯格**
severity: minor
blocking: 否
引句:「            _rf = sum(1 for r in _rest if "findings-over-reported" in _d(r))」
file: `scripts/lumos:9534`
- 我在舊版(cb832b56)和新版(211ccd4e)的 clone 上各注入兩筆 `quote-rule:` 事件再跑 `gov --stats`。舊版算出「報告沒正規化 22 / 缺 refuted-set 4」,新版是「21 / 3 / 引句判準 2」。
- 舊版把其中一筆算進「缺 refuted-set」。另一筆的報告路徑含 `report-not-normalized`,就被算進「報告沒正規化」。
- 影響只在統計數字,總數仍是 69,不會崩。但第二階段後若還原,第一條 REVISIT 的人工分類要記得這點。

**逐項答覆**

- **會凍結、補凍、重算判定的入口:**
  - 處置閘 `loop status --disposal`:非綠回 rc1,不放行。
  - `loop next`:非綠不回 converged,只回 `cap-reached` 或 `plant-canary`。
  - `loop replay --freeze`(首次與帶 `--note` 的重凍):只擋 rc2,rc1 照凍。帳上有 5 份 rc1 的判定檔,與計劃和 Issue 所寫的數字一致。
  - `replay_weekly.py` 的補凍:同上,既有設計,計劃已立 Issue〈凍結接受非綠判定〉。
  - `loop replay --golden`:非綠或判準丟例外時回 rc1,報「邏輯漂移」。
  - 我查了 `code-loop pass`、`doctor` 和掛鉤,沒有別的地方會呼叫處置閘。

- **舊帳回放是否一致:**
  - 我在舊版和新版各把全部凍結判定檔回放一遍(新版多一份計劃自己凍的,共 307 份),結果一致。
  - 每份的 rc 都相同,其中 1 份(`消費專案接入靜默失效`)是 rc1。
  - 輸出文字只差一行,281 份多出 `[disposal] 引句判準:legacy(帳上無章)`,其餘位元組相同。
  - `_quote_rows_legacy` 的函式本體和舊 `_quote_rows` 逐行比對,只有 docstring 不同,滿足「一字不改」。

- **新帳(有章)被舊程式讀:**
  - 第一階段所有章都是 `legacy`,舊程式忽略 `quote_rule` 欄,判定與回放都不變。我把一個迴圈的載體列改蓋 `full-span-v1` 後用舊版跑處置閘,輸出與原本相同。
  - 第二階段之後就不成立。我在新版程式上測了兩個例子,舊判準的結果是:
    - 巢狀同型引號會把前綴截成不足 10 字,判失敗,新判準判過。
    - 引句內嵌的標籤會被抽成第二條,可能判失敗,新判準只算一條。
  - `quote-check --compare-rules` 在現有帳上也量到 43 組舊判不過、新判過,21 組反向。計劃〈回退〉只說「第二階段之前才能完整還原第一階段」,與此一致,資料面沒有新的矛盾。

- **還原這個提交後的帳:**
  - 已寫入的 `quote_rule` 欄:舊程式忽略,無影響。
  - `quote-rule:` 事件:留在版控的治理帳,只影響上面第 2 條的統計歸格。

- **處置閘輸出多了行,是否影響解析輸出的腳本:**
  - `governance/autonomous-loop.sh` 只看 `loop status` 的 rc。
  - `replay_weekly.py` 只用 `RED_MARKERS` 這幾個紅標記和 `STALE_MARKER` 比對文字,新增行不含這些字樣。
  - `loop next` 把處置閘輸出吞進緩衝,只在 rc2 時才轉到 stderr。
  - `scripts/` 與 `governance/` 裡沒有腳本在 grep 這幾行。

總結:最高等級 minor,blocking 共 0 條
