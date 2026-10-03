severity: minor

審查範圍:fixup 6c22a561..35de50ac 的差異,即 `scripts/lumos`、判定者範本和 `03-寫回圖譜.md`。我用 `_tail_repo`、`_na_repo`、`_tail2_repo` 的寫法在臨時 repo 實跑。

結果:沒找到 blocker 或 major。找到三個 minor,其中一個在差異之前就存在。

**B1 NFC 與 NFD 同名篇並存時,NFD 那篇的新違規整篇漏查(r1 的「整組不配」只補了配對表)**
severity: minor
blocking: 否 — 差異之前就存在,要兩篇同名篇並存才會發生,補括號放寬沒有因此被繞過
引句:「會被拿去扣另一篇的新違規(代碼審 r1 資安席、正確性席實測:NFC 與 NFD 兩種寫法的同名筆記並存),這種篇整組不配。」
1. 輸入:git 索引裡 `Systems/é.md` 同時有 NFC 和 NFD 兩份,內容都是乾淨的一行;之後只有 NFD 那篇新增一行違規行(含 `` `src/a.py:3` ``),完全沒有補括號。
2. 預期:`lumos note-shape --staged` 回 rc 1,報程式行號引用。
3. 實際:rc 0,沒報。補括號的情境也一樣:兩篇都補括號,NFD 那篇舊行有違規,整組不配之後仍然 rc 0。
4. 原因:`_notelines_parse_added` 用 `nfc(f["b"])` 當鍵,兩篇的新增行併成同一鍵,之後只讀到 NFC 那篇的內容。file: `scripts/lumos:27298`、`scripts/lumos:27528`。
5. 我拿 3ebeeb91 的舊版(feat 之前)同一輸入重跑,結果相同,所以不是這次差異造成的。但 r1 修的是「同名篇不要互相扣債」,同名篇的違規根本掃不到這個問題還在。
6. 重現:用 `scripts/test_lumos.py` 的 `_tail_repo`,加 `git config core.precomposeunicode false`,再用 `git update-index --add --cacheinfo` 放入 NFC 與 NFD 兩個路徑。腳本是 `/tmp/bx/nfc.py` 的「--swap」段,最後一個案例。

**B2 配對總量超過上限時整批靜默不放寬,擋下訊息也沒講上限**
severity: minor
blocking: 否 — 偏嚴,不會漏擋
引句:「return {}, None                     # 沒有候選,或總量超過上限(偏嚴,不算失敗)」
1. 輸入:一次推送裡有 201 篇各自在舊句尾補括號(或候選總對數超過 20000)。
2. 預期:使用者能看出為什麼補括號沒被放寬。
3. 實際:回空表且不算失敗,不印提醒,也不記放寬帳。新加的擋下提示只講「括號群、300 字內、要帶來源」,沒提 200 篇和 20000 對的上限。使用者會照提示檢查括號,卻查不出原因。
4. 邊界值本身沒問題:`> _NS_APPEND_MAX_FILES` 和 `> _NS_APPEND_MAX_PAIRS` 在 200/20000 剛好放行、201/20001 才不配。
5. 位置:`scripts/lumos` 的 `_notelines_append_pairs`。

**B3 `_note_audit_show_class` 的「這次整行送審」會講錯**
severity: minor
blocking: 否 — 只是說明文字不準,不影響判定
引句:「return "只判過句尾,這次整行送審" if any(i == it["id"] for i, _t in scoped[0]) else "沒判過"」
1. 輸入:同編號只有 `(x, tailA)` 的判定。目前的項目帶 `tail=tailB`(舊句改過,仍是補括號,會以尾巴形式送審),或根本沒有 tail。
2. 預期:帶 tail 的項目不該被說成整行送審。
3. 實際:兩種項目都印「只判過句尾,這次整行送審」。我用 `_load_lumos_inproc()._note_audit_show_class(({("x","a"*16):"CONTEXT"},set()), {"id":"x","tail":"b"*16})` 驗過。
4. prepare 對 tail=tailB 的項目仍會送出「尾 tailB」那種清單。只有真的沒 tail 的項目,這句才說得對。

另外有一點不屬於 finding:判定者範本又改了字,但 `_NOTE_AUDIT_PROMPT_VERSION` 還是 2。`scripts/lumos:29591` 的註解寫「改一個字就升版,並重跑 68 句小實驗」。這是同一串還沒推的提交,版本號 2 在這串裡才第一次出現,所以我不判錯。我沒辦法確認 68 句實驗是不是在這次改字之後重跑過,⚠ 請作者自己確認。

**邊界輸入逐項結果,都符合預期**
- 括號帶來源:
  - 全形冒號、全形方括號、空來源、`[來源:人工|外部]`、未知來源 `[來源:口頭]`、完全沒寫,都 rc 1。
  - 半形且帶來源 rc 0。
  - `[來源:人工]` 寫在括號外,或包在行內程式碼裡,rc 0,跟新寫整行的既有判法一致,不是這次引入。
- 判定檔 tail:
  - 小寫 16 碼通過。
  - 大寫、15 碼、17 碼、前後空白、結尾換行、null、全形數字,整份都當壞檔。
  - 壞檔只印提醒、當作不存在,不會擋整個推送。
- 舊句帶 CR、帶 BOM、檔尾沒換行,試了八種組合:
  - 第一層:程式行號引用的舊債都能正確扣掉,對照組「改了舊句的字」照擋。
  - 第二層:清單的舊句與追加段保留 CR,檔尾沒換行與 BOM 都沒問題。
  - 舊句尾端有空白時,舊句照原樣印,雜湊用去頭尾空白的版本。
- 總量上限:兩個邊界比較式沒有差一。
- skip 與 check:我讀了 `cmd_note_audit_skip` 的新算法,沒找到洞。
  - 同編號任何範圍判了 CODE 或 MIXED 就擋。
  - 只判過別的 tail 的項目,check 也算沒涵蓋,所以 skip 可以略過。
  - 略過檔與判定檔同時存在時,判定優先。
- 申訴不分範圍:同編號的整行與只判句尾兩種判定,申訴都會一起換。一份判定檔裡同編號不會同時有兩種範圍,因為 `_note_audit_mark_appended` 要求同編號每一處都配到同一句舊句才標追加段,所以不會誤降級。
- 擋下訊息:新提示只在 `blocked`、`mode == "block"` 且 `viol or errs` 成立時印。warn 模式、只有格子違規、只有測試綁定違規時都不印。
- 二分裁法:整行長度隨筆數單調,邊界(0 筆、全部留下)正確,`_drift_m1_fit` 行為沒變。
- 放行去重:`pairs` 是 `[路徑, 行號]` 的列表,雜湊鍵確實含配對內容;沒有推送編號就不去重。
- 測試:`-k template_pinned` 和 `-k append` 子集共 181 個通過。

**固定席節點逐條判**
- `reversibility-governance-ledger`:這次多記 `relaxed` 放寬帳,沒動既有欄位的語意,`_ns_relaxed_seen` 只是少記重複的,不影響可逆性帳。
- `lumos-cli-read` 的 INVARIANT(search 預設排除 superseded):沒動搜尋路徑,不影響。
- `bound-tests-gate` 的 INVARIANT(綁定測試逐支真跑):`_gate_event_fit` 只改帳的裁切,沒動綁定測試的跑法,不影響。
- `guard-kill` 的兩條 INVARIANT(kill 的 rc 優先序、`--json` 純淨輸出):沒碰這些函式,不影響。
- `授權與歸屬`:`scripts/lumos` 的檔頭 SPDX 與 MIT 沒動,不影響。
- `測試假綠形態`:要求翻紅釘配前置斷言。這次新增的測試我沒逐支檢查翻紅性,不影響該節點宣稱的行為。
- `pitfalls-code-loop`、`design-loop`:這次沒動它們的合約行為,不影響。
- 其餘只列名的節點不必答。

最高嚴重度 minor,blocking 0 條
