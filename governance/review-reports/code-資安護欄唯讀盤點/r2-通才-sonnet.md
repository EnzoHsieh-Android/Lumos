severity: major

# 通才席(sonnet)r2 報告:code-資安護欄唯讀盤點

**共用派工詞補發前的限制**:我先跑時 `code-seat-common.md` 還不在,所以只依 `通才.txt` 和 `r2-intake.md` 做事。現在已補讀〈輸出格式〉,報告內容沒變,只改格式。

我跑的版本:修前 `20293afe`、修後 `aadf6b07`,各開一個臨時副本。修後版 `python3.14 scripts/test_lumos.py -k seclist` 結果是 280 passed、0 failed。

## 發現

### F1:`_sl_vault` 測試輔助函式撞名,弄壞既有的 summary_line 測試

severity: major
blocking: 是

歸因:有證據的原有漏查。這是整條分支從 `ec4c6307` 到 `aadf6b07` 帶進來的,不是 r2 修補造成的。修前和修後兩版結果相同。

引句:「def _sl_vault(pay_body=」

file: `scripts/test_lumos.py:38114`(既有的 `def _sl_vault(summary):`,不在 diff 裡,被本分支在 `:99630` 新增的同名函式蓋掉)

失敗場景:
- 同名時 Python 取後面那個。既有的 `t_summary_line_*` 測試呼叫 `_sl_vault("WHY:...")` 並期待回傳 3 個值,實際拿到一個 `PosixPath`。
- 我跑了 `-k summary_line`,修前與修後都是 3 passed、6 failed。紅的 6 支是 `t_summary_line_ambiguous`、`_continuation`、`_delete`、`_rejects`、`_replace`、`_verify`,錯誤都是 `cannot unpack non-iterable PosixPath object`。
- `-k seclist` 只跑新測試,看不到這個問題。全套的推送前閘會紅。
- 我另外掃了 `def` 重名:除了 `_sl_vault`,只有 `t_dart_profile_discovery` 重名。它在 `ec4c6307` 就已經是 2 個,與本案無關。

證據(case):
- claim:新增的 `_sl_*` 輔助函式不得蓋掉既有的同名函式。
- input:`python3.14 scripts/test_lumos.py -k summary_line`。
- expected:既有 `t_summary_line_*` 全綠。
- 出處:`ec4c6307` 只有一份 `_sl_vault`(`git show ec4c6307:scripts/test_lumos.py | grep -n "^def _sl_vault"` 只印出 38114)。
- case_source:既有測試。
- before 命令與結果:`r2-通才-before` 跑同一條指令,3 passed、6 failed。
- after 命令與結果:`r2-通才-after` 跑同一條指令,3 passed、6 failed。
- comparison:修前與修後相同,不是 r2 回歸。
- attribution:原有漏查。

### F2:非 UTF-8 的筆記被靜默丟掉,沒有任何測試守著

severity: major
blocking: 是

歸因:有證據的原有漏查。這段程式在修前與修後相同;r2 只是把名字從 `_secinv_*` 改成 `_vault_safe_*`。

引句:「errors.append(_vault_issue("not_utf8", nfc(rel), detail="不是 UTF-8"))」

失敗場景:
- 我把這行換成 `pass`,`-k seclist` 仍是 280 passed、0 failed。測試檔裡根本沒有 `not_utf8` 這個字串。
- 拿掉那行後,放一個 `Systems/Bad.md`(內容 `\xff\xfe bad`)進圖譜再跑:rc=0、read_complete=true、registration_complete=true、errors 為空。
- 也就是說,一篇讀不了的登記筆記會被當成「完整讀完、沒問題」。這正是計劃要防的「讀一半報成乾淨」。
- 實際程式現在是對的:同樣輸入會得到 `not_utf8` 錯誤、rc=2、read_complete=false。但沒有任何測試釘住這件事。
- 文件(`lumos-cli-read` 家節點的錯誤種類對照表、r2-intake 的 G6 組)聲稱「not_utf8 確認只記一次」,卻沒有對應測試。

證據(case):
- claim:非 UTF-8 的筆記要列 `not_utf8`、read_complete=false、rc=2,而且只記一次。
- input:`Systems/Bad.md` 內容 `b"\xff\xfe bad"`,另有一條合法控制項。
- expected:照 `_SECINV_READ_KINDS` 與計劃「讀取不完整退出 2」。
- case_source:我手寫。
- before/after 命令與結果:修前與修後程式相同,真實程式回 `[{'kind':'not_utf8',...}]`、rc2。
- mutation 命令與結果:拿掉那行後 `-k seclist` 280 passed(沒有任何測試變紅),手跑同輸入得 rc0。
- comparison:修前、修後相同,不是 r2 回歸。

### F3:讀取類錯誤的 `read_complete` 旗標,只有部分種類有斷言

severity: minor
blocking: 否

歸因:有證據的原有漏查。

引句:「_SECINV_READ_KINDS = frozenset(("unsupported_safe_read", "read_error", "enumeration_failed", "symlink_rejected",」

失敗場景:
- 我分別把 `special_file`、`file_too_large` 從這個集合拿掉,`-k seclist_s0` 與 `seclist_s1` 都全綠。拿掉 `changed_during_read`(S11 紅)和 `symlink_rejected`(S3 紅)則有測試抓到。
- 拿掉 `special_file` 或 `file_too_large` 後,read_complete 會變成 true,但 rc 仍是 2,因為 errors 非空。
- 只讀 `read_complete` 的機器消費者會被誤導成「讀完整」。

證據(case):
- claim:`special_file` 與 `file_too_large` 都要讓 `read_complete=false`。
- input:`-k seclist_s0`、`-k seclist_s1`(s03、s10 在內)。
- expected:這兩個集合成員被移除時要有測試紅。
- case_source:我手寫的 mutation。
- before/after:修前與修後的 `_SECINV_READ_KINDS` 內容相同。
- mutation 結果:全綠。
- comparison:不是 r2 回歸。

### F4:`references_valid` 裡的 `unknown_evidence_status` 分支沒有測試

severity: minor
blocking: 否

歸因:有證據的修復新增處的測試缺口。G3 是 r2 新增的行為,屬於「修補處的相鄰路徑」。

引句:「_SECINV_REF_ERROR_KINDS = ("reference_error", "unknown_evidence_status")」

失敗場景:
- 我把它改成只剩 `("reference_error",)`,`-k seclist` 仍是 280 passed。
- 影響:證據紀錄的 status 不是合法值(例如 `SlWeird` 的 `status: greenish`)時,控制項是否算 `references_valid`、是否消除入口缺口,現在沒有測試釘住。
- G3 的測試只用「找不到的決策」(`BADREF-R`)和「找不到的 Verification 節點」(`BADEV-R`),兩者都屬 `reference_error`。

證據(case):
- claim:證據 status 非法的控制項不得消除入口缺口。
- input:`evidence_refs` 指向 `Verification/SlWeird.md`(status `greenish`)。
- expected:`references_valid=false`、入口仍 unmapped。
- case_source:我手寫,fixture 裡已有 `SlWeird`。
- before:`20293afe` 沒有 `references_valid` 這個欄位,無法比較。
- after:拿掉分支後 280 passed。
- comparison:這是 G3 新行為的守衛缺口,屬修補不完整。

### F5:G2 的「文字模式自由欄位最多 2000 字」只做了一部分,文件卻寫成全部

severity: minor
blocking: 否

歸因:有證據的修復不完整。

引句:「cid = _secinv_show(r["id"])」

失敗場景:
- 計劃與家節點寫「文字模式每個自由欄位最多 2000 字並標明截斷」,但控制項 `id` 的 regex 沒有長度上限,而且顯示時沒帶 cap,在標題行和框線行各印一次。
- 我造了一條 1,000,000 字元的 id,跑文字模式,輸出約 3.0MB,這個 id 在輸出中原樣出現 3 次(兩行加覆蓋缺口段)。
- 其他沒有套 cap 的地方:`_secinv_render_coverage` 裡的 `inventory`,以及 `unclassified_contracts` 的 `claim`。
- G2 的測試只量了 `scope` 這一個欄位。

證據(case):
- claim:文字模式的所有自由欄位都有長度上限。
- input:id=`"A"*1_000_000`,`security list` 文字模式。
- expected:輸出不超過各欄位 cap 的總和。
- case_source:我手寫。
- before/after:r2 沒動 `id` 的顯示方式,只動了 `scope`。
- comparison:前後相同,屬 G2 的修補範圍沒蓋到。

### F6:文字模式的覆蓋缺口看不到 `invalid_reference_control_ids`

severity: minor
blocking: 否

歸因:有證據的修復不完整。

引句:「cols = ("mapped_control_ids", "applicability_pending_control_ids", "unverified_control_ids", "defect_control_ids",」

失敗場景:
- 這個欄位清單沒有 `invalid_reference_control_ids`。
- 我造了一條決策引用錯誤的控制項(`BADREF-R`,surfaces=["S-refund"]),跑文字模式。
- 結果:S-refund 行顯示 `state=unmapped`,所有 `*_control_ids` 都是空的,看不到是哪條控制項被擋;要自己去翻錯誤區。
- 計劃 d3 說「另列 invalid_reference_control_ids」,但只有 JSON 做到了。G3 的測試也只驗 JSON。

證據(case):
- claim:文字模式也要列出引用失效的控制項。
- input:`BADREF-R`,`decision_ref: Systems/SlPay#d9`,文字模式。
- expected:S-refund 行含 `invalid_reference_control_ids=["BADREF-R"]`。
- case_source:我手寫。
- before:`20293afe` 沒有這個欄位。
- after:文字模式沒有。
- comparison:r2 新欄位只接到 JSON。

### F7:整合反例 ⑤ 沒有測到真正的風險,「來源修訂與證據適用性未核對」這句限制沒有任何測試

severity: minor
blocking: 否

歸因:有證據的修復不完整。

引句:「check("整合⑤ 舊證據 stale", _sl_rec(doc, "I-OLDENV").get("evidence_check") == "stale")」

失敗場景:
- 測試用的是作者已經把 Verification 標成 `stale` 的情況。工具讀到 stale 就回 stale,這本來就是對的,但不是母計劃表格(「換需求修訂、實作或環境後套舊證據 | P1報告列待重驗」)描述的風險。
- 真正的風險是:需求或實作改了,作者卻沒更新 Verification,它仍是 `pass`。工具只能判成 `declared_only`,並靠限制句「來源修訂與證據適用性未核對」說清楚它做不到。
- 我把這句限制從 `_SECINV_RECORD_LIMITS` 拿掉,`-k seclist` 仍是 280 passed。
- 測試的 docstring 有誠實說明「盤點層做不到的只驗不升格」,但 ⑤ 沒有任何不升格的斷言。

證據(case):
- claim:⑤ 在盤點層的預期是「不升格,並列限制」。
- input:`revision` 與 Verification 內容不同步的 pass 紀錄。
- expected:`declared_only` 加上該句限制。
- case_source:我手寫。
- mutation 結果:拿掉該句限制後全綠。
- comparison:r2 已改寫此測試,這一句在修前修後都沒有斷言。

### F8:50000 項上限的邊界(剛好 50000 項)沒有測試

severity: minor
blocking: 否

歸因:有證據的修復新增處的測試缺口。上限是 r2 新增的。

引句:「if len(out) >= entries_left:」

失敗場景:
- 我把 `>=` 改成 `>`(會差一格),`-k seclist_g7` 仍是 5 passed。
- `t_seclist_g7_scale` 只造 `cap+1` 個 .png,再加上 mkvault 本身的幾個目錄,所以超限那邊不管差一格都會觸發。
- 對照:S10 對 .md 檔數有「剛好 10000 照讀、10001 停」兩側,這裡只有一側。

證據(case):
- claim:剛好 50000 項要通過,50001 項要停。
- input:`>` 與 `>=` 兩種寫法。
- expected:只有 `>=` 版本剛好在第 50001 項停。
- case_source:我手寫。
- mutation 結果:全綠。
- comparison:r2 新增處的單側斷言。

## 特別問題:`t_seclist_integration_gaps` 是否涵蓋母計劃六項整合控制

六項都有對應斷言,我跑過測試、拿掉實作確認會紅:

| 項目 | 盤點層預期 | 是否真的能紅 |
|---|---|---|
| ① 決策作廢 | 列引用錯誤、入口不算映射 | 能。我把 `_secinv_surface` 的 `references_valid` 條件拿掉,整合 ① 與 G3 都紅 |
| ② 重抄 oracle | 只到 `declared_only`,列「不核對報告內容」 | 部分。沒辦法區分獨立判準與重抄判準(測試自己也承認),等於只守「不升格」 |
| ③ 假拒絕 | 有 A 合法對照時 `incomplete`,沒有時 `missing` | 能,兩種成對。但「情境無效」是用 `pending` 狀態替代 |
| ④ 執行無效 | `incomplete`,作者的 `verified` 保留 | 能 |
| ⑤ 舊證據 | `stale` | 只守了作者已經標 stale 的情況,見 F7 |
| ⑥ 清單完整仍有未驗 | rc0、errors 空、仍 `not_assessed`、逐入口列未驗 | 能 |

## 三個問題的答案

**① 原問題的修復效果有何行為證據?**

| 組 | 行為證據 |
|---|---|
| G1 | 我拿掉 `_secinv_inv_items` 裡的 `continue`,G1 測試出現 TypeError 紅。拿掉 `_secinv_is_text` 的代理字元檢查,G1 紅(30 項替換 rc 預期 2 卻是 0)。 |
| G3 | 把 `_secinv_surface` 的 `references_valid` 條件拿掉,G3 與整合 ① 都紅。 |
| G4 | 拿掉圖譜根的 `O_NOFOLLOW`、拿掉中間目錄的 `O_NOFOLLOW`,G4 各自紅。 |
| G7 | 把 `by_surface` 索引改回掃全表,G7 紅(21.0 秒,門檻 12 秒);把合約宣稱快取拿掉,G7 紅(12.3 秒,門檻 6 秒)。但 inventory 的 ID 集合被我改回每筆重建後,G7 仍通過(測試沒抓到這個二次方)。 |
| G8 | 拿掉讀取請求的剩餘額度限制(`want = _VAULT_SAFE_FILE_MAX + 1`),G8 紅,S10 沒紅。 |

G2 與其他組我沒另做逐項變異實驗。這些結果只是這幾個 mutation 的紅,不代表整體無回歸。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- `_fence_regions` 抽出前後的 `_visible_lines`:我拿 `ec4c6307` 的舊版與 `aadf6b07` 的新版做隨機差異比對,3 萬組(各 2 種 `keep_fenced`)輸入,0 個差異,所以抽取沒有丟掉舊行為。
- 舊名稱殘留:`git grep` 已無 `_SECINV_FILE_MAX`、`_secinv_err`、`_secinv_snapshot`、`_secinv_read_rel` 等被改名的符號。
- 相鄰路徑:F1 是新輔助函式蓋掉既有的,屬於影響到呼叫端的相鄰路徑失敗(原有漏查)。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- F1:修前 3 passed、6 failed;修後 3 passed、6 failed。相同,原有漏查。
- F2、F3、F8:`_vault_safe_*` 這幾段在 r2 只是改名與加上限,行為前後相同;沒有測試守著這點兩版都一樣。
- F4、F5、F6:`references_valid`、`invalid_reference_control_ids` 與 2000 字 cap 的相關欄位是 r2 才新增,修前不存在,無法兩版對照,這幾條歸因為「修復不完整」。

preserve(正常路徑仍成立)的修前成功證據:`r2-intake.md` 的 preserve 案例我只在修後版驗了 S1–S13 與 G1–G8 全綠(280 passed)。修前版我只跑了 `-k summary_line`,其他 preserve 例沒有在 `20293afe` 逐一跑,所以這部分未判定。

## 未驗範圍
- 沒有逐項驗證 G2 的 JSON 跳脫(我只讀了程式和測試,沒另做 mutation)、G5 以外的 `_vault_in` 呼叫端、文字模式的資料框是否能被偽造。
- 沒有跑 CI 或全套測試(只跑子集),也沒檢查文件 patch 的 Verification 內容是否與 `lumos doctor` 對得上。
- 文件 `Verification/2026-10-19_資安護欄唯讀盤點實作.md` 裡「14 支測試、203 條斷言」的舊數字(現在是 280 passed)有沒有過期,我沒逐句核對。

## 暫存清理
- 兩個臨時 worktree 已用 `git worktree remove --force` 移除,`/tmp/lumos-seat-work/code-資安護欄唯讀盤點/通才-sonnet/` 已刪。
- 測試紅時會在 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 留下 `gctl-run-*` 現場。我確認屬於我的只有 `gctl-run-1buxrb4_`,已刪。我另外跑的 mutation 紅也各留了現場,但目錄裡有 100 多份、同時間可能有別的會談在跑,我無法逐一確認哪些是我的,所以沒刪,請編排者視情況處理。

最嚴重 severity: major,blocking 共 2 條(F1、F2)。
