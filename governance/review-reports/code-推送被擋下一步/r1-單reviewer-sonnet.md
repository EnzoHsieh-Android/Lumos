severity: major

## 發現

### F1 範圍:新分支首推時,下一步印的範圍跟擋下那道閘實際用的不同
severity: major
blocking: yes
file: `scripts/hooks/pre-push:476`(`_PP_CUR_RANGE="$_range"`);對照 `scripts/hooks/pre-push:481`(`_brange`)與 `scripts/hooks/pre-push:496-512`(`_hrange`)

引句:「_PP_CUR_RANGE="$_range"」

- 掛鉤一個 ref 用了三套範圍。`home` 和 `note-shape` 用 `_hrange`,`spec-gate` 和 `code-loop` 用 `_brange`,`drift`、`room-guard`、`reread` 用 `$_rsha..$_lsha` 加 `--push-remote/--pushed-ref`。
- `_PP_CUR_RANGE` 卻一律記 `pp_range_for` 算出的 `_range`。
- 遠端舊值全零(新分支首推)時,`_range` 是 `空樹..頂端`,也就是整段歷史。
- 重現:用真 git 建一個有遠端 `origin` 的 repo,在 feat 分支加一個提交,再問真的 `lumos push-range`。輸出是 `cd1d6e33618b…..55212eee9b05…`(跟主線的分岔點到頂端)。`_hrange` 走 `git rev-list --topo-order --reverse $L --not --remotes | head -1`,第一個提交是 55212 本身,所以起點是它的上一個提交 cd1d6,實測 `HEAD~1` 也是 cd1d6。
- 下一步會印 `lumos home check --diff 4b825dc642cb6eb9a060e54bf8d69288fbee4904..55212…`,用的是空樹起點。照抄的人重查整個 repo 歷史(本專案有 1900 多個提交),看到的不是剛才擋下的那一筆。
- `code-loop` 的重查也不帶 `--at-sha` 和 `--branch`。`drift`、`room-guard`、`reread` 的重查不帶 `--push-remote/--pushed-ref`。推 `feat:other` 或強推時,重查的比對對象跟擋下當時不同。
- 測試漏掉這一型:`t_prepush_blocked_last_line_is_next_step` 的 stdin 是 `refs/heads/main {head} refs/heads/main {base}`,舊值非零,`_range`、`_hrange`、`_brange` 剛好全相等。把 `_PP_CUR_RANGE` 換成任何一套都照綠,新分支首推沒有測。
- 能翻紅的最小重現:在假環境用 `refs/heads/feat {head} refs/heads/feat 0000…`(舊值全零)跑掛鉤,FAKE_RCS 設 `home:1` 或 `code-loop:1`。
  - 實測最後一行是 `下一步:lumos code-loop check --diff 4b825dc642cb6eb9a060e54bf8d69288fbee4904..<頂端>`。
  - 同一次呼叫紀錄裡,`code-loop check` 本身收到的是掛鉤算好的 `_brange`,假環境的 `push-range` 沒回合格範圍,所以那次也是空樹。
  - 有遠端的真實情境下 `_brange` 是 cd1d6..55212,兩者會分開。

### F2 tag 推送被安全證據擋下時,下一步指向另一個指令
severity: major
blocking: yes
file: `scripts/hooks/pre-push:644`(`code-loop check --security-only --at-sha "$_lsha"`)、`scripts/hooks/pre-push:656`(`pp_record_block code-loop`);對照 `scripts/lumos` 的 `_PUSH_SUMMARY_NEXT`

引句:「"code-loop": "lumos code-loop check --diff {range}",」

- 推 tag 時,擋下的只有安全證據那一道,實際呼叫是 `code-loop check --security-only --at-sha <sha>`。
- 這個擋下記的閘名是 `code-loop`,所以下一步印的是 `lumos code-loop check --diff <空樹..頂端>`,不帶 `--security-only`,也不帶 `--at-sha`。
- 重現:假環境加一行 `# "--security-only"` 讓掛鉤認得該旗標,stdin 用 `refs/tags/v1 {head} refs/tags/v1 0000…`,FAKE_RCS 設 `code-loop:1`。
  - 實測最後一行:`下一步:lumos code-loop check --diff 4b825dc6…..b610c0c5…`
  - 呼叫紀錄顯示掛鉤真正跑的是 `code-loop check --security-only --at-sha b610c0c5…`
- 這個重查是完整的高風險審查判定,不是安全證據判定,看不到被擋的原因。
- 測試只驗分支路徑和 `home`,tag 路徑沒有案例。

## 其餘逐項檢查(零發現)

- 舊掛鉤配新 lumos:`first_range` 為 None,要範圍的閘不印,不要範圍的閘照印。
  - 引句:「if not first_range or not _PUSH_SUMMARY_RANGE_RE.fullmatch(first_range):」
  - 走過這兩種輸入:`--first-range ""` 回空串、沒帶旗標回 None,都進這個分支回 `[]`。
- 新掛鉤配舊 lumos:`--first-range` 不認得,argparse 回 2,掛鉤走 `pp_plain_summary`,仍然 exit 1。
  - 引句:「[[ "$ps_rc" -eq 0 ]] || pp_plain_summary」
  - 測試 `push-summary:2` 涵蓋。
- 迴圈外的閘:`anchor`、`anchor-baseline`、`doctor` 在逐 ref 迴圈之前記錄,`_PP_CUR_RANGE` 為空。
  - 引句:「[[ "$_PP_NBLK" -gt 1 ]] || _PP_FIRST_RANGE="$_PP_CUR_RANGE"」
  - `doctor` 不需要範圍。迴圈之後沒有任何 `pp_record_block`,範圍不會殘留。
- 多 ref 推送:第一筆擋下取記錄當時的 `_PP_CUR_RANGE`。實跑 `home:1,drift:1`,下一步指 `home`(測試 ②)。
- 範圍字串含特殊字元:`x; rm -rf y` 被 `fullmatch` 擋下,輸出裡沒有下一步(測試 ②)。
  - 三個點的 `a...b` 會通過 `fullmatch`,但掛鉤只傳 sha 範圍,不會遇到。
- 十道閘的指令:我手動給錯旗標(`home check --diffx`、`drift check --bogus`),真 lumos 都回 rc2 並印「不認得這幾個參數」。
  - 引句:「check(f"①{g}:真的 lumos 認得這行指令」
  - 測試的判斷字串抓得到旗標寫錯。
- 全套測試紅與自主迴圈紅的兩行下一步:實跑 `t_prepush_blocked_last_line_is_next_step`,4 條斷言過。
  - 引句:「echo "下一步:$PY scripts/test_autonomous_loop.py"」
  - 文件子集時重跑會跑整支檔,範圍變大但不會改變結果。
- 作廢濾除的寫法與大小寫:三個濾點都經 `_ns_superseded`,內部 `.lower()`,我實測 `[status:SUPERSEDED]` 也被濾掉。
  - 引句:「if not _ns_superseded(s.partition(":")[2]):」
  - 三個濾點傳進去的字串不同:`_impact_contract` 的 INVARIANT 傳的是 `INVARIANT_RE` 的 group(1),IRREVERSIBLE 傳整行,`_contract_key_matches` 傳 `:` 之後的部分。
  - 三種形狀都被 `t_superseded_contract_not_sent` 驗到,結果一致。
- 被濾掉的合約對其他呼叫端的影響:
  - `_lens_spec_node_line`(`scripts/lumos:64699`)的「M 條合約」改為排除作廢行,「N 行 KEY」仍含作廢行。這是顯示用,不影響判斷,不算錯。
  - 規格閘的 `_contract_texts` 不再綁作廢合約的測試,這是本案目的。
  - doctor、裸合約、守衛稽核走 `extract_contracts`,本 diff 沒碰。
- 錨點:`lumos anchor verify` 13 個驗證器檔案跟基準線一致。兩篇筆記 `lumos lint` 都是 0 問題。
- 三支新測試單跑都綠:`push_summary_last_line` 33、`superseded_contract_not_sent` 9、`prepush_blocked_last_line` 4。
- 固定席與角色卡:本次派工詞沒有附固定席節點,也沒有附角色卡,沒有帶殘留徽章或新增殘留的節點,這幾項略過。

最高嚴重度:major
