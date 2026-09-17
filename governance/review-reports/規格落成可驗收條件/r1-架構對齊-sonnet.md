severity: minor

## 一、分層與依賴方向

**對齊。** 新指令 `lumos spec-gate` 與既有 `cmd_canary`、`cmd_loop_escape`、`cmd_pitfalls`、`cmd_spec_trace` 同層(`scripts/lumos` 裡的頂層 `cmd_*` 分派函式,由 CLI 解析器與 `scripts/hooks/pre-push` 以 subprocess 呼叫),沒有看到跨層直呼。

- 逃逸自動記(S9–S11)這部分**其實已經落地**,不是紙上設計:`scripts/lumos:7544` 的 `cmd_loop_escape(..., auto=False, ...)` 與 `scripts/hooks/pre-push:237-240` 的呼叫,行文與 fail-open 註解跟凍結稿第五節逐字對得上。
  引句:「三個來源:代碼審 major 以上的發現、CI 紅、推送閘擋下」
severity: minor
  (這條不是缺陷,是提醒:代碼審那三條裡有兩條已經在工作樹跑,審查對象應同時確認 `git status` 顯示的 `scripts/lumos`/`scripts/hooks/pre-push`/`scripts/test_lumos.py` 改動與凍結稿一致,而不是重審一份還沒寫的設計。)

- 共用條款檢查器方向(spec-gate 與處置閘第五步呼叫同一支)符合本專案「單一來源、不留兩份規則」的既有慣例——同一份 `條款綁測試算進度_計劃` 在 code-loop r2 就因為「三條規則散在解析器裡,又是第二份」被架構席判 major、收斂成 `_strip_inline_markup`。
  引句:「處置閘第五步改成呼叫同一支條款檢查器(單一來源,不留兩份規則」
  file: `docs/lumos-toolchain-knowledge/Projects/條款綁測試算進度_計劃.md`(code 迴圈 r2 段:「三條行內可見規則散在解析器裡,又是第二份 → 收成 `_strip_inline_markup`」)—與凍結稿同一種收斂方向,對齊。

- 門判定借用 `PITFALL_CLASSES`(`scripts/lumos:16962-16966`)的四類與既有 `risk/` 標籤、`★IRREVERSIBLE★`/`★CHECKPOINT★` 合約行,沒有另開偵測層。
  引句:「實務隱患反問的關鍵字表命中四類任一(金流/對外送出/不可逆/自我治理」
  對照:`PITFALL_CLASSES = {"payment":..., "external-send":..., "prod-irreversible":..., "self-governance":...}`(`scripts/lumos:16962-16966`)——四類名稱與凍結稿逐一對上,借用不自建,對齊。

## 二、命名與錯誤處理

**大致對齊,一處落在灰色地帶。**

- 指令命名 `spec-gate` 延續既有 `spec-trace`(`scripts/lumos:4718 def cmd_spec_trace`)的 `spec-*` 家族命名,一致。
- 印法明講「照處置閘」,即沿用 `[disposal] <名>: ✓/✗ — <原因>` 那套已經是三段式白話的格式(發生什麼→為何在意→指令獨立一行的既有慣例,見 `scripts/lumos:15716`、`15734` 等處置閘輸出),對齊。
  引句:「新閘 `lumos spec-gate <計劃.md>`(印法照處置閘)」

- **落點不清楚的一條**:凍結稿要求雙向門放行時「在審查帳寫一筆 `kind: spec-gate` 留痕」,但 `.canary-log.jsonl` 的寫入口 `cmd_canary` 在 CLI 層把 `kind` 鎖成封閉列舉 `choices=("caught", "missed", "none")`(`scripts/lumos:27818`),讀側 `_round_valid_m2` 也明講「未知 kind 使輪無效」(`scripts/lumos:6335` 附近註解)。凍結稿沒有提到要擴充這個列舉、也沒提到要不要綁 `--loop`,如果走的是繞過 `cmd_canary` 直接寫 JSON 行,就是對同一本帳開了第二個未經驗證的寫入路徑,跟既有「留痕走既有審查帳的寫入原語」的自我要求(凍結稿第 174 行「留痕走既有審查帳的寫入原語」)不一致。
  引句:「並在審查帳寫一筆 `kind: spec-gate` 留痕(推送閘與代碼審才知道這份計劃是這樣放行的)」
severity: minor
  (只是命名/驗證層級跟鄰居沒對齊,不是結構錯誤——既有 `kind` 家族本身也是逐步擴充出來的 caught/missed/none,加一個新值是可以做的事,只是這份設計沒寫清楚要不要改 `cmd_canary` 的 choices、要不要繼續走它做驗證,留給實作時裁。)

## 三、第二種做法

**沒有找到「第二套」的實質違規;一處待實作時確認寫入路徑(見上)。**

- 五型觸發式句式檢查是新能力,但不是重複——既有 `[SN]` 機制(`條款綁測試算進度_計劃` 落地的 `clause_bindings`/`_disposal_clause_step`)只驗「有沒有定義行、有沒有綁定」,從沒驗過定義行文字的句式;新加的是正交檢查,且 PRIOR-ART 明寫「借用 EARS/BDD,不自建」,不構成第二套條款解析引擎。
  引句:「不算條款,閘印「格式看不懂」(沿用處置閘第五步「像清單項卻用了不認得的前綴」那條的處置)」——連錯誤處置路徑都沿用既有的,而不是另開一條。
- 風險類偵測完全借用 `PITFALL_CLASSES`,逃逸帳完全借用既有 `.escape-log.jsonl` 與 `cmd_loop_escape`(已落地驗證)。四類/去重鍵/fail-open 全部跟既有原語一致,沒有另開第二本帳。
  引句:「去重鍵:(計劃、階段、提交 sha)。寫進既有的 `.escape-log.jsonl`,不開新帳」
- 唯一有疑慮的是 Q2 提到的 `kind: spec-gate` 寫入方式——如果是走 `cmd_canary` 加一個新 choice,是既有 `kind` 家族的自然擴充,不算第二種做法;如果繞過 `cmd_canary` 另開寫入函式,才構成「留痕欄位形狀外加一套寫入原語」。凍結稿文字本身沒點名走哪一條,判不準,標 ⚠ 交編排者:實作時看 diff 就能一眼確認是否新增了獨立的 append 邏輯而非呼叫 `cmd_canary`/`_jsonl_append_verified`。

## 四、落點合不合理

**對齊,而且正好是這條規則要解決的問題本身。**

`Systems/design-loop.md` 現況:`about_code` 只列 `scripts/lumos` 一支檔(`docs/lumos-toolchain-knowledge/Systems/design-loop.md:128-129`),但 `summary` 裡有 36 行 `KEY:`、被圖譜裡 59 篇節點連結、Projects 底下約 122 篇筆記提到它——已經是一篇「長成包全部」的巨型節點,而這正是 `每支檔有家_計劃` 立下「落點」規則(2026-09-11,S21)想擋的形狀。凍結稿選擇只把「處置閘第五步的不可變合約行改寫」記回 `Systems/design-loop`,把 spec-gate 本體與條款檢查器的家開一篇新的 `Systems/規格閘`,恰好符合落點規則本身的精神(現況分散落點、不再往同一篇塞)。
引句:「lands_in: [[Systems/design-loop]](閘的語意)、新開 `Systems/規格閘`(spec-gate 與條款檢查器的家)」
對照:`docs/lumos-toolchain-knowledge/Systems/design-loop.md` KEY 行本身就記著「節點長成一篇包全部,是因為落點從來沒被審過」(design-loop.md 第 41 行 KEY,關於 `每支檔有家_計劃` [S21] 的段落)——凍結稿的落點選擇正是照著這條教訓做,沒有違反。

---

不對齊共 1 條,其中 major 0 條(minor 1 條:`kind: spec-gate` 留痕的寫入路徑未指明是否走既有 `cmd_canary` 驗證原語或另開寫入邏輯,實作時需確認;附帶 1 處 ⚠ 判不準,理由同上,交編排者在實作 diff 出來後確認)。
