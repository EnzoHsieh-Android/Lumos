severity: minor

**邊界與輸入鏡頭報告(R2B,第 2 輪)**

先說結論:CRLF、tab 縮排、續行比前綴行淺、合併中跳過、`pre2` 的搬運這幾個我最擔心的角落,實測都沒問題。找到 5 條小問題,沒有一條需要擋推送。下面每條都跑過,重現腳本在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/` 的 `k.py`、`e2.py`、`e3.py`。

**R2B1 比對鍵去掉所有空白後,不同的兩句會撞在一起**
severity: minor
blocking: 否 — 只有上一版剛好有一條缺格的舊行才會誤豁免,而閘本來就只防疏忽。
引句:「    bare = _NS_SLOT_SEP_RE.sub("", core)」
- 這個 `sub` 把空白、`見與和及` 和各種標點整個刪掉,不再換成空格。
- 重現:先把 `WHY:a bc` 當舊行,再試新行 `WHY:ab c`,`_ns_slot_line_problems` 回 `[]`,算舊行放行。
- 其他撞鍵例子:`WHY:to run it` 對 `WHY:tor unit`、`WHY:不見得會` 對 `WHY:不得會`,都是 `[]`。
- 改前這幾組的鍵都不同。
- 計劃〈改到舊行〉(約第 111~114 行)只說「連結與分隔字也去掉再比」,沒寫「所有空白去掉」。
- 英文句子撞鍵的機率很低,但這個行為是這輪新加的。
- 場景:需要上一版剛好有缺格的舊行,才會讓新寫行被當舊行放行。
- 選項:要嘛用「空白壓成零或一格」之類只吃折行的規則,要嘛在計劃補一句「空白整個去掉」並把撞鍵記進天花板。

**R2B2 只放連結但帶別名或段落的舊 DEP,永遠不算舊行,補個欄位就被擋**
severity: minor
blocking: 否 — 這種舊行在本 repo 為 0 筆,而且擋下的訊息說得清楚。
引句:「    if "[[" in core and _NS_POINTER_ONLY_RE.match(core):」
- `DEP:[[Systems/甲|說明]]` 與 `DEP:[[Systems/甲#段]]` 在 `_NS_POINTER_ONLY_RE` 不收,`bare` 又被 `[[...]]` 整個吃光,所以 `_ns_slot_key` 回 None。
- 重現:上一版有 `DEP:[[Systems/甲|說明]]`,新行 `DEP:[[Systems/甲|說明]] [confirmed:2026-10-01]`,結果是 `(('來源',), '缺 [來源:]')`。
- 這違反計劃 [S6]「只改欄位的舊行不套必有鍵」。
- 範圍:只影響其他專案可能留著的別名式舊 DEP。
- 解法有兩條:鍵的算法對別名與段落連結照樣取 `link_target`,或在計劃天花板寫明「別名式舊指路行改欄位也要補必有鍵」。

**R2B3 ⚠ 只放連結的舊行,換掉連結不算舊行,但計劃寫「改了連結也算」**
severity: minor
blocking: 否 — 這是文字與程式不一致,擋下訊息會引導改成 `SEE:`,代價很小。
引句:「        return any(old and old <= key[2] for old in old_keys.get(None, {}).get(key[:2], ())), False」
- 程式要求舊連結集合是新連結集合的子集,也就是只能「補」。
- 計劃〈改到舊行〉那一段(約第 114 行)寫「只放連結的舊 DEP/FLOW 行改了連結…也算舊行」。
- 重現:舊 `DEP:[[Systems/甲]]` 改成 `DEP:[[systems/甲]]`(大小寫不同),得到「只放連結的 DEP 改寫成 SEE」。把 `甲` 換成 `乙` 同樣被擋。
- 程式這樣收窄是 r1 為了不放行全新連結,方向合理。
- 該修的是計劃那句,不是程式。
- 此外舊行已標 `status:superseded` 時,只放連結的路徑固定回 `old_sup=False`,和其他路徑不一致。實際影響只是重標作廢的舊行多要求一次 `[被取代:]`。

**R2B4 ⚠ 路徑清控制字元那段是死碼,含 `"`、tab、ESC、換行的檔名整篇被靜默放過**
severity: minor
blocking: 否 — 這個漏洞先於本 diff 存在(`_notelines_parse_added`),本 diff 只是宣稱防了它。
引句:「    路徑也清控制字元(代碼審 code-筆記格子第1步 r1 資安席:檔名可以夾 ESC 序列改終端畫面)。」
- git 對含 `"`、tab、ESC 的路徑一律加引號,`+++ "b/..."` 讓 `p.startswith("b/")` 不成立,`path=None`。
- `file: scripts/lumos:25927-25944`。
- 結果是這種檔名的筆記整篇不查,走不到 `_esc_clean(p, 200)` 這一行。
- 重現:用 `e2.py` 在 `Systems/` 放 `plain.md` 與 `中文.md`,各帶一條 `WHY:另一條缺格子的`,提交時都被擋(rc 1)。
- 同樣內容換成 `tab\tname.md`、`q"uote.md`、`esc\x1b[31mX.md`、`nl\nname.md`,rc 都是 0 且沒有輸出。
- 影響:`"` 這類檔名的筆記不管寫什麼都不會被格子閘(以及整個筆記形狀擋)查到。
- 建議:該檔名要嘛讓抽取改用 `-z`,要嘛在天花板記一句「檔名含引號或控制字元的筆記不查」。

**R2B5 `_ns_vault_rel` 說明寫「工作目錄所在的圖譜優先」,程式其實用 repo 根**
severity: minor
blocking: 否 — 只是說明寫錯,行為跟搬走前一致。
引句:「    """這次要查哪個圖譜(repo 相對路徑)或 None:工作目錄所在的圖譜優先,否則第一個。cmd_note_shape 與單次跳過共用」
- 程式 `wv = _vault_in(root)` 看的是 repo 根(或 `--repo`)下按名稱排序的第一個 `*-knowledge` 目錄,不是 cwd。
- 多圖譜時,從哪個子目錄跑都選到同一個。
- 好處是單次跳過與正常路徑現在會選同一個圖譜(以前跳過那條寫死 `vaults[0]`),這點修對了。
- 說明該改成「repo 根下排序第一個有追蹤檔的圖譜」。

**沒問題的角落(都實測過)**
- CRLF:舊行是 CRLF 加欄位、整檔 LF 轉 CRLF、新寫缺格子的 CRLF 行,結果分別是放行、放行、擋下(`e3.py`)。
- 縮排與續行:續行改成 tab 縮排、續行併成同一行,提交時都放行。`_ns_deleted_summary_lines` 與 `_ns_summary_logical` 用同一套「縮排更深才算續行」,較淺的續行兩邊都不接,沒有不對稱。
- 合併中跳過:`_ns_skip_slot_extra` 在 `MERGE_HEAD` 存在時回 None,和正常路徑一致,跳過帳不會灌水。
- 推送路徑:`pre2` 在 `dests` 與 `_carry` 裡四個字典都有搬運,`mark2` 為空時不收。
- 重複連結:`frozenset` 去重,`[[甲]], [[甲]]` 沒問題。
- 治理帳:`check: "slots"` 不影響 `度量` 的計數,那個只看 gate 與 kind。

**圖譜固定席**
- `lumos impact --diff` 的家是 `Systems/筆記內容閘`、`Systems/每支檔有家` 與計劃 `Projects/筆記格子寫法與過期檢查_計劃`。
- 我看的合約是計劃 [S6] 與天花板 7。
- [S6] 對 R2B2、R2B3 有影響,已寫進上面。天花板 7 這次新增的「複製舊句也算舊行」與 R2B1 同族,但沒有互相打架。
- 其餘 `★INVARIANT★` 節點(`lumos-cli-read`、`bound-tests-gate` 等)是因為改了 `scripts/lumos` 才列入,這次改動的邊界輸入面沒碰到它們。

最高嚴重度 minor,blocking 0 條
