severity: minor

我沒等到 `--suite docs` 跑完。機器上有別的會談的測試在搶 CPU,這個任務卡在背景,所以 docs 子集的結果是未判定。其餘證據都已取得。

## F1 新測試只讀 HELP_WHEN 字典,不讀實際 `--help` 輸出,少了修補前有的一層覆蓋
severity: minor
blocking: 否

引句:「說明文字跟 parser 與 HELP_WHEN 要,不起子行程剖 --help 排版(見 _lumos_parser_tree() 的說明;剖排版會隨終端寬度斷行)。」

- 失敗場景:子命令說明的斷言 ①②只檢查 `m.HELP_WHEN["spec-gate"]`,沒碰 spec-gate 子 parser 實際會印的 description。
- `_fill_help_when` 只在子 parser 沒有 description 時才灌 HELP_WHEN。有人在 `add_parser("spec-gate", …)` 加上舊的 `description`,使用者看到的 `--help` 就會回到舊說法,測試卻照綠。
- 歸因:修補造成的覆蓋縮小,不是原有漏查。修前的測試是跑 `spec-gate --help` 再看輸出,這種情況會紅。
- 修前:舊測試實際讀 `--help`,能抓到。這個變異我沒有在修前版本實跑,只依舊測試的寫法判斷。
- 修後:我在 clone(`/tmp/lumos-seat-work/code-README與指令參考校正-std/正確性3-sonnet/repo`)的 `scripts/lumos` 把該行改成 `p = sub.add_parser("spec-gate", description="綁的測試真跑一次印紅綠(不擋)", help=…`,再跑 `python3.14 scripts/test_lumos.py -k spec_gate_help`,結果 `3 passed, 0 failed`。同時 `python3.14 scripts/lumos spec-gate --help` 印的是「綁的測試真跑一次印紅綠(不擋)」。
- 佐證:`scripts/lumos:50462`(`_fill_help_when` 的判斷是 `if not sp.description`)。
- 小補充:
  - 總表那行(斷言 ③)走 `_choices_actions` 讀 parser 物件的 help,這點跟 `_lumos_parser_tree()` 的慣例一致。
  - 但 `_choices_actions` 是 argparse 私有屬性,全檔只有這一處用到。

## F2 `lumos note-shape --staged` 放在「這幾個只列出、不擋」標題下,但它本身會擋
severity: minor
blocking: 否

引句:「lumos note-shape --staged             # the check the pre-commit hook runs; also reminds: split a line binding several tests; tag count sentences; don't point to list items as "item N"」

- 失敗場景:這個區塊的標題是「These only list, they don't block」,其他項目遇到會擋的例外都寫明了(例如「only drift fix --kind c2 --close blocks」)。
- 這一行寫「also reminds」,但沒說這支指令對新寫的程式行號引用、沒來源的現況描述會 rc1,掛鉤會因此 `exit 1`。讀者可能以為整支指令只列出。
- 證據:`scripts/hooks/pre-commit:230` 跑 `note-shape --staged`,`[[ "$ns_rc" -eq 1 ]] && exit 1`。`cmd_note_shape` 在有違規時回傳 `_note_shape_report` 的 rc。
- 歸因:未判定,偏向原有問題。修前同區塊放的是 `git commit`,同樣會被同一道擋住,所以標題不精確在修前就存在。修補是把提醒改掛到正確的指令名,說法反而更準。
- 修前:`git commit` 也被擋。
- 修後:`lumos note-shape --staged` 被擋。我只讀程式判斷,沒有實跑 rc。

## F3 `note_shape.close_summary` 的說明把觸發條件寫窄了
severity: minor
blocking: 否

引句:「commit-time reminder when a closed note's summary still says pending (same)」

- 失敗場景:實際觸發條件是「狀態從非收尾值改成收尾值,而且摘要行逐字沒變」,與摘要有沒有寫「待定」無關。
- 寫了待定的行只是在清單裡排前面並加上「← 還寫待定」。
- 一篇改成 done 的筆記,摘要沒有任何待定字眼,照樣會被提醒。依說明字面,讀者會以為不會。
- 證據:`scripts/lumos:35899` 的 `_drift_close_summary_untouched` 只比對狀態變化和 `_summ(old_text) != new_summary`,`rows = [(ln, _drift_summary_is_current(ln)) …]` 只用於排序。
- 中文版同樣寫窄:「提交時提醒結案後摘要還寫待定」。
- 歸因:修補新寫的句子,是修補自己引入的不精確。修前那列把四項併成一句「結案摘要」,沒有這個限定。
- 修前:沒有這個窄說法。修後:有。

## F4 規格閘摘要的「每次跑寫治理帳一行」忽略被擋的早退路徑
severity: minor
blocking: 否

引句:「每次跑寫治理帳一行 kind=spec-gate-run(RETIRE-IF ② 與第二階段「跑過 30 份」靠它)」

- 失敗場景:`cmd_spec_gate` 在 `_spec_gate_front` 回傳整數(句式、綁定被擋,rc1 或 2)時直接 return。相依回歸失敗和風險低放行條件沒過也是 return 1。
- 這幾種情況都在 `_append_governance_log(... "spec-gate-run")` 之前離開,不會寫帳。
- 證據:`scripts/lumos:7740` 附近的 `if isinstance(front, int): return front`,以及 `scripts/lumos:7819`(只有跑到最後才寫)。
- 歸因:有證據的原有漏查。修前的同一行就寫「每次跑寫治理帳一行」,修補只動了前半句,沒有改這個限定。
- 修前:被擋時沒有 spec-gate-run。修後:一樣。
- 我只讀程式判斷,沒有實跑被擋案例。

## 修補效果與相鄰路徑核對

**repair(原問題修復)**
- 規格閘說明測試
  - 對 `HELP_WHEN` 做四種變異,斷言都紅:放回「印紅綠(不擋)」(2 條紅)、語意寫反(1 條紅)、風險低講成不擋(1 條紅)。
  - 總表那行放回「(不擋)」和寫反各 1 條紅。
  - `COLUMNS=40` 和 `COLUMNS=200` 都是 `3 passed`。
  - 未覆蓋的缺口:把「相依功能的合約測試紅一律擋」從 HELP_WHEN 刪掉,測試仍綠(`3 passed`)。修前的測試也沒檢查這句,不算回歸。
- 開關表四列
  - 鍵名、預設 warn、值 warn / off 都對。
  - 「總開關 off 一起關」屬實:`cmd_note_shape` 在 `mode == "off"` 時早退 `return 0`(`scripts/lumos:33079` 附近),其後的 hints、tags、wording、close_summary 都不會跑。
  - 只有 F3 是描述範圍寫窄。
- `lumos note-shape --staged`
  - 確實是 pre-commit 掛鉤跑的那道(`scripts/hooks/pre-commit:230`)。
  - 三種提醒(一行綁多支測試、數量句、更正括號用「第 N 項」)都由 `_ns_wording_hints` 產生,屬實。
- doctor 兩項:S21 是指向別篇的回頭條件(提醒不擋),S20 散文撤除候選也看只掛 `[manual:]` 的計劃,屬實。
- 回放通知:`replay_weekly.py` 的 `errors` 收集補凍結 rc / timeout(`freeze:…`)和回放 rc / timeout(`replay:…`),「回放與補凍結執行出錯」屬實。
- 清點處置欄:`governance/autonomous-loop.sh` 沒帶 `--max-per-window`(預設 0 停用記帳),兩份 README 都沒提用量帳,「只記在這份清點,README 不寫」屬實。
- 規格閘家筆記:`lumos lint Systems/規格閘` 為 0 問題。PITFALL 的 `[出處:]`、`[根因:]`、`[test:]` 齊備。
- 圖譜新舊消息:摘要裡「半套不寫審查帳」已拿掉,與 FLOW 的「兩門都留 kind=spec-gate 進審查帳」一致(`_spec_gate_record` 無論風險高低都寫)。

**preserve(不應被改壞的行為)**
- `python3.14 scripts/test_lumos.py -k spec_gate`:104 passed,0 failed。
- `assets/readme-diagrams/generate.py --check`:22 份雙語 SVG 通過。
- 結構檢查
  - 兩份指令參考的程式碼區塊開合配對正常。
  - 開關表每列都是 4 欄。
  - 英文 README 連結標了「in Chinese」,目標檔 `docs/updates/2026-10-10-readme-audit.md` 存在。
- `--suite docs`:未跑完,未判定。

## 圖譜鏡頭與角色鏡頭

- 固定席各節點(design-loop、測試假綠形態、lumos-cli-read、bound-tests-gate、guard-kill、lumos-cli-lifecycle、授權與歸屬、README圖產生器等):不影響。修補只動文件、`scripts/test_lumos.py` 的一支測試,以及規格閘家筆記的摘要。
- `scripts/lumos` 沒有任何變更,沒有改任何 `★INVARIANT★` 合約行。
- 角色卡 be-api-compat、be-authz:不適用。這次沒有對外 API 欄位、沒有端點、沒有授權邏輯,只有文件文字和一支說明文字測試。

## 三問

1. 原問題的修復效果:規格閘說明已改成風險低與風險高分開講,測試能對語意寫反和放回「不擋」翻紅(上述變異實測)。開關表與回放通知的說法與程式一致(F3 是例外)。證據充分,但 `--suite docs` 未判定。
2. 修補處的正常、錯誤與相鄰路徑:正常路徑(`-k spec_gate` 104 passed)與終端寬度 40、200 穩定性都成立。相鄰路徑上,F1 的實際 `--help` 輸出已不在測試覆蓋內。
3. 新發現同案例的修前、修後:
   - F1:修前被抓,修後漏過。
   - F2:修前後都有,原有問題。
   - F3:修前沒有,修後出現。
   - F4:修前後都有,原有漏查。

最高等級:minor
