severity: minor

我這席的 Bash 在第一輪測試後遇到「磁碟已滿」(ENOSPC),之後所有指令都跑不起來,連叫子代理清自己的暫存目錄也失敗。所以下面三條都**沒能重現**,是靠讀 diff 與計劃書得出的,判不準的標 ⚠。

已經跑過的部分:在 clone 裡執行 `-k reread_block`,27 項綠、2 項紅。這 2 項是 `t_reread_block_layer2` 和 `t_reread_block_undecidable`,都死在「寫檔時磁碟滿了」,不是斷言紅。`t_reread_block_layer2` 的 ① 之後和 `t_reread_block_undecidable` 的全部斷言這次沒有實際跑到。我也沒做「把程式改壞看測試會不會紅」的實驗。

## F1 S18 的「淺層 clone」案例用空範圍,測不到淺層偵測
severity: minor
blocking: 否
引句:「("淺層 clone", shallow, ("--diff", f"{tip2}..{tip2}"), 0),」
file: `scripts/test_lumos.py`(diff 內 `t_reread_block_undecidable` 的 `cases`)

1. 淺層案例的範圍是 `tip2..tip2`,起點等於終點,本來就是「範圍沒有新東西」,帶不帶 `--gate` 都該回 0。
2. 把淺層 clone 的偵測整段拿掉,這個空範圍仍會回 0,所以 `⑥[S18]帶 --gate、淺層 clone → rc0` 與不帶 `--gate` 的對照照綠。
3. 真正的淺層情境是範圍起點 `b2` 不在淺層歷史裡。偵測壞掉時,那種情境在 `--gate` 下會落到「終點找不到」回 2,或落到「判不了」回 1 而擋人。這條路徑沒有測試守。
4. ⚠ 我沒讀到真檔裡淺層偵測放在「解析範圍」之前還是之後,沒能實際拿掉偵測來驗證。
5. 改法:淺層案例改用 `f"{b2}..{tip2}"`(淺層 clone 裡拿不到 `b2`)。

## F2 `drift scan` 計數那一條斷言,可能在沒有表態的情況下就綠
severity: minor
blocking: 否
引句:「種類計數不出現 reread", head and "reread" not in head」
file: `scripts/test_lumos.py`(diff 內 `t_drift_ack_reread_kind` ⑥)

1. ⑤ 之後 `drift-acks.jsonl` 只寫在工作目錄,沒有提交,然後才跑 `drift scan`。
2. 如果 `scan` 只讀已提交樹裡的表態,或者標題列只列計數大於 0 的種類,把 `reread` 加進 `_DRIFT_SCAN_KINDS` 的改壞版本也不會讓 ⑥ 翻紅。
3. 結論 ⚠:我沒能確認 `scan` 讀的是工作目錄還是已提交樹,也沒能確認標題列怎麼列種類。要證明 ⑥ 有殺傷力,需要「先 `_nh_commit` 表態檔,再把 `reread` 加進 `_DRIFT_SCAN_KINDS` 看是否翻紅」的實驗。

## F3 行程內呼叫沒有隔離 `LUMOS_SKIP_REREAD_CHECK`,本機和 CI 結果可能不同
severity: minor
blocking: 否
引句:「rc = m.cmd_note_audit_reread_check(repo=str(r), diff_range=diff or f"{base}..{_na_head(r)}", gate=gate)」
file: `scripts/test_lumos.py`(diff 內 `t_reread_block_undecidable` 的 `inproc`)

1. 同一份 diff 裡經 `_rr` 的路徑會 pop 掉 `LUMOS_SKIP_REREAD_CHECK`、`CI`、`GITHUB_ACTIONS`。
2. `inproc` 是直接呼叫函式,沒有清環境變數。
3. 開發者本機若 export 了 `LUMOS_SKIP_REREAD_CHECK=1`(S19 規定它回 0 並記 skipped-env),②「讀不到清單、逾時、例外」那三組的 `rc == 1 and ev == ["blocked"]` 就會在本機變紅、在 CI 保持綠。
4. 這是環境漏進測試,不是假綠。⚠ 我沒確認 `cmd_note_audit_reread_check` 是在函式內讀環境變數,還是只在 argparse 入口讀。

## 其他鏡頭

**掛鉤正確性**,逐項走過的結果:
- 只有 `set -u`,沒有 `set -e` 和 `pipefail`,所以 `|| rr_rc=$?` 有效。
- 回傳碼 0:放行。
- 回傳碼 1:印逃生段並 `exit 1`。
- 回傳碼 2:舊工具不認 `--gate`,印「這次沒檢查」後放行。
- 回傳碼 130、137、143:都被 `pp_stop_if_signaled` 在 128 以上攔下並 `exit` 原碼。137(被系統砍掉)現在會整支停推,這是計劃書明寫的刻意翻案,不算缺陷。
- 多個 ref 時,第一個擋下就 `exit 1`,跟 drift 那段處理一致。
- 標準錯誤不再丟掉,舊工具下會多印 argparse 的用法說明;掛鉤註解已寫明是已知雜訊。
- 逃生訊息所教的救法:`LUMOS_SKIP_REREAD_CHECK=1` 單次略過、`note_reread.gate` 改 warn 要提交進被推的提交,與計劃書〈輸出〉一致。
- 沒找到能當場翻紅的洞。
- 測試對應:`t_reread_block_hook_and_ci_wiring` 的 ④(回 1)、⑤(143)、⑥(回 2)分別對應三種分支,都已跑過且全綠。
- `FAKE_RC_CMD` 只在 `c == "note-audit"` 時觸發,不會誤傷其他假閘。

**測試隔離**:`_rr` 新增 pop `GITHUB_ACTIONS`,補得對。唯一的隔離缺口是上面的 F3。

**圖譜鏡頭**,逐條判定,這份 diff 不破壞下列節點宣稱的行為或合約:
- `Issues/code-loop守衛main-direct盲區`:不影響。diff 只在 code-loop 之後多接一段 reread-check,沒碰 code-loop 的 main-direct 判斷。
- `Systems/存量漂移守衛`:會作廢該節點「m1 沒寫是 warn、不跟 gate 走」的 RULE。diff 只改程式與測試,筆記標 superseded 屬別段改動。⚠ 本席沒看到那部分,筆記是否同批更新請另席確認。
- `Systems/筆記內容閘`、`Systems/pitfalls-code-loop`、`Systems/每支檔有家`:不影響。沒動它們宣稱的合約,只動了掛鉤的 reread 段和 README 圖產生器。
- `Systems/README圖產生器`:`generate.py` 改了兩列的徽章、一個標籤和中英描述,長度夠放。⚠ 我沒確認 repo 裡是否有已提交的 SVG 需要同批重產,以及是否有比對測試。
- `Systems/lumos-cli-read` ★INVARIANT★(search 預設排除 superseded):不影響。diff 沒碰 search。
- `Systems/guard-kill` ★INVARIANT★(rc 優先序、`--json` 純度):不影響。diff 沒碰 guard kill。
- 超出上限只列名的節點:沒逐條判,不影響。

三條 finding 全部是未重現的 minor,沒有 major 以上;本席沒找到能讓目前 diff 的測試或掛鉤出錯的證據。

最高嚴重度 minor。
