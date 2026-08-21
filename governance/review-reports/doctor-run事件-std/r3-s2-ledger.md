# doctor-run事件-std r3 独立复核(s2,LENS: ledger semantics)

角色:外部第三方,對抗性但憑事實。標的:`/tmp/doctor-run事件-std-r3.md`(第二輪連續 delta,K=2)。

## 結論先講

r3 文件本身邏輯自洽,r1(std/light)兩輪抓到的洞都已在文件裡妥善收斂(note vs detail 欄位名、過濾不可
落在 `ded` 上這條核心規則都寫對了)。但**用同一條「不可動 `ded`」規則去反推 `cmd_gov` 全函式**時,發現
文件漏看了 `ded` 的另一個消費者——**恰好是 std r1 s1 抓到的同一種失效模式,換了一個發生點**。判定:
發現 1 筆 major(新,本輪),另附 1 筆與本案無關但同 lens 命中的既存潛伏 bug(僅供留痕,不計入 r3 判定)。

## Finding 1 — major(新發現,本輪)

**現象**:`cmd_gov` 尾端的總筆數列 `print(f"\n{len(ded)} 筆(近 {since_days} 天)")`
(scripts/lumos:3138)在 `--full` 與預設(非 `--full`)兩種模式下**都會執行、都讀未經過濾的 `ded`**。
r3 設計要求「非 `--full` 的顯示迴圈」對 `gate == "doctor-run"` 的列 `continue`(只動印出動作,不動
`ded`,理由是保護 `_render_gov_stats`)——但這條規則只顧到了 `_render_gov_stats` 這一個消費者,沒發現
`ded` 還有第二個消費者就在同一函式裡:這行尾端總數。一旦照設計把 doctor-run 列從預設視圖的逐行印出
迴圈裡拿掉,這行總數依然把 doctor-run 列算進去——**預設 `gov` 畫面會出現「印出的行數」與「尾端寫的
筆數」對不上**。

引句(來自 r3 文件,即被本發現戳破覆蓋範圍的那句):「過濾只作用在顯示迴圈的印出動作」

**實測驗證**(在乾淨 vault 灌入 1 筆真實 code-loop 事件 + 2 筆模擬 doctor-run 事件,跑今日未改版的
`gov`,證明「總數行目前忠實反映印出行數」——一旦照 r3 設計只在印出迴圈加 `continue`,這個一致性就會
被打破):

```
$ python3 scripts/lumos --vault docs/kg gov          # 預設(非 --full)
2026-08-21 [code-loop/passed/軟] -
2026-08-21 [doctor-run/ran/軟] -  issues=0 gates=0
2026-08-21 [doctor-run/ran/軟] -  issues=0 gates=0

3 筆(近 90 天)
```
今天這 3 行全部有印出來,所以「3 筆」與畫面吻合。但依 r3 設計,一旦在預設模式的印出迴圈里加上
`if r["gate"] == "doctor-run": continue`,上面兩行 doctor-run 就會從畫面消失,只剩 1 行
`[code-loop/passed/軟]`,而 3138 行的 `len(ded)` **仍是 3**——尾端變成「1 行印出內容,卻寫著 3 筆」,
對讀帳的人是一個新的誤導點,而且恰好是本案自己在乎的那類問題(帳本顯示與底層筆數對不上)。

**為什麼是 major**:直接誤導 `gov` 的預設輸出——這正是治理帳日常最常被人讀的畫面(非 `--full`、非
`--stats`)。且 r3 規劃的測試 3(`t_gov_hides_run_marker_unless_full`)只斷言「預設畫面不印
doctor-run 字串」與「`--stats` 去重筆數 == 2」,**不會斷「尾端筆數 == 實際印出行數」**,所以這個洞
會直接滑過 r3 自己規劃的回歸測試,原地成為新的假綠。

**建議**(僅供落地時參考,非本輪判定範圍):尾端總數行應改用「印出迴圈實際印出的行數」而非
`len(ded)`,或在非 `--full` 模式下對這一行也扣掉 doctor-run 筆數;`--full`/`--stats` 模式維持用
`len(ded)` 不變(那兩處本來就該與 doctor-run 一致)。

## 附帶發現(不計入 r3 判定,與本案無關,同 lens 命中,建議另開留痕)

`_codeloop_gov_log`(scripts/lumos:14038)寫入 `.governance-log.jsonl` 時用的原始欄位是
`"detail": note`,但 `cmd_gov` 對 `.governance-log.jsonl` 的 mapper(scripts/lumos:2993)讀的是
`d.get("note", "")`——兩邊欄位名不一致,導致 code-loop pass/skip 的 `--note` 內容**從來沒有**在
`gov`/`gov --full` 裡顯示過(恆空字串)。

引句(mapper 端,顯示這條 bug 的真身):「"detail": d.get("note", "")」

實測(乾淨 repo,`code-loop pass --note "MYUNIQUENOTE123"`,再 `gov --full`):
```
2026-08-21 [code-loop/passed/軟] -
```
`MYUNIQUENOTE123` 完全沒出現。這件事**不是 r3 引入的、也不在 r3 的改動範圍內**(r3 自己新增的
doctor-run 事件正確用了 `note`,與 mapper 一致,沒有這個問題)。之所以列在這裡,是因為本輪 lens
(ledger semantics)與審查範圍(cmd_gov mapper、note/detail 欄位語意)直接命中了它,交接方便人判斷
要不要另開 `Issues/` 節點追。

## 覆核清單(逐項核對 r3 聲稱)

- 顯示迴圈過濾不落在 `ded`(保護 `_render_gov_stats`):文件的核心主張本身成立,`_render_gov_stats`
  (scripts/lumos:2910)確實共用 `ded`,若濾了 `ded` 會把 doctor-run 從 `--stats` 分母一併濾掉——
  這條 r1 抓到的洞,r3 的因應寫法是對的。唯獨遺漏了同函式裡的第二個 `ded` 消費者(見 Finding 1)。
- `note` 欄位名與 mapper 一致:核對 scripts/lumos:2993 `"detail": d.get("note", "")`——r3 設計用
  `"note"` 是對的。
- dedup 鍵含 commit、nodes 恆空:核對 scripts/lumos:3020 `k = (r["commit"], frozenset(r["nodes"]),
  r["gate"], r["kind"], r.get("token", ""))`——兩次不同 commit 的 doctor-run 不會被去重,`--stats`
  的去重筆數 == 2 這個斷言是站得住的。
- `_KNOWN_GATES` 漂移測試(t_gov_stats_gate_drift,scripts/test_lumos.py:3047)只認字面值
  `"gate": "doctor-run"`,只要實作照文件寫死字面值(不要用 f-string/變數拼 gate 名),就不會撞上
  「動態 gate 寫點恰為 1 處」那條釘子——文件裡沒明講「必須是字面值」這個前提,但這是實作層的事,
  不算文件缺陷。
- CI workflow(.github/workflows/ci.yml:25 `doctor --ci`)只在 ephemeral checkout 裡寫,沒有任何
  commit/push 步驟把 `.governance-log.jsonl` 帶出去——本案不會改變 CI 行為,範圍刀寫的「不碰」成立。
- `_BOOKKEEPING_FILES`(scripts/lumos:10299)已含 `docs/.governance-log.jsonl`,pitfalls --diff 掃描
  與 code-loop pass 的簿記白名單豁免都已涵蓋這支檔案,doctor-run 只是多寫幾行,不會新增風險面。

## 一行計數

blocker=0 / major=1 / minor=0(另有 1 筆與 r3 無關的既存 bug,未計入上列計數)
