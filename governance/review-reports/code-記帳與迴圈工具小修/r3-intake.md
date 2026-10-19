# code-記帳與迴圈工具小修 r3 收貨與處置

七席收齊後一次存檔(存檔工具已改成存全文,檔級行由 report-normalize 補);report-normalize 只做格式搬移。共 15 條(正1、邊1–3、整1–4、通1–4、架1–3;資源 clean、資安 clean):major 3 條(正1、邊1、通1,三席獨立一致指向同一處),其餘 minor。上限輪(3/3),照使用者裁定「代碼審跑滿上限時折完就合併」:全部折入,駁回 0 條,折完不再派新席,cap-decision 記 accept-risk 並寫跑滿回顧。

## 錨不到的三句引句:機械重現

| 編號 | 指令 | 輸出 | 判 |
|---|---|---|---|
| 邊界 引句#2 | `grep -n -F 'if d.get("loop") == loop_id and d.get("kind") != "spec-gate":' scripts/lumos` | `13221:                if d.get("loop") == loop_id and d.get("kind") != "spec-gate":   # 規格閘留痕不是審查輪…` | HIT(diff 外的 cmd_loop_verify_progress) |
| 整合 引句#3 | `grep -rn -F '`_jsonl_append_verified`(審查帳)直接 `open(path, "a")`' docs` | `Issues/治理帳與審查帳其他讀寫函式的硬化缺口.md:45:…與 `_jsonl_append_verified`(審查帳)直接 `open(path, "a")`,前兩支只接 `OSError`。` | HIT(diff 外的 Issue) |
| 整合 引句#4 | `grep -rn -F '真實 ID none' docs` | `Projects/載體零引句在記帳前拒收_計劃.md:36:- [S3] …包括真實 ID none（2026-10-15 起改成保留字、這個案例改驗被擋）…` | HIT(席位把全形括號打成半形) |

## 根因分組與編排者裁定(交作者照做)

- G1 讀回自驗切錯行(正1、邊1、通1,major):`_jsonl_append_verified` 讀回改走既有 `_ledger_lines`;同族一次掃:全檔所有讀帳或讀回帳檔內容的地方(不論是 read_text、decode 還是參數傳進來的字串)都不准用 `splitlines()`,把 `t_cap_retro_r3_ledger_lines_everywhere` 的原始碼守衛改成能抓到 `tail.splitlines()` 這種寫法(看函式內對帳檔內容的切行,不只看 read_text 那一種字面)。補 `--note` 分別含 U+2028、U+2029、U+0085 的記帳測試:rc0、帳上恰好一列。
- G2 帳壞分支沒測試(通2、通3):`--regression-set` 帳壞分支補一支「整本帳非 UTF-8 時印審查帳讀不懂、不印第一輪那句」的測試;`--orchestrator` 帳壞分支若對所有非結局帳呼叫都與輪次規則重複,就刪掉並在註解寫明由輪次規則統一擋,否則補一支能分辨的測試。
- G3 只讀回新寫那段沒守(通4):補一支測試,斷言讀回自驗讀到的位元組數與新寫的那段相同(攔 open 或量讀取量),把起點改成 0 要紅。
- G4 結局帳入口漏網(邊2、架1):`cmd_loop_verify_progress` 與其他直接讀審查帳的指令(canary-stats、loop list 等,逐一查)也走 `_is_outcome_row`;`_is_outcome_row` 的註解列出實際入口清單,並補 verify-progress 的測試。
- G5 照抄指令編號(邊3、架2):所有印給人照抄的迴圈編號一律走 `_rf_qloop`,包括 `_cap_retro_record_block` 與 `_retro_cmd`,不再有截斷版與整行清版;補各一支測試。
- G6 讀帳快取寫法(架3):`cmd_canary` 內的閉包快取改成跟鄰居一樣把讀到的一份當參數往下傳(`scan=`/`rows=` 形狀),不另立第三種做法;S41 讀帳次數測試照綠。
- G7 文件(整1、整2、整3、整4):`--folded-set` 說明改成現行 none 保留字規則;loop-convergence-recording 與計劃第 1 節裡「先過 _review_rows」改成現行入口濾除;硬化缺口 Issue 第③項與 reversibility-governance-ledger 的 PITFALL 照現行改(已補帳尾換行),Issue 該項標已修;載體零引句計劃 [S3] 的 none 半句改成指向 `t_canary_record_none_is_reserved_id`,`t_canary_carrier_quote_positive_controls` 的 docstring 同步。
