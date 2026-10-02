severity: major

審查範圍:通讀 diff 全文,把 diff 已提交進去的版本複製到臨時 clone(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/r2c`)做實驗,沒動原 repo。實跑結果如下。
- `-k slots_retire`:20 條斷言全綠。
- `-k drift`:883 條全綠。
- 在 clone 裡逐項拿掉判斷重跑 16 種(跑前都清了 `__pycache__`):①②③⑤、doctor 三處、預算都有咬住。有 5 處沒翻紅,見 R2C3。

**R2C1**
severity: major
blocking: 是 — 表態只認第一個實體行,續行寫條件的 RULE 會被別條的表態或舊表態靜默放行,擋人的閘出現新的繞過路徑。
引句:「out.append((no, phys[no - 1].strip(), _probe_parse("[" + vals[0] + "]")))」
1. 表態比對的鍵是「路徑 + 一字不差的原文 + 種類」(`_drift_ack_key`、`_drift_split_acked`)。欄位寫在續行時,原文只剩第一個實體行,撤除條件本身不在鍵裡,有兩種後果。
   - 同一篇筆記裡首行相同、續行條件不同的兩條 RULE,表態其中一條會讓另一條一起放行。
   - 表態之後把續行的條件改成別的(例如改成已成立的檔),舊表態仍然有效,「新寫時已成立」的擋就失效了。
2. 改這版之前,原文是接回續行的整條,改條件會讓表態失效。這個行為退化只發生在續行寫條件的 RULE;首行就有條件的 RULE 不受影響。
3. 最小重現(在 clone 用 `_dr_repo`、`_rt_push` 臨時加測,已實跑):
   - 重現 A:摘要寫 `head, "  [retire:when-file:src/a.py]", head, "  [retire:when-file:src/b.py]"`,其中 `head = "RULE:要人簽 [依據:人] [since:2026-09-01]"`。
     - 先推 base,再推加 `src/a.py`、`src/b.py` 的 tip。`drift check` 回 rc 1,兩條都列出(第 14、16 行)。
     - 只對第 14 行 `drift ack --kind retire`,提交後重跑,rc 變 0,第 16 行也被放行(預期仍擋)。
   - 重現 B:一條 RULE 的續行是 `[retire:when-file:src/a.py]`。
     - 推 a.py 和 c.py,對首行 ack,提交。
     - 把續行改成 `[retire:when-file:src/c.py]`(c.py 已存在,應算新寫時已成立,要擋),重跑得 rc 0(預期 1)。
4. 建議:`kind == "retire"` 的表態鍵加入撤除條件值或整條 RULE 的雜湊(例如發現多帶一個欄位,ack 時一併記下);或表態只認首行加條件文字。

**R2C2**
severity: minor
blocking: 否 — 沒有判定錯誤,但與圖譜裡寫明的慣例互相矛盾,而且 diff 沒更新相關筆記。
引句:「kind = ("blocked" if mode == "block" else "warned") if must else "passed"」
1. 現在每次跑撤除條件都寫一筆 `passed`。這在 `_drift_probe_check` 的 `if not lines: return` 之前就發生,所以專案根本沒有寫 `[retire:when-*]` 的 RULE 時,每次推送與 CI 照樣寫一行。對照:舊句檢查 m1 在範圍裡沒改程式檔時不記帳。
2. 與下列圖譜筆記衝突,diff 沒有更新:
   - file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:31`:drift-check 閘「放行不寫帳」,理由是存量每天唸同一批會被週報升級成噪音。
   - file: `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:43`:逐一列出寫入者與寫帳頻率,撤除條件這個新增的每推送必寫者沒有補,2026-10-11 的重看會算漏。
3. 小處不一致:非字串的 `base` 在 m1 記成 `""`,這裡 `base_sha` 會記成 `null`。
4. 建議:至少在候選為空時不記帳;並補寫上述兩篇筆記的現況,或明寫撤除條件是例外。

**R2C3**
severity: minor
blocking: 否 — 守衛行為本身沒壞,但測試釘不住這次修的幾處,下一輪改動可以無聲退回。
引句:「check("①續行 RULE 先擋、印的是那一行原文、帶表態段", rc == 1 and head + "\n" in out and "不改就留著並表態" in out」
1. 拿掉判斷後測試仍全綠的項目(clone 實跑):
   - 壞的 `retire` 值(例如 `"nope"`)與 `gate=warn` 並用時不跟總開關,改成寫死 block:無測試。doctor 只測了 `retire: nope` 的「沒讀懂」字樣。
   - `gate=off` 加明寫 `retire=block` 時仍跑撤除條件(`rt_mode` 那個 `if mode != "off"`):無測試。因為沒寫時 retire 本來就跟 off,看不出差別。
   - 推送時印出 `rt_warns` 提醒:整段拿掉,測試仍綠。
   - 逾時訊息依 kind 寫(「RULE 撤除條件」與「條件式回頭條件」):②只斷言「判不了(只列出,不擋)」。
   - 固定段裡 `lumos drift ack <節點> <行號> --kind retire ...` 那一行:①斷言的「不改就留著並表態」和 `--kind retire` 都被標題行與逐筆改法提示滿足,拿掉指令行仍綠。
2. 另外「設定檔壞掉」與「drift_check 不是物件」兩支改成寫死 block 也不會紅,因為這兩種情況下 gate 本來就是 block,兩者等價,不算缺口。

**鏡頭 1 其餘逐項**
- 縮排、tab、行尾空白、`\r`:`_ns_summary_logical` 與 `phys[no-1]` 用同一份 `split("\n")` 和同一個 `strip()`,行號與 `drift ack` 記的 text(`lines[line-1].strip()`)對得上。
- 「同一條」比對(`_drift_probe_old`):只比條件元組、不比原文。只改續行條件時,舊版找不到同條件,會被當新寫,轉變判定這端沒問題;問題只出在表態那端(R2C1)。
- gate/retire 組合:
  - gate=off 時不跑、提醒也不印。
  - gate 或 retire 寫壞時,retire 跟 gate(gate 壞值就是 block)。
  - 設定檔壞掉時,推送印三句提醒、doctor 三行,是照 old_sentence 先例,屬噪音但符合設計,不標。
- doctor:
  - gate=warn 且 retire=block 時不講(比總開關嚴)。
  - gate=block 且 retire 沒寫時不講(retire 跟著 block,沒有鬆動)。
  - gate=block 且 retire=warn 或 off 時講。
  - 寫壞值時講(gate=off 除外)。
  - 與測試④一致。
- `_drift_config` 四元組:除測試外沒有產品端呼叫者。`rt_warns` 改由 `cmd_drift_check` 直接印、doctor 直接讀,沒有提醒因此遺失。
- 記帳:`_gate_event_or_warn` 在沒有 `docs/` 時回 None、寫失敗只印警告,不改判定;整段包在 `except Exception` 裡,git 失敗時 tenv 為 None 會走「判不了」。但 tenv 讀不出時帳上記的是 `passed`,會掩蓋讀取失敗。
- 時間:最壞約為核心 60 秒加一次呼叫、撤除條件 20 秒加一次呼叫、m1 30 秒,合計約 130 到 150 秒。推送前掛鉤沒有逾時,m1 已有同類疊加的先例,不標。

**鏡頭 2 圖譜**
- `Systems/存量漂移守衛`(家):文字已同步,但「表態對的是第一個實體行」這句的後果見 R2C1。
- `reversibility-governance-ledger` 的 WHY「放行不寫帳」與 `Issues/治理帳多個寫入者都沒上鎖`:被牽連,見 R2C2。
- `Projects/舊句檢查_計劃`、`否定現況句配回頭條件_計劃`、`存量漂移防線_計劃`:轉變判定核心沒動(只改逾時訊息文字),gate 預設 block 的決定也沒動,不影響。
- 固定席的 INVARIANT 與 RISK 節點(`lumos-cli-read`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`、`測試假綠形態`、`lumos-cli-lifecycle`、`design-loop`、`canary-audit`、`slim-*`、`節點範圍與索引守衛`、`cochange-guard`、`check-r-guard`、`lumos-deinit`、`pitfalls-code-loop` 等):本 diff 只動 drift check 推送段、doctor 的漂移段和一支新測試,不碰搜尋、綁定測試、guard-kill、安裝與卸載、代碼審 marker。代碼審 marker 讀端已用 `gate == "code-loop"` 過濾,新增的 `drift-check` `passed` 事件不會被誤讀。判不影響。

**鏡頭 3**
- `t_slots_retire_when_push` 仍成立,七項全綠,包括「撤除條件在回頭條件之後另跑一次」。
- `t_slots_retire_followups` 的 ①(首行原文)、②b(獨立截止時間)、③(預設跟 gate)、④(doctor 三處)、⑤(passed 與 head_sha、base_sha)都被實際翻紅;缺口見 R2C3。

**鏡頭 4 角色**
- 資安:控制字元已用 `_esc_clean` 處理,沒有新增的注入面。
- 回滾:`drift_check.retire: off` 仍可只停這一段。

最高嚴重度 major,blocking 1 條
