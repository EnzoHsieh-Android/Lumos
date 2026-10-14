severity: major

我沒收到派工詞尾端 hook 附的固定席節點,所以那部分無法逐條判。需要的話請補貼給我。

## 查證結果(先講計劃宣稱成立的部分)

- **S6「舊帳判定不變」成立。**
  - 我掃了 `governance/replay/` 底下全部 321 份凍結判定(含歸檔版)。其中 code 迴圈 220 份。
  - 「判定輪有 major 席、accepted 非空」的只有兩份:`code-待決問題改存開頭欄位` r9(14 條放行)和 `code-審查跑滿回顧` r4(9 條放行)。兩份載體都沒有 `finding_severities`,凍結判定都是 rc=1、fails 為處置集合。
  - 帶 `finding_severities` 的 45 份凍結判定,沒有一份屬於「major 席加非空 accepted」。
  - 現行帳 `docs/.canary-log.jsonl` 裡,code 迴圈、major 輪、有 `finding_severities`、accepted 非空的只有 `code-規格閘半套` r1。它不是最新輪(最新是 r3,accepted 為空),不影響判定。
  - 載體的 `finding_severities` 與 `findings_set` 在帳上沒有子集不齊的情形(寫側 `scripts/lumos:10889` 強制全集)。
  - 我在臨時複本對上述兩份跑了 `loop replay --golden`,結果都是「回放一致」。
- **`_REPLAY_ENGINE_REV` 不 bump,跟前例一致。** 自 08-25 起它從沒因處置閘改動 bump 過。
- **設計審、light、舊 panel 沒被誤套。** 新條件只掛在 `startswith("code-")` 加載體有 `finding_severities`。
- **`_disposal_judge` 的接點大致對,但計劃的描述不準。**
  - file: `scripts/lumos:13657`(`EnzoHsieh-Android/spec-gate-nondo` 分支)。`_disposal_judge` 只是約 15 行的入口,轉手呼叫 `_loop_status_disposal`。
  - 「accepted 必須為空」那段判定仍原封不動留在 `_loop_status_disposal` 的處置集合區塊(該分支約 `27869-27871` 行)。
  - 凍結與回放(該分支 `1126/1140/1268` 行)直接呼叫 `_loop_status_disposal`,不經 `_disposal_judge`。所以改那一段,回放就會同步套到,這點成立。
  - 但「改它抽出後的那段」會讓實作者去 `_disposal_judge` 找,其實沒有新位置。

## Findings

### 1. 數量檢查加降級清單,擋不住「把 major 標成 minor 放行」

引句:「再加上載體降級清單的條數」

severity: major
blocking: 是

- **分母太鬆。**
  - 分母算的是同輪所有席報告裡的 minor 與 clean 宣告行,包含沒存活、被折掉的那些。
  - 我用現行帳重算了 78 個「major 輪加有 `finding_severities`」的輪次。
  - 例如 `code-probe-postreview-dispatch-ledger` r2:分母 12,逐條標 minor 的只有 4,餘額 8。
  - 只要報告裡有幾條 minor,編排者就能把同數量的真 major 標成 minor 放行,檢查仍然判過。
- **降級清單等於免費增加分母。**
  - 計劃寫的檢查只有:id 在 `findings_set` 內、逐條嚴重度為 minor 或 clean、理由至少 4 字含實字、intake 同一列有該 id 加 HIT/MISS/重現/採信字樣。
  - 沒有檢查「原報確實是 major」,也沒有 file:line 反證。
  - 沒要求被降級的 id 落在 accepted。落在 folded 的 id 也能白白墊高分母。
  - 計劃寫的是「辯方附證據降級」,機械上只驗字串。要放水的人記幾條降級就能無限放大分母。
- **應該是:**
  - 分母只算存活的 minor,不含已被折掉或重現不到的。
  - 或改成檢查 major 條數守恆,也就是報告宣告的 major 數必須能在逐條嚴重度裡對上。
  - 降級至少要比照現有 `--refute-verdict evidence` 的反證要求(file:line),並要求被降級的 id 落在 accepted。
- **與現有機制重疊。** 現有 `--refute-verdict evidence` 已經是「辯方拿反證降級,去向必是放行」(`scripts/lumos:10911-10927`),計劃的 PRIOR-ART 說沿用,卻另開 `--downgraded-set`,沒交代兩者關係。

### 2. 推翻舊裁定 d2 卻沒排進收尾動作

引句:「major 以上照舊一律折,minor 可以附理由放行」

severity: major
⚠(判不準是 major 還是 minor,偏 major)
blocking: 是

- **d2 與它的連動。** d2 是 `Projects/probe輪退場_計劃` frontmatter 的 decisions 紀錄,內文是「輪內任一席 ≥ major 則 accepted 必空」。它同時是 d4「防線不降級」的地基。
- **計劃只在 WHY 提了 d2。** 範圍與做法裡沒有 `lumos decision-add` 翻案或標 superseded 的步驟。
- **造成的後果。** 專案 CLAUDE.md 規定,有結構的決策紀錄可以挑戰程式碼。上線後 d2 仍然有效,而程式碼違反它,下一個 session 會依 d2 把閘改回去。
- **既有測試。** `t_panel_probe_retired`(`scripts/test_lumos.py` 約 9042-9053 行)要求 code-* 加 major 加 accepted 時,輸出含「major 一律折」。沒帶逐條嚴重度的分支必須保留這句訊息,計劃沒提。
- **應該是:** 做法裡加一步「d2 以 `decision-add` 翻案並寫明新範圍(minor 可放行)」,並註明舊訊息字串要保留,或同步改測試。

### 3. 手冊與筆記同步清單不全

引句:「改寫成新規則一句,同一步」

severity: minor
blocking: 否

計劃只列 `SKILL.md` 第 7 步和 `reference.md` 新增一段。仍寫著舊規則的地方還有:

- `skills/lumos-code-loop/reference.md:596`(第 7 步的重複版,寫「★code 迴圈輪內任一席 severity ≥ major 則 accepted 必空★」)
- `skills/lumos-project-notes/commands/06-代碼審與推送.md:41`
- `docs/lumos-toolchain-knowledge/Systems/design-loop.md:55`(KEY「code 迴圈輪級加嚴(major 席→accepted 必空,d2)」)
- 同一檔裡的 `Systems/convergence-evidence-gate.md:69`

S7 是 manual 條款,抓不到這些殘留。

### 4. 回退段沒講凍結判定怎麼處理

引句:「改回後,上線期間在 major 輪放行過 minor 的迴圈會判不過」

severity: minor
blocking: 否

- 上線後凍結的判定,若屬於 major 輪放行 minor 的新形狀(rc=0),回退時回放會變成「邏輯漂移」紅燈。
- 計劃在 S6 沒 bump `_REPLAY_ENGINE_REV` 的前提下沒提這點,建議在回退段加一句處理方式(重凍或標記)。

### 5. `finding_severities` 其他讀取點的行為變化沒列出

引句:「被放行的 minor 其實是 major、事後以逃逸記帳」

severity: minor
blocking: 否

計劃說「沿用不另做」,但放行 minor 之後 `--finding-severity` 會變成常態,下面兩處會跟著變:

- **逃逸自動記**(`scripts/lumos:11130`)按逐條嚴重度判 `_hit`。被降級成 minor 的原 major 不會留下逃逸紀錄,所以 RETIRE-IF 的「累計 3 筆」會看不到降級放水,只能靠人事後補記。
- **fix-check 同類重複**(`scripts/lumos:14116`):帶逐條嚴重度時,折入的 minor 不再觸發「要寫 prior」。過去沒帶時,major 輪的每條折入都以輪最高值算 major。這是行為放寬,建議計劃明講。

### 6. 分母定義與邊界含糊

引句:「同一席同一份報告只算一次」

severity: minor
blocking: 否

- **「各席最新一筆帳」與「鍵 (auditor, report_sha256)」互相衝突。** 同一席改過報告(例如收貨時正規化)後有兩個 sha,會被算兩次,分母膨脹。
- **讀報告的順序。** 數量檢查在處置集合區塊(②)讀報告,留痕 sha 重驗在 ③。篡改的報告會先被拿來算數,最後才被 ③ 擋下。
- **缺鍵未定義。** 計劃沒定義 accepted id 不在 `finding_severities` 時怎麼判(應判不過)。

---

總結:最高嚴重度 major,blocking 2 條(finding 1、2),minor 4 條。

臨時複本在 `/tmp/lumos-seat-work/代碼審minor解綁/相容回放-sonnet/`,含 `clone/`、`nondo-lumos.py`、三支掃描腳本和 `out.txt`,請編排者刪除。
