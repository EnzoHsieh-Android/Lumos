severity: minor

我逐 hunk 挑輸入走了一遍,沒找到會讓 pre-push 誤擋或誤放的洞,找到三個會讓背書算錯或算不出來的小洞。三個都只影響「只提醒」的背書,所以都標 minor。

**沒問題的部分:**
- **`_codeloop_record_valid` 包裝:** 包裝只是把三元組去掉第三格,ok 與說法跟上游逐字一致。git 逾時、讀不懂 diff、提交找不到三個分支也都標成判不了。
- **gov load:**
  - 我跑了 `python3.14 scripts/test_lumos.py -k gov_`,116 個全綠。`-k backing` 32 個也全綠。
  - 改用逐行讀取後,帶 U+2028 的行不再被切碎,非物件行會略過,殘行停在半個中文字不會丟編碼錯誤。
  - 型別不對的行仍由 `_gov_event_types_ok` 擋掉。
- **kill-add 與 kill:**
  - 配方身分鍵改用 json 序列化再雜湊,不會有 ("a","bc") 與 ("ab","c") 撞在一起的問題。
  - `note` 預設改為 None 後,只補 covers 的路徑沒有走錯,新增配方時 `note or ""` 也正確。
  - 沙盒改成用同一個完整 sha 建立,這部分也對。

severity: minor
blocking: 否。只影響只提醒的背書,不影響推送判定。
file: `scripts/lumos:38219`。`_codeloop_bookkeeping_code` 讀 blob 時 git 出錯或逾時就回 `True`。`_codeloop_record_valid_ex` 沒有把這個情況標成判不了,而是回 `(False, "…動了代碼…", False)`。算背書時這筆紀錄就被當成「確定無效」丟掉,而它可能正是一筆 survived。結果是題目可能被誤記成強證據。`_nodehome_cat_blobs_capped` 傳入的是 `_disp_git_timeout()`,不是剩餘預算,所以 20 秒預算也可能被多吃一次。
最小重現:拿 `governance/replay/readme` 這種在簿記資料夾、沒有副檔名的檔,記錄提交到目標提交之間只動它。把 `_nodehome_cat_blobs_capped` 換成回 None 的函式後,呼叫 `_codeloop_record_valid_ex` 得到 `(False, '記錄 sha … 之後動了代碼(非純簿記增量)', False)`。不換的時候同一組輸入得到 `(True, …簿記豁免…, False)`。
引句:「        return True
    return any(head is None or _head_is_shebang(head, lenient=True) for head in blobs)」
佐證行:file: `scripts/lumos:38219`

severity: minor
blocking: 否。只是讓背書在有舊紀錄時退成「沒有」。
file: `scripts/lumos:38748`。`_backing_valid_rows` 只要 `matched` 裡有任何一筆判不了,整題就回 none。kill-log 是長期累積的,同一個測試名的舊紀錄很多。舊紀錄的提交之後被 rebase、壓縮並清掉後,`merge-base --is-ancestor` 回 128,被標成判不了。在非淺 clone 的 repo 裡,這種找不到的提交不可能是祖先,可以當確定無效。現在卻會讓同一題剛跑出來的強證據被連帶否決,原因還顯示成「版本驗證逾時或出錯」。
最小重現:在 `_backing_valid_rows` 傳入 `matched=[{head_sha:"a"*40,…}, {有效的新紀錄}]`。`_codeloop_record_valid_ex(repo, "a"*40, B)` 回 `(False, '…找不到…', True)`,整題回 `(None, "版本驗證逾時或出錯:…")`。
引句:「        if unsure:
            return None, f"版本驗證逾時或出錯:{why}"」
佐證行:file: `scripts/lumos:38748`

severity: minor
blocking: 否。只在寫 kill-log 被中途打斷後才會發生。
file: `scripts/lumos:13358`(寫入端)與 `scripts/lumos:12880`(讀取端)。kill-log 用 `open(log, "a")` 直接 append,沒有先檢查檔尾有沒有換行。上一輪被砍斷的殘行沒有 `\n`,下一輪第一筆就會黏在殘行後面,讀取端整行略過。如果被吃掉的那筆剛好是 survived,算背書時就看不到它。這是「改回 errors=replace 之後殘行與後一行」要問的情況。
重現:我寫了一個檔,內容是 `{"verdict":"killed","tail":"\xe4\xb8` 緊接 `{"verdict":"survived","n":1}\n`,再加一行含 U+2028 的物件、一行 `[1]`、一行 `{"ok":1}`。`_jsonl_tolerant_rows` 回 `[{'a': 'x\u2028y'}, {'ok': 1}]`,survived 那行不見了。U+2028 行、`[1]` 與後面的 `{"ok":1}` 都正常。
引句:「                fh.write(json.dumps({"ts": ts, "node": rel, "commit": commit,」
佐證行:file: `scripts/lumos:13358`

**圖譜鏡頭:** 這輪沒有附固定席筆記,所以沒有逐條判。

最高嚴重度:minor,blocking 0 條
