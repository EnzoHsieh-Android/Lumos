severity: major

## F1 `superseded_by` 為空鍵或區塊清單時,`lumos rejections` 整支崩潰(修補新引入)
severity: major
blocking: 是
引句:「"content": first_line(str(d.get("content", "")), 160), "context": d.get("superseded_by")})」
佐證:file: `scripts/lumos:18124`(`parse_decisions` 遇到「鍵後面沒值」就把 `cur[key]` 存成 list)
佐證:file: `scripts/lumos:18219`、`scripts/lumos:18223`(context 原樣放進去重用的 set 鍵)
歸因:有證據的修復回歸。修前 c728cf14 的 context 是 `"→ " + str(...)` 字串,也沒有去重;09ffec28 為了去重與 `null` 才改成原始值。

失敗場景:
1. 某篇決策寫成 `valid: false` 後接一行空的 `superseded_by:`(後面沒東西,或接 `- d2` 的區塊清單)。`parse_decisions` 在 `val == ""` 的分支把它存成 `[]` 或 `['d2','d3']`。
2. `_superseded_decisions` 收進這條決策,`_rejections_collect` 把 `d.get("superseded_by")` 原樣放進 `context`。
3. 去重那段 `key = (x["node"], x["kind"], x["content"], x["context"])` 做 `key not in seen`,拋出 `TypeError: cannot use 'tuple' as a set element (unhashable type: 'list')`。
4. 結果是文字模式和 `--json` 都 rc=1 並印 traceback,整張清單出不來。`decisions --superseded` 對同一份資料正常(印 `→ []`)。
5. 規格閘的安全網有接住(印「收集失敗…略過」、rc 0),但 `lumos rejections` 本身不能用。
6. 筆記裡「沒寫是 null」的說法,對空鍵的情況也不成立。

重現(最小,探針腳本 `/tmp/lumos-seat-work/code-否決提案收齊查重/正確性r2-sonnet/probe3.py`;vault 只有一篇含 `valid: false` 與空 `superseded_by:` 的計劃):
- 修後 09ffec28:`rejections` 與 `rejections --json` 都 rc=1 並印 `TypeError ... unhashable type: 'list'`;`decisions --superseded` 印 `甲_計劃: 舊做法 → []`;`spec-gate --no-run` 印 `[spec-gate] 舊否決: —(收集失敗:cannot use 'tuple' as a set element (unhashable type: 'list');略過)`,rc 0。
- 修前 c728cf14:`rejections` rc=0,印出 `Projects/甲_計劃: 舊做法 → []`,`--json` 正常。
- 區塊清單寫法(`probe2.py`)結果相同。
- 這種寫法在真圖譜(768 篇)裡是 0 筆,實際觸發靠手寫空鍵。`decision-supersede` 寫的是純量。
- 修法:context 轉成 `str(...)`,沒有或空值時用 `None`。

## F2 引號排除與「推翻在前」兩條規則,在 120 字窗口邊界與混合句會失準
severity: minor
blocking: 否
引句:「c = _REJ_QUOTED_RE.sub("", str(d.get("content", ""))[:120])」
引句:「return bool(nogo) and not (rev and rev.start() < nogo.start())」
佐證:file: `scripts/lumos:18187`
歸因:前半(引號跨 120 字界線)是有證據的原有漏查:修前整段不扣引號,修後仍收,沒有改善也沒有惡化。後半(混合句)是有證據的修復回歸:修前收,修後不收。

失敗場景:
1. 先切前 120 字、再扣引號。`"a"*100 + "「不做戊" + "b"*30 + "」"` 的引號在第 120 字之後才收尾,切完變成未閉合,「不做」被當成真否決。修前、修後都列出 `#A5`。
2. `「不做「X」不做」庚` 這種巢狀引號,regex 只吃到第一個 `」`,殘留的「不做」被收。修前、修後都列出 `#A7`。
3. 推翻字眼只要早於不做字眼就整條排除,不看兩者是不是講同一件事。`推翻了 d3 的舊方案;卯方案停案` 是推翻一件、停掉另一件,修前收(`#A17`),修後漏掉。`翻案後改採子:不做丑`(`#A15`)也一樣漏掉。
4. 真圖譜上這些情況都是 0 筆:全庫只有 1 筆被「推翻在前」排除(`Projects/評測尺翻案_計劃.md#d1`),它確實是在推翻舊的「刻意不做」,排除正確。先扣引號再切 120 字,真圖譜結果也沒有差別。

## F3 驗收條款 S4 的措辭與修後行為不一致
severity: minor
blocking: 否
引句:「回傳碼與判定 應 跟沒有這行時一樣;收集出錯時 應 略過這行 [test:t_spec_gate_rejections_hint]」
佐證:file: `scripts/lumos:7275`、`scripts/lumos:7280`
歸因:有證據的修復回歸:修補把「略過這行」改成「改印一行略過原因」,但計劃條款沒跟著改。

失敗場景:
1. 條款 S4 要求收集出錯時「略過這行」。
2. 實作與綁定測試的第③項要的是印出 `[spec-gate] 舊否決: —(收集失敗:…;略過)`。
3. 條款句和它綁的測試描述的是兩種行為。
4. `規格閘.md` 與 `lumos-cli-read.md` 已寫「改印一行略過原因」,只有條款沒改。
5. 重跑規格閘時要改條款指紋,所以只是文字不一致,不影響功能。

## 三問與同一案例證據

**① 原問題的修復效果(修前 c728cf14、修後 09ffec28,同一佈景 `_rej_vault()`,跑兩版的 `scripts/lumos`)**
- 摘要與正文同一行 WHY 只收一次:修前列 7 條(乙、丙各重複一次),修後 5 條。
- 推翻/翻案在不做之前、引號內不做:修前收進 `d9` 與 `d10`,修後不收;`d13`(先停案、後提推翻)修後照收。
- 無編號的決策:修前印 `Projects/甲_計劃#:`,修後 `Projects/甲_計劃.md: 不做午方案`。
- `--json`:修前鍵為 `source`(不帶 .md),context 為 `→ d2`;修後鍵為 `node`(帶 .md),context 為 `d2`、沒寫是 null。
- 空圖譜:修前印清單標題加 `共 0 筆。按概念…`,修後只印 `無舊否決(共 0 筆)`。
- 把修後的測試檔放到修前的 `scripts/lumos`(`mix/`)跑 `-k rejections`:10 條斷言轉紅,其中兩個測試各有 4 到 5 條(`t_rejections_collects_sources` 與 `t_rejections_json_and_empty`),`t_spec_gate_rejections_hint` 的③也紅。這證明新測試對症。
- `t_docs_command_count` 在修前紅(兩份文件寫 84、實際 85),修後綠。
- 組 1 的「每個關鍵字單獨一筆」:`d2` 停案、`d5` 否決、`d6` 不採、`d7` 不做,以及 120 字內外各一筆(`d7` 收、`d8` 不收),修後輸出都符合。
- 作廢、否決與 wontfix 各篇都列出。

**② 修補處的正常、錯誤與相鄰路徑**
- 正常路徑成立:
  - 修後 `-k rejections`、`-k decisions_superseded`、`-k docs_`、`-k spec_gate_` 全綠(42、2、76、102 項)。
  - `lumos decisions --superseded` 在修前、修後對同一佈景輸出一字不差:`甲_計劃: 舊做法戊 → d2`、`不做舊方案壬 → d2`、`舊的申 → ?`;沒有時印「無被推翻的決策」。
  - 真圖譜上被翻案決策共 44 筆,與 `decisions --superseded` 的 44 行一致,去重沒有吃掉東西。
  - 規格閘的 rc 與判定不變,`--no-run` 也印筆數。
- 錯誤路徑:
  - 收集丟例外時,規格閘印略過原因、rc 0,這是我在 F1 的探針實測。
  - 無 frontmatter、frontmatter 未閉合、CRLF、非 UTF-8、`Superseded` 大小寫與加引號,全都不崩。
  - 效能壓力:3001 篇、每篇 30 個決策加 50 條 WHY(24 萬條),`rejections` 約 4 秒;單行有 5 萬個 `[不選:a` 也未卡住。真圖譜收集本身約 0.17 秒。
- 相鄰路徑問題:`superseded_by` 為空或清單時崩潰,見 F1。`--push-check` 走另一條路徑,不經過 `_spec_gate_front`,pre-push 解析不受影響。

**③ 新發現的同一案例在修前、修後各是什麼**
- F1:修前 rc 0,修後 rc 1 並印 traceback,屬回歸。
- F2:`#A5`、`#A7` 修前、修後都收,是原有漏查;`#A15`、`#A17` 修前收、修後漏,是修復造成的行為變化。
- F3:修前 S4 與行為一致,修後不一致。

**未驗範圍**
- 沒跑全套(約 8 分鐘)。
- 沒驗 `ARCHITECTURE.md` 的 mermaid 圖是否正常渲染。

## 本案特定鏡頭(真圖譜上跑 `lumos rejections`)
- **有沒有漏掉真否決:** 沒有。全庫只有 1 筆被「推翻在前」排除,它確實是在推翻舊否決。
- **「前 120 字」之外漏掉的 4 筆**,實測不是新的否決:
  - `Projects/design-loop提效_計劃.md#d1`(跨家族否決於 v4 解除)
  - `Projects/狀態標籤同步守衛_計劃.md#d1`(整批砍仍不做,但改成可行)
  - `Projects/評測尺翻案_計劃.md#d1`(推翻刻意不做)
  - `Systems/slim-gen-生成器.md#d2`(已不採用)
- **仍誤收的非否決**(計劃已承認「關鍵字判,可能誤收」,所以不單獨列 finding):
  - `Systems/cross-family-audit.md#d2`:「disputed=否決不放行」是判定狀態名。
  - `Systems/design-loop.md#d1`:「判決不採信」中的「不採」。
  - `Systems/design-loop.md#d11`:「否決席」是席位名。
  - `Projects/自足性審計閉環_計劃.md#d4`:「可否決」。
  - `Projects/主session鏡頭利用率_計劃.md#d1`:「(必答/不做)」是選項。
  - `Projects/design-loop重設計.md#d4`:「退出一票否決」。
- **S5 手動驗收成立:** 輸出第 156 行有 `Systems/開發工作流總覽.md#d1: 計劃節點不做模板化盤問…`。

## 圖譜固定席判定
- `lumos-cli-read`(search 預設排除 superseded 的 ★INVARIANT★):不影響。`rejections` 是新增的只讀指令,沒碰 search 的濾網。
- `design-loop`(處置閘第五步、審材需為 .md 計劃的 ★INVARIANT★):不影響。只在 SKILL.md 的開案步驟多一句,沒改判定碼。
- `bound-tests-gate`(對 impact 固定席的合約測試逐支真跑):不影響。規格閘只多印一行,rc 與留痕不變;`--push-check` 不經過這條路徑。
- `guard-kill`、`授權與歸屬`、`測試假綠形態`、`lumos-cli-lifecycle`:不影響。diff 沒碰 kill 流程、授權白名單、vendor 或 re-inject。
- `loop-convergence-recording` 與其餘只列名的節點:未發現牽連。
- 提醒:`commands/INDEX.md` 沒列 `rejections`,而 `reference.md` 說它是「85 個指令的總目錄」。計劃已用 4.5k 字上限說明這是刻意的,所以不單獨列。
- 角色卡:`LUMOS-ROLE-CARDS: on`,但沒有附卡,略過。

共 3 條 finding,最高一條是 F1(`superseded_by` 為空鍵或清單時 `lumos rejections` 崩潰,修補新引入)。
