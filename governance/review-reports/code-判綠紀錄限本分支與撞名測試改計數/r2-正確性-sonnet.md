severity: minor

## 結論

沒找到會做出錯行為的洞。我走了分離 HEAD、還沒有提交的 HEAD、同一個 head_sha 多筆、上限剛好 200、截止時間用完、ref 型別不對、有同名 tag、淺複製、部分複製、舊帳沒有 ref 或 head_sha 這些輸入,實際行為都跟計劃一致。只找到一條測試覆蓋缺口。

驗證方式:把修後版(6e10ae5b)與修前版(409ab14f)各解到暫存目錄。修前版的程式搭修後版的測試檔,再用 `-k` 跑。我另外手動改壞了六處,看測試會不會紅。

## Finding

1. 守衛「HEAD 解不出時不問 git」與「分支名取不到時不用名字丟」沒有任何測試釘住。

引句:「ok = bool(head) and isinstance(sha, str) and bool(_LENS_SHA_RE.fullmatch(sha))」

- 失敗場景:把 `ok = bool(head) and isinstance(sha, str) …` 的 `bool(head) and` 拿掉。還沒有任何提交的 repo,治理帳被忽略,帳裡有帶 head_sha 的紀錄。此時 head 是 None,`merge-base --is-ancestor <sha> None` 會把 None 當 git 參數傳出去。依 `_lens_git` 只接 OSError、ValueError、TimeoutExpired 推得,會丟 TypeError 一路崩出規格閘。這一點我沒實跑出崩潰。
- 另一處:把 `if isinstance(ref, str) and ref and name and ref != name:` 的 `name and` 拿掉。分離 HEAD 時所有帶 ref 的紀錄都會被丟,跟計劃天花板二寫的「分離 HEAD 只剩祖先判斷」相反。
- 我實跑這兩處改壞:`python3.14 scripts/test_lumos.py -k t_spec_gate_redbase` 都是 `60 passed, 0 failed`。
- 我手動驗過目前程式分離 HEAD 的行為是對的:帶 ref 為 featA 的紀錄,只靠祖先判斷,`[3b8a4b7, 739b400]` 都留下。
- 歸因:有證據的原有漏查。修前(409ab14f)的 `_redbase_on_branch` 已有同樣兩個守衛(`if not head or …`、`name and ref != name`),測試也沒釘,不是 r2 修補造成。
- 修前版同樣沒有測試釘住這兩處(我只在修後版跑了改壞,修前版的守衛是讀程式確認的)。

severity: minor
blocking: 否

## 修補三問

①原問題的修復效果。修前版搭修後測試檔(`-k` 逐支跑):

| 測試 | 修前版 | 修後版 |
|---|---|---|
| `t_redbase_branch_rows_fallback_keeps` | 4 條紅:超過上限的順序、部分複製三條(照留、印一句、不連遠端) | 12 條全綠 |
| `t_spec_gate_redbase_green_other_branch` | 紅:S2 同名 tag 時分支名對不上,多存了紅燈版 | 綠 |
| `t_spec_gate_redbase_green_tracked_unfiltered` | 綠 | 綠 |
| `t_spec_gate_redbase_green_tracked_unfiltered` 以外的 `t_tq_guard_string_comma_args` | 綠 | 綠 |

- 對應 behavior-cases 的 G3、G4、G5 repair 成立。
- G1(淺複製真祖先回 rc 1 照留):修前版這個案例也是綠的。修前程式本來就把淺複製判成「留」,只是判法走另一條路。所以這個案例區分不出修前修後,只能證明修後仍成立,不能證明「修前一律丟」。
- G2 是只改測試。我把 `_join` 的快取守衛拿掉再跑 `t_name_collision_scales`:`②每種串接只算一次` 紅,`{('test', True): 515, ('group', True): 515}`。1000 次呼叫只有 515 個不同物件,代表 id 會被重用,但 1000 次下仍抓得到。

②修補處的正常、錯誤與相鄰路徑。修後版跑 `-k t_spec_gate_redbase`、`t_tq_guard_cli_contract`、`t_tq_guard_string_comma_args`、`t_name_collision`,分別是 60、99、24、22 條,全綠。

- 手動改壞「完整 repo 裡 rc 1 當判不了」,`t_spec_gate_redbase_green_other_branch` 的 S6 紅。
- 有同名 tag 時分支名照樣對得上。
- 完整 repo 裡查不到的提交照丟。
- 還沒驗到的方向:修補把「判淺複製」從「git 失敗當淺複製」換成既有的 `_git_is_shallow`,它在回傳碼非 0 時回「不是淺複製」,極性反了。我只想到 git 小於 2.15 或「HEAD 解得出但 `rev-parse --is-shallow-repository` 失敗」才會踩到,後者實務上走不到。我沒有造出具體輸入,所以不當 finding,只標未驗。

③新發現的同一案例修前與修後:上面那條 finding 在修前版有同樣的守衛、同樣沒有測試,結果相同。

## 圖譜鏡頭(固定席節點)

- `Systems/lumos-cli-read`(search 預設排除 superseded)、`Systems/guard-kill`、`Systems/lumos-cli-lifecycle`、`Systems/design-loop`:這份 diff 沒碰 search、guard kill、re-inject、處置閘第五步,不影響。
- `Systems/測試假綠形態`(還原翻紅釘要有前置斷言):新測試大多有。
  - `t_name_collision_scales` 有 ★前置★。
  - `t_redbase_branch_rows_fallback_keeps` 的淺複製與部分複製有 ★前置★,過了截止時間那幾條由 ★對照★ 補。
  - `t_spec_gate_redbase_green_tracked_unfiltered`(S7)有 ★前置★。
  - S6 與 S9 沒有獨立前置,但我手動改壞「rc 1 當判不了」後 S6 確實翻紅,現場是真的。
- `Systems/pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`:本輪沒新增 pitfalls manifest,不影響。治理帳多了 `ref` 欄位。我查過 `scripts/lumos` 裡讀 `ref` 的程式只有簽核帳、回顧與 `_redbase_on_branch`,沒有會把 spec-gate 事件的 ref 當留痕讀走的讀取端。

## 已驗與未驗

- 已驗:`_lens_git_dl` 回 None 與 `_git_is_shallow` 丟 TimeoutExpired 都有接;head 為 None 時全留;截止時間用完回 None 再轉成「判不了照留」;從最新問起;去重與上限;舊帳沒有 ref 或 head_sha 時照舊留;`_redbase_attach` 先問一次忽略狀態且沒有重複問;`_TG_CONST_PAT` 加三引號後,三處 fullmatch 共用同一常數。
- 未驗:時鐘倒退;真實慢遠端(測試用留記號的腳本代替);git 小於 2.15;`kind="unknown"` 且 merge-base 仍成功的組合。我推論這個組合走不到:repo 種類在第一次問祖先前就先判,逾時時兩者一起逾時。
- 清理:只能確認 `gctl-run-7_52vqgv` 是我的,已刪。我跑改壞時另外留下的 gctl 現場無法確定歸屬,沒動,請編排者自行判斷。

最嚴重等級是 minor,blocking 共 0 條。
