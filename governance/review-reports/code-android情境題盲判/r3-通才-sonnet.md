severity: major

第二輪 13 條我逐條核對過了,F1(三方各異算進採盲判)和 F2(`--part 0` 變成第 1 份)都真的修好。表態讀取在帳裡沒有該分支紀錄時,四個讀者的行為也都合理。

- code-loop check:`rec` 是 None,往下走合併側查找,再走「缺表態」的擋。
- `--carry`:`rec or {}`,不帶舊答案。
- 盲判 `--disagreements`:作者答案是空的,印「這次沒有要盲判的段」。
- 派工鏡頭:快取 key 是空字串。

我在臨時複本(HEAD e7da27914)實測了這幾件事:

- `_ledger_lines_having` 對照 `_ledger_lines` 做 20 萬份亂數位元組帳,內含 `\r`、`\r\n`、行尾沒換行、同一行兩個字樣、U+2028、非 UTF-8 位元組,結果完全一致。
- 真實 21.7 MB、12.4 萬行的帳,`_codeloop_read_dispositions` 約 0.022 秒、峰值約 22 MB,派工鏡頭的 45 秒逾時不會被吃掉。
- `python3.14 scripts/test_lumos.py -k blind`:137 通過、0 失敗。

### F1 帳尾沒換行時,表態寫成功卻讀不回來,而本機標記檔這道保險已拿掉
引句:「f.write(json.dumps(ev, ensure_ascii=False) + "\n")」
file: `scripts/lumos:71623`(`_codeloop_gov_append`;這支沒改,但修補把標記檔的備援拿掉,它就成了表態與盲判唯一的寫入路徑)
severity: major
blocking: 是

- **輸入:** 治理帳最後一行沒有換行(寫一半、手改、別的工具截斷),再執行 `code-loop dispositions <檔>`。
- **實際:**
  - `_codeloop_dispositions_gov_log` 回 `(True, '')`,指令印「✅ 表態記下來了」。
  - 帳裡的新事件被黏在舊的最後一行後面:`{"gate":"x","kind":"y"}{"ts":...}`。
  - 這行 JSON 解不開,舊的最後一行也一起丟了。
  - `_codeloop_read_dispositions(root, "feat")` 回 None。
- **預期:** 帳尾沒換行就先補換行再寫。同一支檔的主寫入器 `_gate_event` 已經這樣做(`if _ledger_tail_needs_newline(path): line = "\n" + line`,`scripts/lumos:1850`)。
- **為什麼是這輪才變 major:** 以前本機標記檔優先,本機還讀得到剛寫的表態,只有 CI 會擋。現在標記檔不寫也不讀,本機 check、`--carry`、`--disagreements` 和派工鏡頭全部讀不到。使用者看到成功訊息卻被擋為缺表態,而且被黏掉的那一行如果是舊的 pass/skip 留痕,留痕也一起消失。
- **影響範圍:** 盲判寫入走同一支 `_codeloop_gov_append`,同樣中招。
- **修法:** 在 `_codeloop_gov_append` 寫入前用 `_ledger_tail_needs_newline`。測試要補一條帳尾沒換行的先紅案例,寫完再讀得回來。

總結:最嚴重是 major(`_codeloop_gov_append` 不補帳尾換行,標記檔拿掉後表態與盲判寫入成功卻讀不回,誤擋且可能吃掉前一筆留痕),會擋 1 條。
