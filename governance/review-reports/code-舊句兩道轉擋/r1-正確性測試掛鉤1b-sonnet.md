severity: major

我對六支新測試各做了改壞實驗,另外對隔離做了環境變數實測。有三支(`t_reread_block_undecidable`、`t_reread_block_layer2`、`t_drift_ack_reread_kind`)改壞後仍照綠,其中兩條是 major,其餘是 minor。實驗都在 `/tmp/lumos-seat-work/code-舊句兩道轉擋/正確性測試掛鉤1b-sonnet/` 的三份 clone 裡跑,改完都已還原,clone 的 `git status` 是乾淨的。

## F1 淺層 clone 偵測整段拿掉,S18 綁的測試照綠
severity: major
blocking: 是
引句:「cases = (("淺層 clone", shallow, ("--diff", f"{tip2}..{tip2}"), 0),」
file: `scripts/lumos:33745`(`_note_audit_resolve` 的淺層偵測);`scripts/test_lumos.py:65767`(測試行,patch 第 828 行)
1. 改壞:把 `if sh is not None and sh.stdout.strip() == "true":` 改成 `if False:`。跑 `python3.14 scripts/test_lumos.py -k t_reread_block_undecidable`,結果 `29 passed, 0 failed`。
2. 原因:案例範圍是 `tip2..tip2`,是空範圍,沒有淺層偵測也會走到「沒有要對照的家筆記」而回 0。所以 `rc == want(0)` 兩種實作都成立,這個案例測不到淺層偵測。
3. 真實差異:我用 `git clone --depth 1 --branch feature` 造了淺層 clone,範圍給 `base..tip`、帶 `--gate`。原版回 rc0,印「淺層 clone 算不出範圍」。拿掉偵測後回 rc1,印「擋下:回頭重讀…有 3 篇守檔筆記…」。
4. 結論:S18 明定「淺層 clone 帶 `--gate` 應回 0」,守衛被拿掉後測試不紅。腳本是 `tools/shallow_exp2.py`。

## F2 `LUMOS_SKIP_REREAD_CHECK=1` 一設,新測試就紅;逃生寫法會連累掛鉤裡的全套測試
severity: major
blocking: 是
引句:「        g = m.cmd_note_audit_reread_check.__globals__」
file: `scripts/test_lumos.py:65695`(`inproc`,沒清環境變數);`scripts/lumos:35137`(單次略過在工具最前面判);`scripts/hooks/pre-push:678`(跑全套測試時沒清環境變數)
1. 實測:`LUMOS_SKIP_REREAD_CHECK=1 python3.14 scripts/test_lumos.py -k t_reread_block_undecidable`,結果 7 條斷言紅。
2. 紅的是三個②案例(各兩條,含「rc=0」)和④「紀錄總量超過上限」。原因是 `inproc` 直接呼叫 `cmd_note_audit_reread_check`,它一看到這個變數就回 0。
3. 其他新測試的 `_rr` 都有清這個變數,只有 `inproc` 漏掉,所以是漏網。
4. 影響:掛鉤逃生段教的是 `LUMOS_SKIP_REREAD_CHECK=1 git push`。掛鉤第 678 行用 `"$PY" test_lumos.py` 跑全套,環境變數會原樣繼承。⚠ 整支掛鉤端到端我沒跑(全套約 8 分鐘),這一步是讀程式推得。依此推論,在會跑到這支測試的推送上,救法會讓推送改被「test_lumos.py 有紅」擋下。
5. 對照組:`_dr` 有 pop `LUMOS_SKIP_DRIFT_CHECK`,這次漂移那條有處理,回頭重讀這條沒有。

## F3 比對字串下限 6 改成 1,S12 綁的測試照綠,且造成誤擋
severity: major
blocking: 是
引句:「    for label, quote, want in (("quote 少於 6 字 → 改用 text(那一行是 RULE)→ 擋", "推送", 1),」
file: `scripts/lumos:34358`(`_NOTE_REREAD_MATCH_MIN = 6`)
1. 改壞:`6` 改成 `1`,跑 `-k t_reread_block_layer2`,結果 `17 passed, 0 failed`。改成 12 也是 17 passed。只有改成 0 才紅(⑨)。
2. 原因:測試的「短 quote」是 `"推送"`,而且指到的那行本身就是 RULE 行,所以用 quote 或用 text 比,結果都是擋。下限的數值沒被釘住。
3. 誤擋重現(`tools/exp3.py` 的 E1):摘要有 `RULE:推送前一定要先跑全套測試…`,另有 `WHY:推送前要看 git status…`。判定列指到 WHY 那行,quote 只給 `推送前`(3 字)。原版回 rc0(只算一般行)。下限改成 1 後回 rc1,擋下的是 RULE 行。
4. 結論:守衛被改壞,測試不紅。

## F4 第二層表態「只認頂端提交的樹」沒有被測試釘住
severity: minor
blocking: 否
引句:「    acks.write_text(ack_row([fp1], 1) + ack_row([fp2], 2), encoding="utf-8")」
file: `scripts/lumos:34937`(`_drift_load_acks(root, tip)`)
1. 改壞:改成 `_drift_load_acks(root)`(讀工作目錄),跑 `-k t_reread_block_layer2`,結果 17 passed。
2. 原因:測試裡每一筆表態寫完都立刻 `_nh_commit`,從來沒有「寫了表態但沒提交」的案例。
3. 實際差異(E2):表態沒提交時,原版回 rc1,改壞後回 rc0。設計節寫「沒提交的表態不算」,逃生訊息也寫「都要提交進去才算」。
4. 降為 minor 的理由:這句寫在設計節,不是 S 條款。

## F5 規則類判定的兩個分支(superseded 排除、`KEY:★INVARIANT★`)沒有測試
severity: minor
blocking: 否
引句:「    summ = "\n".join([_RRB_RULE, "WHY:之所以這樣選是因為比較快 [出處:討論] [因:速度]",」
file: `scripts/lumos:34865`、`scripts/lumos:34867`
1. 改壞一:拿掉 `_ns_superseded(...)` 判斷,`t_reread_block_layer2` 結果 17 passed。實際差異(E3):標了 `[status:superseded]` 的 RULE 行,原版放行,改壞後被擋。
2. 改壞二:拿掉 `INVARIANT_RE.match(s)`,結果也是 17 passed。實際差異(E4):`KEY:★INVARIANT★ …` 的摘要條目,原版擋,改壞後放行。
3. 原因:測試裡的 ★INVARIANT★ 只出現在正文說明句,從沒當過摘要條目。S11 只管「正文提到不擋」這一半。
4. 設計節第 53 行明定這兩條。降為 minor 的理由同 F4。

## F6 `drift ack` 的「note 欄要等於這篇」和第二層「不論 provenance_ok」沒有測試
severity: minor
blocking: 否
引句:「          and g.get("reason") == "照留理由寫在這" and g.get("verdicts") == [fp], str(g))」
file: `scripts/lumos:37929`(note 欄比對);`scripts/lumos:34925`(第二層取紀錄)
1. 改壞一:拿掉 `doc.get("note") == note_full`,跑 `-k t_drift_ack_reread_kind`,結果 7 passed。原因是測試只有一篇筆記,別篇的紀錄不可能混進來。
2. 改壞二:第二層只收 `provenance_ok` 為真的紀錄,`-k t_reread_block_layer2` 結果 17 passed。原因是第二層測試裡沒有「來源核對沒過、但點出規則行」的紀錄。程式註解寫「不論 provenance_ok(較保守)」,這個方向沒有測試守著。
3. 這兩項我給不出比 F4、F5 更具體的失敗場景,放在這裡當記錄。

## F7 「擋下訊息講程式改了就要重判」的斷言可以被反話滿足
severity: minor
blocking: 否
引句:「    check("①擋下訊息講程式改了就要重判", "重判" in e, e)」
file: `scripts/lumos:35339` 附近(`_note_reread_print_layer1` 最後一句);訊息裡有「改筆記不用重判」
1. 改壞:把「程式改了就要重判:…改筆記不用重判。」整行拿掉,斷言紅(正常)。
2. 但只把前半「程式改了就要重判」換成別的字、留著「改筆記不用重判。」,13 條 `t_reread_block_layer1` 斷言照綠(9 passed)。
3. 原因:`"重判" in e` 被「不用重判」滿足。

## 改壞實驗總表
| 測試 | 改壞哪裡 | 紅或綠 |
|---|---|---|
| layer1 | `_note_reread_covered` 不看 provenance_ok | 紅(⑤⑥) |
| layer1 | prepare 的 `done` 改成只比檔名 | 紅(⑥) |
| layer1 | `_note_reread_uncommitted` 拿掉 committed 判斷 | 紅(⑥) |
| layer1 | `hard` 不看 `--gate`(只看 mode) | 紅(②) |
| layer1 | `hard` 不看 mode(warn 也擋) | 紅(④) |
| layer1 | 拿掉 `_note_reread_rc` 的 `if not gate: return 0` | 綠,等價改壞:`hard` 已含 gate |
| layer1 | 第一層不擋 | 紅(①③⑤) |
| layer1 | 預設 mode 改 warn | 紅 |
| layer1 | blocked 與 reminded 對調 | 紅 |
| layer1 | 擋下訊息改走 stdout | 紅 |
| layer1 | 「重判」那行只換前半 | 綠(F7) |
| layer2 | 比對下限 6→0 | 紅(⑨) |
| layer2 | 比對下限 6→1、6→12 | 綠(F3) |
| layer2 | superseded 不排除 | 綠(F5) |
| layer2 | `INVARIANT_RE` 不認 | 綠(F5) |
| layer2 | 表態改讀工作目錄 | 綠(F4) |
| layer2 | 只收 provenance_ok 為真的紀錄 | 綠(F6) |
| layer2 | 表態取聯集改成覆蓋 | 紅(⑤) |
| layer2 | 表態「子集」改成「有交集」 | 紅(④) |
| layer2 | 只取最新一份紀錄 | 紅(④);但這是靠檔名排序剛好撞上,不是穩定地測到「聯集」 |
| layer2 | 單行 summary 不補 | 紅(⑪⑫) |
| layer2 | 只認 RULE: | 紅(⑦對照組) |
| layer2 | 不認 TEST_REF | 紅(⑦對照組) |
| layer2 | 所有條目都算規則類 | 紅(⑦) |
| layer2 | 比對字串不在也算還在 | 紅(⑤⑥⑦) |
| layer2 | 接續行不併回 | 紅(⑩) |
| undecidable | 判不了照舊回 0 | 紅(9 條) |
| undecidable | 淺層偵測拿掉 | 綠(F1) |
| undecidable | 參數錯回 1,或當判不了 | 紅(⑥,3 條) |
| undecidable | 單次略過拿掉 | 紅(⑦) |
| undecidable | 非 git 專案判斷拿掉 | 紅(⑥) |
| undecidable | 沒預料例外不接 | 紅(丟例外) |
| undecidable | rows 非清單 / quote 與 text 都非字串 不檢查 | 紅 |
| undecidable | 單份上限 256KB 改成 10MB | 紅(④) |
| undecidable | 殘檔不過濾 | 紅(①③) |
| undecidable | 全 0 範圍檢查拿掉 | 紅(⑥) |
| undecidable | 讀不成 JSON 吞掉 | 紅(③⑤) |
| drift_ack | 不驗工作目錄有判定點出 | 紅(②) |
| drift_ack | text 記實體行 | 紅(⑤) |
| drift_ack | `_DRIFT_SCAN_KINDS` 含 reread | 紅(⑥) |
| drift_ack | 不記 verdicts | 紅(④) |
| drift_ack | 非規則類也收 | 紅(①) |
| drift_ack | 接續行也收 | 紅(①) |
| drift_ack | 不看 note 欄 | 綠(F6) |
| hook_and_ci | 掛鉤拿掉 `--gate` | 紅(①③) |
| hook_and_ci | `rr_rc -eq 1` 改成 `-eq 2` | 紅(④⑥) |
| hook_and_ci | 擋下後不 exit | 紅(④) |
| hook_and_ci | 拿掉 `pp_stop_if_signaled "$rr_rc"` | 紅(⑤) |
| hook_and_ci | 逃生段拿掉 `LUMOS_SKIP_REREAD_CHECK` | 紅(④) |
| hook_and_ci | 非零放行訊息拿掉 | 紅(⑥) |
| hook_and_ci | rc≠0 都擋 | 紅(⑥) |
| hook_and_ci | enforcement 不查 `--gate` | 紅(⑩) |
| hook_and_ci | record 又說「不需要表態」 | 紅(⑦) |
| hook_and_ci | `git add` 列整個資料夾 | 紅(⑦) |
| hook_and_ci | S25 提示永不印 | 紅(⑨) |
| hook_and_ci | 提示忽略 CI 環境變數 | 紅(⑨對照組) |
| hook_and_ci | CI 那步也帶 `--gate` | 紅(②) |
| old_sentence | 沒寫改固定 warn / 只看 block | 紅(11 條 / 9 條) |
| old_sentence | 壞值改固定 warn | 紅 |
| old_sentence | 壞 JSON 改 warn | 紅 |
| old_sentence | 明寫值被總開關蓋過 | 紅 |
| old_sentence | `_drift_config` 第四值恆 block | 紅 |
| old_sentence | 掛鉤又說「改 gate 沒用」 | 紅(⑨) |

分支能不能走到:各案例的 rc 之外,多數也驗了 stderr 的「擋下:」、事件種類(`ev == ["blocked"]`)和具體檔名或行號,只有兩處弱,即 F1 的 rc-only 和 F7。

`t_drift_ack_reread_kind` ⑥ 在表態沒提交時跑 `drift scan`:scan 本來就讀工作目錄,所以合理。這條斷言只驗種類計數行不含 reread(`_DRIFT_SCAN_KINDS` 改壞會紅),驗不到「scan 有讀到表態」,但我給不出具體失敗場景,不另列。

## 掛鉤逐碼走查(讀 `scripts/hooks/pre-push:536-550` 加實驗)
- **rc 0**:無輸出,往下跑。
- **rc 1**:`pp_stop_if_signaled` 放過(1 小於 128),印逃生段後 `exit 1`,不跑全套。H-b、H-c 都紅,有守住。
- **rc 2**:不是 1,印「沒能跑完…這次沒檢查」放行。H-g 紅,有守住。真實的參數錯也走這條,訊息的措辭涵蓋了。
- **rc 128、130、137、143**:全部交給 `pp_stop_if_signaled`,整支停下並原碼 exit。H-d 紅,有守住;130 另有 `t_note_audit_reread_check_wired` ⑧。
- **多個 ref**:迴圈裡第一個 rc1 就 `exit 1`,後面的 ref 這次不評估。要連續修完才會一次看全,但推送本來就被拒,不算缺陷。
- **工具 traceback**:Python 未捕獲例外是 rc1,會被當成「擋下」。我用不存在的 repo、壞範圍、空的 push 參數試過,都走得到正常出口,沒構造出 traceback,⚠ 判不準。
- **逃生訊息**:`note_reread.gate` 改 warn 的救法可行,因為工具從被推頂端讀設定。`LUMOS_SKIP_REREAD_CHECK=1` 在工具層可行,但見 F2,可能被全套測試連累。第一層「記判定紀錄、提交」不改變對照指紋,救得回。

## 隔離實測
- **`CI=true GITHUB_ACTIONS=true`**:六支全綠。
- **`LUMOS_SKIP_DRIFT_CHECK=1`**:六支全綠。
- **`LUMOS_SKIP_REREAD_CHECK=1`**:`t_reread_block_undecidable` 紅(見 F2),其餘五支綠。
- **有沒有寫到真 repo**:各份 clone 在跑完所有測試後 `git status` 乾淨,只多一個被 ignore 的 `.lumos/test-cache.json`。clone 的 `docs/.governance-log.jsonl` 曾多一行,是我手動對 clone 跑工具造成的,已還原。

## 圖譜鏡頭
派工詞說沒附固定席節點,以下是我讀這份 diff 對相關筆記的判定:
- **`Projects/舊句兩道轉擋_計劃`**:diff 的 S1 到 S26 與測試對得上,綁定測試名正確。受影響的條款是上面 F1(S18)和 F3(S12)。
- **`Projects/守檔筆記對照改動_計劃`(S7、S9)**:舊說法「只提醒、任何情況回 0、只在 130 停」被這份 diff 推翻。該筆記的 S7、S9 已改成「不帶 `--gate` 時…」並指向新計劃的 S16 到 S19、S23,測試 docstring 也同步,沒有留下矛盾。
- **README 與 `assets/drift-guard-*.svg`**:`python3.14 assets/readme-diagrams/generate.py --check` 通過,圖與生成器一致。
- **`Systems/bound-tests-gate`、漂移守衛、筆記內容審那幾篇**:diff 沒有改它們宣稱的行為。我對這幾篇只讀了 diff 本身,沒逐篇打開。

最高 major(F1、F2、F3)。
