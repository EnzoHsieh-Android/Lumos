severity: major

## F1 修補後的寫帳裁切仍會讓整行超過 4096,綁它的測試照綠(被一組剛好落在縫裡的輸入騙過)
severity: major
blocking: 是
引句:「nodes = _gate_event_fit(root, "note-reread", kind, note, extra, "rows", hard=hard, nodes=nodes, nodes_cap=20)」
file: `scripts/lumos:1577`(`_gate_event_fit` 預設 `head_sha=None`)、`scripts/lumos:1522-1526`(`_gate_event` 寫帳前才補 `head_sha`,事件多出 `commit` 與 `head_sha` 兩欄)
歸因:有證據的修復回歸。修前 f80352f6 同一輸入寫出 11646 位元組(紅);修後 5ce8115d 對部分輸入寫出 4120 位元組。兩版查證:`git clone` 後各跑 `python3.14 scripts/test_lumos.py -k t_reread_block_ledger_fits_4k`。

1. 根因:舊句檢查與筆記形狀擋呼叫 `_gate_event_fit` 都帶 `head_sha`(`scripts/lumos:33187`、`:40103`)。回頭重讀這一筆沒帶,所以量長度時少算「commit」(7 字元)與「head_sha」(40 字元)那兩欄,約 70 位元組。
2. 實測(修後版本):用測試同款的 30 條規則類條目,只把條目長度改成 `"很長的規則句子" * 1`,新測試的同一個斷言就紅:`(4120, {...'head_sha': '22d79f1…'})`。指令是 `mut.sh test_lumos.py r1.py t_reread_block_ledger_fits_4k`。
3. 掃描:條目數 20 到 60、引句長 30/50/80 字,共 123 組輸入,有 20 組(16%)整行超過 4096,最大 4156。腳本是 `sweep2.py`。
4. 為什麼測試照綠:測試只用一組固定輸入(30 條、每條約 560 位元組),落在 3964,剛好沒進縫裡。再用兩個放寬的改壞確認它量不出誤差:
   - 把二分上限放寬 400(`size() <= 4096 + 400`)→ 綠。
   - 把截斷門檻放寬 60(`size() > 4096 + 60`)→ 綠。
5. 這條不是文件問題:程式註解與測試名都宣稱「整行不超過 4096」,實際不成立。修法是把 `head_sha` 傳進 `_gate_event_fit`;測試補一組掃條目長度的案例。

## F2 修補在 `INDEX.md` 加了字,讓既有測試 `t_command_index_complete` 在修補提交與分支頂端都紅
severity: major
blocking: 是
引句:「drift scan·fix·ack(存量漂移:列出、工具改、照留;推送時的舊句檢查 m1 與 ack --name;回頭重讀點出的規則類條目 ack --kind reread)」
file: `scripts/test_lumos.py:8184`(斷言 `len(idx) <= 4500`)、`skills/lumos-project-notes/commands/INDEX.md`
歸因:有證據的修復回歸。查證:`git show <提交>:skills/lumos-project-notes/commands/INDEX.md | wc` 得到 f80352f6=4494、69ac44b2(主線)=4494、202da1a4(修補提交)=4525、5ce8115d=4525、88322e46(分支頂端)=4525。

1. 修前 `-k t_command_index_complete` 是 `14 passed, 0 failed`。修後與頂端都是 `13 passed, 1 failed`,失敗項是「總目錄控制在 4.5k 字元內」,值為 4525。
2. 這個變更在 `r2-repair-docs.patch` 裡,測試修補段沒有碰它。修補代理沒有跑到這支測試,推送前全套會被它擋下。
3. 另外,我用 `CI=true GITHUB_ACTIONS=true` 加全部 `LUMOS_SKIP_*` 跑全套,跑了 46 分鐘仍未結束(機器負載 6.4),我把它中止。中途看到的失敗只有這一支,沒有看到其他與環境變數有關的紅。全套沒有跑完。

## F3 `t_runner_drops_inherited_skip_env` 只觀察到一個變數,把「清掉整族 `LUMOS_SKIP_*`」縮成只清一個仍然綠
severity: minor
blocking: 否
引句:「env = dict(_os.environ, LUMOS_SKIP_REREAD_CHECK="1", LUMOS_SKIP_DRIFT_CHECK="1", CI="true", GITHUB_ACTIONS="true")」
歸因:有證據的修復回歸(修補新增的測試本身的缺口)。兩版查證:修前測試總檔帶 `LUMOS_SKIP_REREAD_CHECK=1` 跑 `-k t_reread_block_undecidable` 是 `22 passed, 7 failed`;修後清變數生效是全綠。

1. 改壞一:拿掉 `_drop_inherited_skip_env()` 這一行 → 紅(`0 passed, 1 failed`)。這一半有效。
2. 改壞二:把 `k.startswith("LUMOS_SKIP_")` 改成 `k == "LUMOS_SKIP_REREAD_CHECK"` → 綠(`1 passed, 0 failed`)。測試雖然也設了 `LUMOS_SKIP_DRIFT_CHECK=1`,但子行程只跑 `t_reread_block_undecidable`,這個變數沒有被任何斷言觀察到。
3. 洩漏的實際後果:拿掉清變數並匯出 `LUMOS_SKIP_DRIFT_CHECK/NOTE_SHAPE/CODE_LOOP/FIX_CHECK/NOTE_AUDIT/LINT_NEW`,`-k t_note_shape` 就有 `t_note_shape_ledger_rules`、`t_note_shape_revisit_needs_date_or_probe`、`t_note_shape_test_refs_index_fail_open` 三支紅(共 7 條斷言),`-k t_drift_m1` 也有 1 條紅。也就是說,同族其他變數洩漏造成的紅,這支回歸測試看不到。
4. `Systems/測試假綠形態.md:19` 寫「清掉繼承來的所有 LUMOS_SKIP_*」並把 `[test:t_runner_drops_inherited_skip_env]` 當防回歸,這個宣稱比測試實際守的範圍大。
5. 之後有人把前綴比對改成寫死的名單,漏掉新變數時,這支測試不會紅。

## F4 `_note_reread_uncommitted` 新加的四道防護沒有任何測試守
severity: minor
blocking: 否
引句:「if f.is_symlink() or not f.is_file() or f.stat().st_size > _NOTE_REREAD_VERDICT_MAX:」
歸因:有證據的修復回歸(修補新增的程式沒有配案例)。修前該函式只比檔名,沒有這些分支。

1. 改壞 W2:拿掉符號連結/非一般檔/太大那一行 → `-k t_reread_block_layer1` 綠(12 passed)。
2. 改壞 W4:拿掉資料夾本身是符號連結的判斷 → `-k t_reread_block` 綠(84 passed)。
3. 改壞 W5:不吞 `_NoteRereadStop`(形狀壞的紀錄)→ 綠。W5 若真發生,是 prepare 在「工作目錄有壞紀錄」時丟堆疊,沒有測試會抓。
4. `⑦` 只造了「形狀對、provenance_ok 為假」這一種,所以只有 provenance 那條分支(改壞 W1)會紅。

## F5 `t_hooks_path_dir_shared` 是看原始碼字串的測試,`.git/hooks` 預設分支沒有行為測試
severity: minor
blocking: 否
引句:「check(f"{fn.__name__} 用 _hooks_path_dir、自己不展開 ~", "_hooks_path_dir(" in src and "expanduser" not in src, src[:300])」
歸因:未判定。修補前後該預設路徑的邏輯相同(兩版 `hp or str(Path(".git") / "hooks")` 結果一致),所以不是修補回歸;缺口是修補時既有的。

1. 改壞 H4:把 `_enforcement_prepush_ungated` 的預設改成 `.git/hookz` → `t_hooks_path_dir_shared`、`t_reread_block_hook_and_ci_wiring`、`t_hooks_path_forms_all_recognized`、`-k enforcement` 全綠。
2. 改壞 H3:`_hooks_path_is_ours` 留一個沒用的 `_hooks_path_dir(` 呼叫、自己另算且不展開 `~` → `t_hooks_path_dir_shared` 綠,但既有 `t_hooks_path_forms_all_recognized` 紅(`~/hk` 判成 inactive),所以那一路有人守。
3. 字串檢查本身可以被「留一行假呼叫」繞過;真正的行為由別的測試守,這支只是風格釘。

## F6 `Systems/存量漂移守衛.md` 仍寫超長行用子字串判,與修補後的程式不符
severity: minor
blocking: 否
引句:「原本用純子字串,消失的名稱只是較長識別字的一段(get_user 對 get_user_id)也算有關;」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:164`(該行寫「行內以子字串出現任一這次消失的名稱的照判不了算」)
歸因:有證據的修復回歸。修前該句與程式一致;修補後程式改為整字先篩,該家筆記沒跟著改(修補的文件段改了別的筆記,沒改這篇)。

1. 這篇是 `scripts/lumos` 的家,專案規定改程式要把說明寫進家。
2. 照專案的「筆記對不上時以程式碼為準」處理:這句是線索,不是依據,需要立 Issue 或改句。

## 改壞實驗總表

| 測試名 | 改壞哪裡 | 結果 |
|---|---|---|
| t_runner_drops_inherited_skip_env | 拿掉 `_drop_inherited_skip_env()` 呼叫 | 紅 |
| t_runner_drops_inherited_skip_env | 前綴比對縮成只清 `LUMOS_SKIP_REREAD_CHECK` | 綠(F3) |
| t_reread_record_refuses_unreadable_size | `max_bytes=None` | 紅(2) |
| t_reread_record_refuses_unreadable_size | 上限乘 4 | 紅(2) |
| t_reread_record_refuses_unreadable_size | 上限 +30000(靠訊息裡的「256 KB」才紅) | 紅(1) |
| t_reread_record_refuses_unreadable_size | 上限 +100000 / +400000 | 紅(2) |
| t_reread_record_refuses_unreadable_size | 判斷式加 `and False` | 紅(2) |
| t_reread_record_refuses_unreadable_size | 拿掉 `too_big` 提示 | 紅(1) |
| t_reread_record_refuses_unreadable_size | 上限降到 1024 | 紅(1) |
| t_reread_block_ledger_fits_4k | 不走 `_gate_event_fit` | 紅 |
| t_reread_block_ledger_fits_4k | 拿掉 `nodes_cap` | 綠(`nodes_cap` 沒案例) |
| t_reread_block_ledger_fits_4k | 不記 truncated 旗標 | 紅 |
| t_reread_block_ledger_fits_4k | 二分上限放寬 400 | 綠(F1) |
| t_reread_block_ledger_fits_4k | 截斷門檻放寬 60 | 綠(F1) |
| t_reread_block_ledger_fits_4k | 輸入條目長度改成 ×1 | 紅,量到 4120(F1 證據) |
| t_hooks_path_dir_shared | 相對路徑不接 root | 紅 |
| t_hooks_path_dir_shared | 不展開 `~` | 紅 |
| t_hooks_path_dir_shared | `_hooks_path_is_ours` 假呼叫加自算 | 綠;`t_hooks_path_forms_all_recognized` 紅 |
| t_hooks_path_dir_shared | 預設 `.git/hooks` 改 `.git/hookz` | 綠(F5) |
| t_drift_m1_long_line_whole_word | 改回純子字串 | ①②都紅 |
| t_drift_m1_long_line_whole_word | 一律算有關(`hit = True`) | ①②都紅 |
| t_drift_m1_long_line_whole_word | 一律算無關(`hit = False`) | ②紅 |
| t_drift_m1_long_line_whole_word | 先篩不照截止時間 | 綠(截止時間沒案例) |
| t_reread_block_layer2 | 門檻 6 改 5 / 改 7 / 改 0 | ⑨b 紅 / ⑨c 紅 / ⑨ 與 ⑨b 紅 |
| t_reread_block_layer2 | `>=` 改 `>`(兩處各改一次) | 都是 ⑨c 紅 |
| t_reread_block_layer2 | 第二層表態改讀工作目錄 | ④b 紅 |
| t_reread_block_layer2 | superseded 不排除 | ⑨d 紅 |
| t_reread_block_layer2 | 不認 `★INVARIANT★` | ⑨d 紅 |
| t_reread_block_layer2 | 第二層只收來源核對過的紀錄 | ⑨e 紅 |
| t_drift_ack_reread_kind | drift ack 不看紀錄 note 欄 | ②b 紅 |
| t_reread_block_layer1 | `_note_reread_uncommitted` 不看 `provenance_ok` | ⑦ 兩條紅 |
| t_reread_block_layer1 | 同函式不擋符號連結/太大 / 資料夾符號連結 / 壞形狀 | 都是綠(F4) |
| t_reread_block_layer1 | 擋下訊息改字 / 拿掉「程式改了就要」前半句 | 都是 ① 紅 |
| t_reread_block_undecidable | 淺層偵測拿掉 | ⑥淺層紅 |
| t_reread_block_undecidable | 淺層原因文字改掉 | ⑥淺層紅 |
| t_reread_block_undecidable | 帳回到 `undecidable: True` | ③紅 |
| t_reread_block_undecidable | 參數錯不印「擋下:」 | ⑥ 三條紅 |
| t_reread_block_hook_and_ci_wiring | `_in_ci` 只看 `CI` | ⑨對照與 ⑨b 紅 |
| t_reread_block_hook_and_ci_wiring | 帳來源只看 `CI` / 提示只看 `CI` | ⑨b 紅 / ⑨對照紅 |
| t_update_prints_python314_notice… | 版本檢查說明只看 `CI` | ④紅 |

## 修補三問

1. 原問題的行為證據:拿修後的測試檔、搭配修前 f80352f6 的 `scripts/lumos` 跑。
   - 由紅轉綠:`t_reread_record_refuses_unreadable_size`(2 紅)、`t_reread_block_ledger_fits_4k`(紅,11646 位元組)、`t_hooks_path_dir_shared`(例外:沒有 `_hooks_path_dir`)、`t_drift_m1_long_line_whole_word`(2 紅)、`t_reread_block_layer1` ⑦(2 紅)、`t_reread_block_undecidable` ③⑥(4 紅)、`t_reread_block_hook_and_ci_wiring` ⑨b(1 紅)。修後都綠。
   - 修前就綠(preserve 案例,上面改壞實驗證明它們咬得住):layer2 的 ④b、⑨b 到 ⑨e,`t_drift_ack_reread_kind` ②b。
   - 清變數:用修前測試檔加 `LUMOS_SKIP_REREAD_CHECK=1` 跑 `t_reread_block_undecidable` 是 `22 passed, 7 failed`,證明原問題成立。
2. 既有測試是否仍守得住:D2、D3 改壞讓 `t_drift_m1_review_r3_long_lines_narrowed` 紅;H3 讓 `t_hooks_path_forms_all_recognized` 紅。但 `INDEX.md` 的變動讓 `t_command_index_complete` 變紅(F2)。
3. 新發現的同一案例修前修後:
   - 4096 裁切:修前 11646,修後部分輸入 4120(F1)。
   - 清變數:修前整族洩漏,修後只有 `LUMOS_SKIP_REREAD_CHECK` 這一支有測試證據(F3)。

## 隔離實測

- `CI=true GITHUB_ACTIONS=true LUMOS_PUSH_ATTEMPT=20261009T000000Z-12345` 匯出後跑五支新測試、`-k t_reread_block`(84 條)、`-k t_drift_ack_reread_kind`,全綠。
- 清變數只發生在 `main()` 內,而且早於 `_isolate_environment()`(`test_lumos.py:35654` 對 `:35710`),`LUMOS_SKIP_CLAUDE_PLUGIN` 之後被重設成 1,順序正確。
- 測試檔裡把 `LUMOS_SKIP_*` 當外部輸入的地方(`:34424`、`:53732`、`:70780`)都是自己設定或自己還原;`ci.yml:178` 的 `LUMOS_SKIP_BOUND_TESTS` 只在 code-loop 那一步,不在跑測試的步驟,所以清變數不會改變 CI 行為。
- `CI`、`GITHUB_ACTIONS` 沒清:兩個讀它的測試(`:62520`、`:63696`、`:65850`)自己清或自己設,實測不影響。
- slim 產物(`slim-gen.py`)不含 `_in_ci` 也不含回頭重讀函式,沒有未定義名稱。
- 全套測試在匯出環境下跑了 46 分鐘未結束(機器負載高),已中止,沒有完整結果。

## 圖譜鏡頭

- `Issues/code-loop守衛main-direct盲區`:本輪修補沒碰 pre-push 的 tier 判斷,沒有衝突。
- `Systems/存量漂移守衛`:164 行的子字串描述已過期(F6)。
- `Systems/筆記內容閘`、`Systems/每支檔有家`、`Systems/README圖產生器`、`Systems/pitfalls-code-loop`:`_note_audit_write_verdict` 只多了可選參數,預設行為不變,筆記沒有宣稱會被破壞的行為。
- `Systems/lumos-cli-read` ★INVARIANT★(search 排除 superseded):`t_search_forget_superseded` 19 條全綠,未受影響。
- `Systems/guard-kill` 兩條 ★INVARIANT★:`t_guard_kill_rc_precedence`(4 條)、`t_guard_kill_json_purity`(6 條)全綠。
- `Systems/測試假綠形態.md:19` 的 PITFALL 宣稱「清掉所有 `LUMOS_SKIP_*`」並綁 `t_runner_drops_inherited_skip_env`,宣稱範圍大於測試實際守的(F3)。
- 修補新增的五個行為(寫入上限、4k 裁切、整字先篩、hooksPath 共用、清變數)在 `舊句兩道轉擋_計劃.md` 的 S1 到 S26 裡沒有對應條款,只靠測試 docstring 的翻紅釘;「改壞某條條款」這個標準對它們無從套用。

## 未驗範圍

- 完整全套測試沒有跑完,只確認過上述子集。
- 沒有對一行極長(MB 級)文字做 `_drift_m1_line_names` 的效能與記憶體實測;改壞 D4 顯示截止時間那一路沒有測試守。
- 沒讀 `r1-*` 檔案,也沒審修補中的主程式邏輯本身(只在對照被測行為與構造改壞實驗時用到)。
- 寫入上限剛好等於 256 KB 的邊界(`>` 對 `>=`)沒有測。

工作目錄 `/tmp/lumos-seat-work/code-舊句兩道轉擋/測試假綠2-sonnet/` 已保留 `repo`、`repo2`、`repo3` 三份 clone 及改壞腳本,`repo` 已還原乾淨。

最高等級:major
