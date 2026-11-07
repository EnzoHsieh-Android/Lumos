severity: major

審查摘要:我在複本(HEAD ffef27ca9,凍結 patch 的改動已在 HEAD 裡)跑了約 45 道改壞實驗,每道都跑 `-k psrc`,有的另加綁定測試子集。複本已刪,沒動 repo。
- 開頭的鎖檔 `.warming` 不存在,沒有需要處理的鎖。
- 這輪新增的測試多數抓得到錯。
- 但有一個筆記與程式相反的 major,以及三個只是覆蓋不全的 minor。

r3 合約席 F1 到 F6 逐條重做:
- F1(d12 沒標已取代):已修好。d12 現在是 `valid: false`、`superseded_by: "#d13"`,d13 四欄齊全,「做法 2」的標註與「資源」那行都改成 60 秒。`lumos lint` 兩篇都 0 問題。
- F2(行中跨行閉合分支沒測試):分支整支拿掉,形狀已換。新形狀的改壞都翻紅:
  - 沒閉合改成不 break:`-k psrc` 165 過 8 敗。
  - 沒閉合蓋到行尾:166 過 7 敗。
  - 短寫 `pos` 多跳 3:171 過 2 敗。
  - 區塊內永不結束、區塊首行永不結束、圍欄不略過、區塊內行不換空:皆翻紅。
- F3(行號下界、倒序):已修好。拿掉下界、倒序、`hi<=n` 三種改壞都翻紅。位數不設限(`\d+`)也翻紅(`int()` 對 5000 位丟 ValueError)。
- F4(結尾沒換行):已修好。不 pop 結尾哨兵時 `t_psrc_lineno_edges` 翻紅;拿掉 CR 換行也翻紅。
- F5(NFC):已修好。出處路徑不轉 NFC 時 `t_psrc_tree_nfd_source` 翻紅。
- F6(〈用詞〉出處合格定義):已改成 `_plan_src_path_ok` 加 `_repo_ref_token_unsafe`,與第 83 行的〈依據來源〉列一致。
- 上輪沒提的目錄 `scripts/` 應擋:已進測試,預期值表仍沒有這一列,但它不在這輪五種裡,不計。

S1 的五種應擋(example.com、未來日期、行號超界、指到 repo 外的符號連結、整節在 HTML 註解裡):條款、預期值表、`t_spec_gate_sources_section` 三方標籤對得上。

F1
severity: major
blocking: 是
引句:「行內註解不跨行(刻意偏離規格):段落內跨行的行內註解,後幾行當看得見的文字」
`Systems/規格閘` 是 `scripts/lumos` 的家,它的 WHY 沒跟上這輪的新行為,而且寫的跟程式相反。
- `docs/lumos-toolchain-knowledge/Systems/規格閘.md:62` 仍寫「行中的要後面同一段真有 --> 才算」。程式現在只在同一行判,跨行分支已刪。
- 這輪的 patch 只改了同檔的首次加入日那一行,沒碰這一行。
- 同一行的 `[test:t_psrc_uncomment_inline_open]` 註解與標籤也還是「同一段」的語意。
- 失敗場景:下一個 session 讀到這行,會以為表格列或清單項的 `<!--` 與後面行的 `-->` 會成對。照它「修」就會把已刪的跨行分支加回來,這個分支連兩輪被打穿。
- 同一行還寫「_plan_tree:一次 git ls-tree …,程序內快取」,現在是走 `_drift_list` / `_drift_oids`,也過時。
- 建議:把這行改成現況(同一行才判、沒閉合照留、刻意偏離規格),`[test:]` 補上 `t_psrc_inline_same_line`、`t_psrc_inline_linear_time`。

F2
severity: minor
blocking: 否
引句:「預期值表那道(`_expected_requirement`)留所有 `.md`」
這輪新加的 `scope="note"` 機制,筆記裡綁的測試守不住。
- 實驗 A:把 `_expected_requirement` 的 `scope="note"` 拿掉,`-k t_high_risk_evidence_since` 7 過 0 敗,`-k expected` 115 過 0 敗。
- 實驗 B:拿掉 `if not keep(path): continue`,同樣兩個子集全綠。
- 只有沒綁任何筆記的 `t_psrc_first_days_note_scope` 會紅(`-k psrc` 171 過 2 敗)。
- 這輪新加的七支測試在 `docs` 裡全是零綁定:`t_psrc_lineno_edges`、`t_psrc_tree_shared_drift`、`t_psrc_tree_nfd_source`、`t_psrc_first_days_note_scope`、`t_psrc_hint_not_commit`、`t_psrc_inline_same_line`、`t_psrc_inline_linear_time`。
- 全套測試仍會抓到,所以不是漏守。但 `Systems/規格閘` 的 PITFALL 綁的 `t_high_risk_evidence_since` 守不住新機制。
- 該 WHY 行(`Systems/規格閘.md` 的首次加入日那條)明寫「預期值表那道留所有 .md」,卻沒綁 `t_psrc_first_days_note_scope`。

F3
severity: minor
blocking: 否
引句:「    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")」
`_repo_ref_source_lines` 的 CRLF 先換這步沒有測試。
- 實驗:改成只剩 `.replace("\r", "\n")`,`-k psrc` 173 過 0 敗,`-k refcheck` 204 過 0 敗。
- `t_psrc_lineno_edges` 只造了純 CR 的 `cr.py`,沒有 CRLF 檔。
- `_plan_blob` 讀的是原始 bytes,沒有經過 Python 的通用換行轉換。改壞後 CRLF 檔的行數會翻倍。
- 失敗場景:3 行的 CRLF 檔,出處寫 `file:5` 會被放行。
- `_validate_repo_ref` 的 at_sha 路徑用 `text=True` 讀,已被 Python 正規化,不受影響。

F4
severity: minor
blocking: 否
引句:「    return path.endswith(".md")」
`_plan_path_is_note` 的範圍,新測試只用 `Projects/` 底下的檔。
- 實驗:改成 `.md` 且路徑含 `/Projects/`,`-k psrc` 173 過 0 敗,`-k spec_gate` 482 過 0 敗。
- 修補理由與筆記都說「規格閘對任何節點跑」,r3 通才席實證用的是 `Systems/s.md`。測試卻沒有一支用非 `Projects/` 的節點。
- 失敗場景:`Systems/` 底下沒有 `created` 的風險高節點,首次加入日讀不到,會被當新節點、要求補預期值表。
- 因為一般節點多半有 `created`,實害有限,所以只列 minor。

未跑或判為等價的實驗:
- `git log` 拿掉 `-M`、單加 `-C` 都全綠,屬等價改動,不算 finding。git 預設 `diff.renames=true`,而 `--diff-filter=AR` 會濾掉 C 項。
- 真正讓複製被追的改法(`--find-copies-harder` 加 `ARC`,並讓解析把 C 當 R)會翻紅,`t_high_risk_evidence_since` 3 敗。
- `_plan_src_miss_reason` 第二條只看最後一段是不是符號連結(中段連結不講原因)仍全綠,只是少一句原因、不影響擋不擋,沒標。

總結:最嚴重是 `Systems/規格閘.md:62` 仍寫「同一段」跨行閉合、與這輪程式相反,會擋 1 條(另 3 條 minor 不擋)。
