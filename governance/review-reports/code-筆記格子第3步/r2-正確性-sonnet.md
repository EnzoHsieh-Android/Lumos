severity: minor

審材範圍:`/tmp/code3-r2.patch` 全 933 行逐段讀完。我在自己的 clone 實跑了 S16 新舊對照、gate 設定探測、約 20 個翻紅實驗和 `lumos doctor`。repo 本身沒動。

## 結論摘要

沒有 blocker 或 major,共 5 條 minor,都不擋。

- 值得留意的行為退步只有 R2C1(S16 對單行 `summary:` 漏判),理論上存在,本 repo 實測零筆。
- 其餘 4 條是測試沒咬住:拿掉判斷後測試仍全綠。

## 逐項查證(沒問題的部分)

1. **S16 用 `_ns_summary_logical` 重組**
   - 我跑了 10 種 frontmatter 形狀,拿舊邏輯(逐實體行)對照新邏輯。
   - 區塊 `|-`、折疊 `>`、`decisions:` 在前、summary 不在最後、CRLF 都一致。
   - 欄位寫在續行的 RULE,新版修正了舊版的誤報。
   - 縮排更深的 `RULE:` 行不會被前一行吞掉,因為前綴比對排在續行判斷之前。
   - BOM 由 `load_vault` 用 `utf-8-sig` 讀入時去掉,`fm_lines` 不帶 BOM。
   - 本 repo 全圖譜新舊都是 6 條、同樣 6 篇;`lumos doctor --verbose` 在 base 與 head 的 S16 到 S8 段輸出完全相同。
2. **`_dref_norm` 路徑寫法**
   - `env.resolve` 內部會剝 `.md`,所以 `路徑.md#dN`、不帶 `.md` 的路徑、`[[X#dN]]` 都解得到。
   - 舊程式的 `or env.resolve(x + ".md")` 退路因此不是缺口。
3. **`_slot_vals` 去空值與去空白**
   - `_doctor_fact_recheck_lines` 與 `_metric_rows` 都用 `(… or [""])[0]`,空值與缺值的結果相同,語意沒變。
   - 只有「同鍵重複且第一個是空值」會換成取第二個,但重複鍵在提交時就被擋。
4. **`_drift_retire_report` 的 rc 與記帳**
   - rc 在記帳前就定。
   - block 與 warn 兩種模式,記帳或印出拋例外都不改 rc。
   - 我實跑確認,拿掉記帳的 try 會讓 `t_slots_retire_issue_followups` 紅 4 條。
5. **`_metric_gate_off` 拿掉 try**
   - 我用 10 種壞設定(None、壞 JSON、非 UTF-8、list、null、欄位型別錯等)× 7 個閘名探測,全部回 False,沒有例外。
   - lint-new 改讀 `mode` 後,`{"lint_new":{"gate":"off"}}` 正確回 True。
6. **`_doctor_cfg_bytes`**
   - 與原本三份抄寫逐字等價,筆記形狀、筆記內容審、存量漂移三段行為不變。
   - 度量段從「普通讀」變成「捷徑不跟」,屬刻意加強。
7. **`_gov_metric_events` 時間轉換**
   - 轉時區已進 try,naive 的 `9999-12-31` 與 `0001-01-01` 都只跳那一行。
   - 帳增速段改用 `_drift_jsonl_parse` 後,24MB 檔尾約 0.2 秒、尖峰記憶體約 200MB,可接受。
8. **衍生資料與時間**
   - 度量式 RULE 的 `since` 比較仍用 `cutoff.date()`,沒有新的時區歧義。
   - 治理帳 `handle: null` 是上一版就有的改動,不在這份差異裡。

## Findings

**R2C1** S16 改用重組全文後,單行 `summary:` 的 RULE 不再被列

引句:「        for t in _ns_summary_logical("---\n" + "\n".join(n.fm_lines) + "\n---\n").values():」

- file: `scripts/lumos:3439`
- 重現(我用 `_note_from_text` 餵 `---\ntype: system\nstatus: doing\nsummary: RULE:甲 [since:2026-01-01] [retire:人裁]\n---\n# x\n`):
  - 舊邏輯(`fields["summary"]` 逐行)回報「沒寫 `[confirmed:]`」。
  - 新邏輯回傳空清單。
  - 加引號的 `summary: "RULE:…"` 同樣漏掉。
- 原因:`_notelines_regions` 把 `summary:` 那一行本身標成 `other`,內容在同一行就不會被讀。
- S17 到 S19 本來就有這個盲點,但 S16 是這次新加的退步。
- 本 repo `grep -rE '^summary: *"?(RULE|FACT|WHY):'` 為 0 筆,所以實際影響為零,只是寫法上的缺口。
- 改法:S16 在 `fm_lines` 的 `summary:` 行本身有內容時,另外補一條邏輯行。

severity: minor
blocking: 否 — 單行 summary 在本 repo 零筆,只影響軟提醒,不計入問題數。

**R2C2** `[[X#dN|別名]]` 的別名切除沒有測試咬住

引句:「+    ref = m.group(1).split("|", 1)[0].strip() if m else v」

- 我把 `.split("|", 1)[0]` 拿掉後,`t_slots_doctor_reminders` 加 `_edges` 共 26 條仍全綠。
- 原因:測試裡帶別名的案例用的是現行決策 `Systems/Live#d1|看這裡`,沒切別名時它會落到節點分支、一樣回 None,輸出相同。
- 沒切別名時,死掉的 `[[X#d2|別名]]` 會被靜默放過。
- 改法:補一個帶別名且指向 `valid: false` 決策的案例,例如 `[[Systems/Live#d2|別名]]`。

severity: minor
blocking: 否 — 程式碼本身正確,只是這個判斷沒有測試釘住。

**R2C3** S17、S18 兩處輸出的 `_esc_clean` 沒測試咬住

引句:「+                out.append(_esc_clean(f"{rel}:{no}:[被取代:{v[:40]}] {why}", 300))」

- 我分別拿掉 S17 的 `_esc_clean`、S18 成立列的 `_esc_clean`、S18「度量寫法不合」列的 `_esc_clean`,測試都仍是 26 條全過。
- 只有 S19 那處被 ⑧ 釘住(拿掉會紅)。
- 差異說明第 2 點宣稱「三段輸出一律過 `_esc_clean`」,實際只有一段有保護。
- 改法:在 S17 的 `[被取代:]` 值與 S18 的 `[retire:度量…]` 值各塞 `\x1b[2J`,斷言輸出不含 `\x1b`。

severity: minor
blocking: 否 — 清洗本身有做,只是三處裡有兩處沒測試守著。

**R2C4** 「先記帳再印」的順序沒被任何測試釘住

引句:「+            _drift_retire_ledger(root, ("blocked" if mode == "block" else "warned") if must else "warned",」

- 我把記帳與印出對調(先印後記),`-k t_slots_retire` 共 34 條仍全過。
- 現有 ② 與 ②b 只數「帳有幾筆、rc 是多少」,不論先後。
- 這個順序是 Issue 第 2 項的反轉(原本寫「記帳挪到印完之後」,現在是先記帳),且計劃與系統筆記都寫明了新順序,所以應有測試守住。
- 改法:讓 `_drift_retire_print` 拋 `BaseException` 子類,或在 print 被呼叫時斷言帳已經在,證明帳先於印出。
- ⚠ `except Exception` 擋不住 `KeyboardInterrupt`,所以這個順序的實際價值只在中斷場景,測試設計要想清楚。

severity: minor
blocking: 否 — 兩種順序都不改 rc,差別只在被硬中斷時帳在不在。

**R2C5** S18 整段包 try 與 `_doctor_cfg_bytes` 捷徑防護都沒被測試咬住

引句:「+            _met18 = _doctor_metric_lines(env, _vault_repo_root(env))」

- 拿掉 S18 的 try/except,測試仍全過,因為沒有案例會讓 `_doctor_metric_lines` 拋例外。
- 把 `_doctor_cfg_bytes` 的 `not cp.is_symlink() and cp.resolve() == …` 拿掉,`-k symlink` 的 33 條仍全過。
- 全檔 `grep 捷徑` 找到的捷徑測試只覆蓋 `_nodehome_config`,沒有一條打到這支新抽出的函式。
- 共用化之後,三段 doctor 提醒加度量段的捷徑防護沒有任何測試守住;這類資安防護應該要能翻紅。
- 改法:補一個 `.lumos/config.json` 是指向外部檔的捷徑,斷言 `_doctor_cfg_bytes` 回 None;再注入一個會拋例外的 `_doctor_metric_lines`,斷言 S18 印出「算不出來」而 doctor 不中斷。

severity: minor
blocking: 否 — 防護程式碼本身存在且與原寫法等價,缺的是回歸保護。

## 圖譜鏡頭

派工尾端的固定席備援段在提示裡是空的。我自己跑 `lumos impact --diff 2f9cb94f..384f4574`,把固定席列了一遍。

- **`Systems/lumos-cli-read`**(INVARIANT 家)
  - 它的 KEY/INVARIANT 行講的是 search 預設排除 superseded、`contracts` 與 `doctor` 的總覽,沒有一條涉及 S16 到 S19 的行為。
  - 不影響。
  - 新增的 WHY(S17 到 S19、`_doctor_cfg_bytes` 統一)與程式一致。
  - S16 那條 WHY 沒提「接回續行」,是漏寫,但不是矛盾。
- **`Systems/存量漂移守衛`**
  - 新 WHY 與程式一致:「rc 判完就定、先記帳再印」。
  - 但「先記帳再印」沒有測試守衛(見 R2C4)。
  - 其餘舊 WHY/RULE 沒被破壞。
- **`reversibility-governance-ledger`**
  - 「放行不寫帳」的規則沒被破壞,只有 `must or unknown` 才記帳,這支判斷沒動。
  - 不影響。
- **`guard-kill`、`bound-tests-gate`、`授權與歸屬`、`測試假綠形態`、`design-loop`、`pitfalls-code-loop` 等 INVARIANT/RISK 固定席**
  - 這份差異動的是 doctor 軟提醒、推送那支撤除條件和一組測試,沒碰這些節點宣稱的合約。
  - 不影響。
  - 軟段一律不計入問題數,不動 doctor 的 rc。
- **文字與程式一致性**
  - Issue `撤除條件檢查末輪遺留四項` 改回 `status: doing`,frontmatter 與 tag 一致,收尾條件寫明「推上主線後結案」。
  - 計劃表格的 `[被取代:]` 一列寫「只看標了作廢的行」,與 `_ns_superseded(rest)` 一致。
  - 計劃表格的 FACT/FLOW/DEP 一列寫「預設 3 條加總數」,與 `warn_soft` 的 `_SOFT_CAP` 一致。
  - 04 子檔的 `drift ack` 行號說明與程式一致。

最高嚴重度 minor,blocking 0 條
