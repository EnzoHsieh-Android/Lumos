severity: major

我只看了「一不一致」,沒找 bug。鎖檔 `…0d40e.json.warming` 不存在,不需處理。

## 第 1 問:分層與依賴方向

結論:新碼放的層對,只有範圍的來源不對(A1)。

- `_PUSH_SUMMARY_NEXT` 和 `_push_summary_next_lines` 放在 `_PUSH_SUMMARY_ANCHOR_NOTE` 旁邊,由 `cmd_push_summary` 呼叫。這和既有的「模組級對照表加 `cmd_*` 內呼叫小函式」一樣。
- 掛鉤只多傳 `--first-range`,沒有讓掛鉤直接呼叫 lumos 內部函式。鄰居用的就是這種「掛鉤傳旗標、lumos 判斷」的做法。例如 `pp_block_range_for` 呼叫 `push-range`(`scripts/hooks/pre-push:51-63`)。
- 作廢過濾放在 `_contract_key_matches`(全檔唯一的合約行掃描)和 `_impact_contract`。兩處呼叫的是 `_ns_superseded`(`scripts/lumos:46058`)。這個函式下方早就有 7 個呼叫點,例如 `scripts/lumos:4488`、`50323`、`51981`。被呼叫的函式在同一檔更早的位置定義,沒有跨層直呼。

引句:「+  _PP_CUR_RANGE="$_range"」

引句:「+                if not _ns_superseded(s.partition(":")[2]):」

## 第 2 問:命名與錯誤處理

結論:對齊,只有一處守衛比鄰居弱(A2)。

- `_PP_CUR_RANGE`、`_PP_FIRST_RANGE`、`_PUSH_SUMMARY_NEXT`、`_PUSH_SUMMARY_RANGE_RE`、`_ppc_last_line`、`t_push_summary_*`、`t_prepush_*` 都跟既有命名族一致。
- 錯誤處理也一致。`push-summary` 的規矩是「觀測失效不得改變擋下」,所以範圍不合格時寧可不印、仍回 0。這和 `pp_plain_summary` 的退路同一精神(`scripts/hooks/pre-push:135`)。
- 掛鉤新增的兩行 `下一步:` 放在既有 `} >&2` 區塊內,印法和同區塊的 `$PY scripts/test_lumos.py --ff -x` 一樣。
- 在 `_impact_contract` 裡,一處傳 `inv`(前綴後的文字),一處傳整行 `line`。兩種都能被 `slot_parse` 解析,結果相同,且有 `46071` 傳整行的先例,所以不列。

引句:「+    if not first_range or not _PUSH_SUMMARY_RANGE_RE.fullmatch(first_range):」

## 第 3 問:第二種做法

- 範圍傳法有一處不對齊,見 A1。
- 判作廢沒有發明新做法,用的是主流的 `_ns_superseded`。唯一的對照是 `_external_fact_lines` 用字面 `"[status:superseded]" in line`(`scripts/lumos:62547`)。那是先前就有的少數寫法,diff 沒有擴散它。
- ⚠ 提醒編排者:`_contract_key_matches` 與 `extract_contracts`(`scripts/lumos:5921`)兩套合約掃描並存,本來就有。diff 在兩處各補一次過濾,而不是改掉分裂。`bound-tests-gate`/`派工鏡頭` 筆記已寫明理由(`extract_contracts` 有 20 多處呼叫端)。這屬於既有分裂,我不判。

引句:「+    "drift": "lumos drift check --diff {range}",」

## A1 掛鉤餵給 `{range}` 的是 `_range`,和各閘實際用的範圍都不同

severity: major
blocking: yes

- 診斷:`_PP_CUR_RANGE` 一律用 `_range` 當「重查指令的範圍」,但各閘跑的是不同的範圍。diff 等於在掛鉤既有的三套範圍(`_range`、`_brange`、`_hrange`)之外,又加了一種「全部閘共用 `_range`」的傳法。
- 各閘實際用的範圍:
  - `home`、`note-shape` 用 `$_hrange`(`scripts/hooks/pre-push:505`、`517`)。
  - `spec-gate`、`code-loop` 用 `$_brange`(`:555`、`583`)。
  - `drift`、`room-guard`、`reread` 用 `"$_rsha..$_lsha"`,而且帶 `--push-remote --pushed-ref`(`:687`、`705`、`731`)。
- 掛鉤自己的註解明講過不要混用:
  - 「★跟上面 _range 是刻意不同的兩套★……別把兩套合併成一套」(`scripts/hooks/pre-push:487`)。
  - drift 那段寫著「不用上面的 _range」(`:680`)。
- 後果:新分支首推時,`_range` 是空樹(`EMPTY_TREE..sha`),而 `home` 等閘專門避開它。印出來的「下一步」會重查整個 repo,結果和剛才被擋的不是同一次檢查。
- 比對對象:鄰居做法是「每道閘用自己那條範圍」。要對齊,應該在每個 `pp_record_block` 呼叫點或各閘區塊裡記下那一道的範圍。
- 另外,`drift`、`room-guard`、`reread` 的重查指令少了掛鉤傳的 `--push-remote --pushed-ref`。

引句:「+  [[ "$_PP_NBLK" -gt 1 ]] || _PP_FIRST_RANGE="$_PP_CUR_RANGE"」

## A2 閘名與指令表在掛鉤和 lumos 各存一份,缺漂移守衛

severity: minor
blocking: no

- 診斷:新表註解寫「閘名與掛鉤 pp_record_block 記的一致」,結構上和 `pp_cl_reason` 同類。`pp_cl_reason` 有雙向守衛 `t_prepush_cl_reason_table_matches_lumos`(`scripts/test_lumos.py:83396`),會從 `pre-push` 原始碼抽集合來比。
- 新測試只拿 `lm._PUSH_SUMMARY_NEXT` 去比測試裡寫死的 `gates` 元組,沒有讀 `scripts/hooks/pre-push` 實際的 `pp_record_block <閘名>`。
- 結果是掛鉤新增或改名一道閘時,這張表不會紅。
- `anchor-baseline` 那條指令字串(含 `gov: 錨點簽名`)在 `scripts/hooks/pre-push:400` 和新表各抄一份,沒有守衛綁在一起。

引句:「+    "anchor-baseline": 'git add governance/anchor-baseline.json && git commit -m "gov: 錨點簽名"',」

不對齊共 2 條,其中 major 1 條。

涉及檔案:
- `/tmp/lumos-seat-work/code-推送被擋下一步/r1-code.patch`
- `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/hooks/pre-push`
- `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/scripts/test_lumos.py`
