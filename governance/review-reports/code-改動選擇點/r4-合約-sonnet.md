severity: minor

## k1 測試分不出「取最後一段」和「取第一段」
severity: minor
blocking: 否。壞法是合理的改壞,測試照綠,但被保護的 `類別.方法` 行為在該 fixture 下兩種取法結果相同,講不出具體會出錯的下游場景,所以降一級。

- **輸入**:`_choice_test_blobs` 把 `FooTest.bar` 這類名字,用 `n.rsplit(".", 1)[-1]` 取最後一段 `bar` 去 `git grep`。
- **改壞**:把 `[-1]` 改成 `[0]`,變成找類別名 `FooTest`。
- **結果**:`t_choice_test_blobs_name_shape` 6 條全綠。fixture 的 `FooTest.kt` 同時含 `FooTest` 與 `bar`,兩種取法找到同一支檔。
- **失敗場景**:方法定義在不含類別名的檔裡(繼承的基底測試類、`@Nested`),取第一段會找不到,守的測試所在檔記成不明。
- **預期 vs 實際**:預期該測試有一條案例讓「方法名只在不含類別名的檔裡」,取第一段時變紅;實際沒有。
- 其餘三種改壞(整串 -F、句子名也取最後一段、查表不用 `term[n]`)都有紅。

引句:`term = {n: (n.rsplit(".", 1)[-1] if _dotted_ident(n) else n) for _p, n in keys}`
file: `scripts/lumos:77933`(`_choice_test_blobs`)
歸因:有證據的原有漏查(新寫的測試沒釘到),不是修復回歸。
- 修前 `dbdc038`:dotted 名整串找,查不到、記成不明。
- 修後 `24ec789`:改為取最後一段,6 條全綠。
- 取第一段的變異體:測試仍綠。

## k2 新增的兩支測試沒有任何計劃條款綁定,計劃正文也沒寫這兩個行為
severity: minor
blocking: 否。文件對不上,但不會讓推送被擋或做出錯的行為,屬措辭層。

- **事實**:計劃 S11 只綁 `t_choice_kill_incremental`,正文沒寫「`類別.方法` 取最後一段」。計劃條款 S1–S26 沒有任何一條寫整批掃描不套忽略規則,所以 `t_choice_scan_batch_no_ignore`、`t_choice_scan_batch_share`、`t_choice_kill_partial_unverified_rc` 都沒有條款釘。
- **只在 Systems/規格閘 的 PITFALL 行有指到**:`t_choice_test_blobs_name_shape`、`t_choice_scan_batch_no_ignore`、`t_choice_kill_test_files_in_test_paths`。
- **完全沒有任何節點引用**:`t_choice_scan_batch_share`、`t_choice_kill_partial_unverified_rc`。
- **案例表錯位**:r4-behavior-cases.md 把 J2 的 `t_choice_scan_*` 標成出自 S19。S19 其實是「只看 B 版本」那條,跟掃描無關。這份案例表是審查材料,不是 repo 檔。
- 三個月後的人從條款或預期值表,找不到新行為由哪支測試守。

引句:`- [S11] 當同一行已有有效處置,choice-kill 應 跳過;已 survived 而守的測試沒變的行 應 不重跑`
file: `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md:206`
歸因:未判定。這是修補新增的缺口,但修前本來也沒條款,所以不能算回歸。

## 三問回答

**① 原問題的修復效果**
- **整批 `--no-ignore`**:變異體 `_CHOICE_SG_NO_IGNORE = ()` 等於修前行為。`t_choice_scan_batch_no_ignore` 兩條都紅,真 ast-grep 在 `.gitignore` 寫 `*.kt` 的目錄下結果是 `{'a/A.kt': 0, 'b/B.kt': 0}`(修前行為重現)。修後 12 支 `choice_scan` 全綠,兩條斷言通過。拿掉 `parent` 一種時,假 ast-grep 那條紅,真 ast-grep 那條仍綠,所以六種旗標由假 ast-grep 那條守。本機 ast-grep 0.51.2 的 `scan --help` 有 `--no-ignore` 六種值。
- **`類別.方法`**:變異體整串找時 `FooTest.bar` 是 `?`(修前行為),3 條紅。修後 `choice_test_blobs` 6 條全綠。
- **拿掉推送前時限底線**:`_choice_requirement` 先用同一個 cache 算過 `("spec", rng, at_sha)`,`_choice_guard` 必命中,見 `scripts/lumos:77785`。`_choice_requirement` 走到判碰到的計劃之前就回傳的路徑,是 `not need`,整圈直接 skip 不進 `_choice_guard`。我沒有造 cache 沒命中的案例,也沒有只改 cache 參數的變異實驗;`spec_gate_push_choice` 42 支全綠。

**② 正常、錯誤與相鄰路徑**
- `choice_kill_incremental` 6、`choice_kill_rerun_rules` 11、`choice_kill_test_files` 19、`spec_gate_push_choice` 42,全綠。
- `guard_kill_rc_precedence` 4、`guard_kill_json_purity` 6,全綠。
- 以上都只跑修後版本;修前版本只用變異體重現,沒有另外在修前 commit 上跑這些子集。

**③ 新發現的案例在修前、修後各是什麼**
- k1:修前沒有這條測試,無法比較。修後那支測試對取第一段的變異體仍綠。
- k2:屬文件缺口,修前修後都沒有條款綁定。

## 圖譜鏡頭
- 尾端沒附固定席節點,只能自己判。
- Systems/guard-kill 的兩條 `★INVARIANT★`(`t_guard_kill_rc_precedence`、`t_guard_kill_json_purity`):不影響。修補差異沒碰 `cmd_guard_kill` 與 guard-kill.md,只改 `_choice_*`,兩支綁定測試修後仍綠。
- Systems/規格閘 與計劃筆記的說明句已跟著改:
  - `--no-ignore` 六種;
  - `類別.方法` 取最後一段;
  - 兩條新 PITFALL。
- 全庫 grep 再找不到殘留的 `_CHOICE_GUARD_FLOOR` 或底線說法。

## 未驗範圍
- 沒跑不帶 `-k` 的全套。
- 沒做真 Android 專案的端到端耗時驗證。
- 沒驗整批輸出超過 64MB 退逐檔、約 450 支以上大檔的時限情形。
- 暫存副本 `/tmp/lumos-seat-work/code-改動選擇點/合約-sonnet/` 已刪。

最嚴重:minor;blocking 共 0 條
