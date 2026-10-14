severity: major

## 合約與圖譜一致席 第八輪報告

整體判讀:r7 換形狀的主線已落地。拿掉內容比對,改成「這個編號的輕量審閘」或「-std 完整設計審過處置閘」兩條出口。AGENTS.md、CLAUDE.md、graph-discipline 範本、兩份指令參考、兩份心智模型、design-loop 與 code-loop 的 SKILL 都改成同一句話。S1–S50 與綁定測試一一對得上,d1 的 trade_offs 與正文一致。

我跑過的檢查:
- `lumos spec-trace` 50 條全綁、懸空 0。
- `lumos lint` 計劃與 Systems/規格閘兩篇都 0 問題。
- 九支相關測試:nogo_light_major_points_to_std、nogo_std_review_exit、nogo_light_bound_rows_same、door_scan_logic_version_pin、door_nfkc_zero_width、canary_ledger_streams、nogo_shared_helpers、older_hint_versions、nogo_line_key_normalized,全過。
- 全 repo 搜尋 `_nogo_major_carried`、`nogo_rows_sha`、`ratchet=False`、`_nogo_major_lookup` 等舊名,程式與現行文件都已清乾淨,只剩標明歷史的說明。

另外找到下列問題。

severity: major
blocking: 是 — 同一族盲區(危險詞藏進看不見的字元,繞過風險判定)的修補只補了一小部分,宣稱「夾零寬字元的危險詞也算」對常見的零寬字元不成立。
引句:「再拿掉零寬字元(共用 _strip_zero_width;」
問題:`_door_scan_text` 只做 NFKC,再用 `_strip_zero_width` 拿掉 U+200B 到 U+200F 和 U+FEFF。其他同樣看不見的字元完全沒處理,包括 U+2060(WORD JOINER)、U+00AD(軟連字號)、U+202A 到 U+202E、U+034F、U+180E、變體選擇符。測試 t_spec_gate_door_nfkc_zero_width 只覆蓋 ZWSP 和 BOM,所以綠燈。這是 r5 圍欄、r6 反引號之後同一族的第三次,沒有一次掃完。
具體失敗情境:我實跑 `_door_keyword_hits("實作 退\u2060款 流程")`,回空。`pay\u2060ment` 和 `pay\u00adment` 也是空。計劃的做法節寫了這種字串,規格閘判風險低,不派審。軟連字號是網頁複製貼上常見的殘留,不只是刻意繞過。文件寫「全形英數與夾零寬字元的危險詞也算」,所指範圍比實際大。
佐證:file: `scripts/lumos:8078`
佐證:file: `scripts/test_lumos.py:61444`

severity: major
blocking: 是 — 新增的 (b) 出口把推送前檢查接到 `cmd_loop_status`,它讀帳只接 ValueError,不接 RecursionError,破壞 S23「超深巢狀行只跳過那一行」。
引句:「except (OSError, ValueError) as e:   # UnicodeDecodeError 是 ValueError 的子類:帳不是 UTF-8、沒人裁紀錄時 cmd_loop_status 照原樣往上丟」
問題:`_nogo_std_gate` 只接 OSError 和 ValueError。`cmd_loop_status` 解析每行用 `except ValueError`,RecursionError 不是它的子類。r4 修過讀帳少接 RecursionError,r7 的 `_canary_ledger_rows` 也有接,唯獨新路徑漏了。
具體失敗情境:我實跑重現。計劃輕量審抓到 major,且已記一筆 -std 完整審,這是 r7 主推的出口。審查帳任一處有一行超深巢狀 JSON(`[` 重複 20 萬次)。推送前檢查丟出 RecursionError 的 traceback,依序經過 `_spec_gate_push_light`、`_nogo_std_gate`、`cmd_loop_status`,rc 1,沒有任何講原因的訊息。這個計劃無法推,除非有人去手動清帳。S23 的測試只涵蓋 (a) 通過的情境,看不到這條路。暫存現場 gctl-run-e5afjoh0 我已確認是自己建的,並已刪除。
佐證:file: `scripts/lumos:13456`
佐證:file: `scripts/lumos:9352`

severity: minor
blocking: 否 — 只是說明文字過期,會誤導操作,但推送前檢查本身會講清楚擋下原因。
引句:「同一個編號以前審過(窗口外有 major,」
問題:templates.md 裡「`loop next` 回 escalate 或 cap-reached」那一段原封未動。它說「推送前檢查只認不帶 -std 的原編號」,並叫人在原編號手寫記帳,「還是 major 就寫 plan_risk: high」。r7 之後有兩處已不成立:(b) 出口明確認 `<編號>-std` 的處置閘;原編號只要有任一筆 major,light 就永久失效,不分窗口內外。
具體失敗情境:`loop next` 因為原編號有 major 叫人開 -std。使用者改照這段在原編號再手寫一筆乾淨輕量審,推送前仍然擋,浪費一輪。
同類未同步的還有 Systems/design-loop.md 第 49 行 KEY:「不做清單略過了危險詞的走…light 輕量審,同樣不進處置閘」。現在 major 時走 -std,會進處置閘。skills/lumos-project-notes/commands/05、commands/INDEX.md、lumos-design-loop/reference.md 只寫「要一筆輕量設計審」,沒補 major 改開 -std。
佐證:file: `skills/lumos-design-loop/templates.md:71`
佐證:file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:49`

severity: minor
blocking: 否 — 測試守不住條款,但目前行為正確。
引句:「真的串流——開檔逐行讀,不把整本帳讀成一份位元組」
問題:t_canary_ledger_streams_one_core 的守衛只攔 `Path.read_bytes` 和 `Path.read_text`。我把 `_canary_ledger_rows` 換成 `Path.open("rb").read()` 整本讀進記憶體的版本,五條斷言全綠。這正是 r6 被點名的「整本讀進來再切」,測試名叫 streams 卻抓不到。這也不符合測試假綠形態合約要求的前置斷言(證明被測路徑真的走到)。
另一個落差:(b) 出口的 `cmd_loop_status` 用 `read_text` 整本讀帳。有 -std 紀錄且 (a) 沒過的計劃,每份都會再整本讀一次。文件寫的「審查帳開頭讀一次、不整本進記憶體」與 S33 因此不再嚴格成立,測試也看不到。
佐證:file: `scripts/test_lumos.py:61377`
佐證:file: `scripts/lumos:13451`

severity: minor
blocking: 否 — S49 的結構守衛太窄,漏掉同族寫法,文件宣稱的「收掉最後一處」不實。
引句:「return q if q.is_absolute() or root is None else Path(root) / q」
問題:t_nogo_shared_helpers_used 只數一種拼法的字串 `is_absolute() or root is None`。`loop next` 的 reviewed_spec 解析仍是另一種拼法 `Path(_sp) if Path(_sp).is_absolute() else (_root / _sp)`,同樣是「帳上相對路徑接 repo 根」。`_hooks_path` 一帶另有 `Path(v) if Path(v).is_absolute() else (Path(root) / v)`。這兩處都沒進共用的 `_under_root`,測試仍綠。計劃修正紀錄寫「`_under_root` 收掉最後一處」,與程式不符。
佐證:file: `scripts/lumos:16048`
佐證:file: `scripts/test_lumos.py:61423`

severity: minor
blocking: 否 — 〈實務隱患〉天花板已誠實寫出,但回頭條件沒有可量的偵測法。
引句:「帳上的編號、輪次、快照、席名都是記帳的人自己填的」
問題:改檔名、換編號、自填輪次這三種手法已寫進〈實務隱患〉並附 RETIRE-IF,同樣有天花板。但 RETIRE-IF 要的是「逃逸帳出現靠改檔名或換編號洗掉 major 的實際案例」。逃逸帳的 `plan` 欄只有計劃路徑,看不出 major 是否被洗。唯一的 REVISIT:2026-12-15 只查 `nogo_skipped_n` 大於 0。r6 原有的、可數的 REVISIT(數被別的編號 major 擋的次數)又拿掉了,沒補替代。這句話等於沒人會回頭查。
具體失敗情境:有人把計劃改名、換編號重審,洗掉了 major。逃逸帳最後只記「該計劃風險低且 `nogo_skipped_n` 大於 0」,RETIRE-IF 的條件永遠判不出來。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/規格閘不把不做節的詞算進風險_計劃.md:154`

逐條回應固定席節點:
- lumos-cli-read(search 不排除 stale):與本次無關。
- design-loop(處置閘第五步):(b) 出口走同一條處置閘,審材為 `.md` 計劃、條款綁定要求都在,沒有破壞。第 49 行 KEY 的過期描述已列入上面第三條。
- guard-kill、bound-tests-gate、lifecycle:本次改動沒有碰到,未見破壞。
- 測試假綠形態:S48 測試缺前置斷言,已列入第四條。

最高等級 major,blocking 2 條。
