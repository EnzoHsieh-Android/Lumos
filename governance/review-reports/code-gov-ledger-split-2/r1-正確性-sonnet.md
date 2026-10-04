severity: minor

## F1 硬連結的 .gitignore 已含兩行也被警告「沒有補」
severity: minor
blocking: 否
引句:「if st.st_nlink > 1:」
file: `scripts/lumos:21057`
失敗場景(已在臨時目錄重現):
1. docs/.gitignore 是硬連結(nlink=2),內容已經有 `.governance-local.jsonl`、`.usage-local.jsonl` 兩行。
2. 跑 `_ensure_docs_gitignore(docs)`:走到 `st.st_nlink > 1` 就 `return _manual("是硬連結…")`,這一步在比對 `have` 之前。
3. 實測印出 ⚠「沒有自動補…請自己加上這兩行」,可是兩行早就在檔裡,git 也讀得到。每次 `lumos init` 或 `lumos update` 都重複印這條假警告。改版前這種情況是無聲回 `[]`。
修法方向:先讀檔、比對 `have`,缺行才因硬連結拒絕追加。

## F2 新建分支的寫入沒有接 OSError,磁碟滿會讓 init 或 update 整支崩
severity: minor
blocking: 否
引句:「with _os.fdopen(fd, "wb") as f:」
file: `scripts/lumos:21053`
失敗場景:
1. docs/.gitignore 不存在,`_os.open(... O_EXCL ...)` 成功建出檔。
2. 緊接著的 `f.write(...)` 遇到 ENOSPC 或配額用盡,丟 OSError。這段寫在 `else:` 裡,沒被任何 try 包住。
3. 例外一路穿出 `_ensure_docs_gitignore`,再穿出 `_init_additive_setup`(`scripts/lumos:21053` 呼叫處),`lumos init` 或 `lumos update` 崩潰。
4. 舊版整段包在 `except (OSError, ...)` 裡會吞掉,新版是退步。留下的空檔下次跑會走「已存在」那條補上兩行,不會卡死。
5. 這條只有磁碟滿一類的少見環境才會碰到。

## 已走過沒問題的範圍
- 暖機起點取第二早(`_gov_metric_events`):
  - 兩本帳各只有一筆時回 None,不判。
  - 同一時刻兩筆時起點等於那一刻,與批次寫入同 ts 的行為一致。
  - 帳首 1970 或 2099 的單筆壞值,`nsmallest(2)` 都不會讓護欄失效或卡死。
  - +08:00 與 UTC、沒帶時區的值都經 `_gov_ts` 轉成帶時區再比較,沒有混用問題。
- `_gov_tail_bytes` 改丟 OSError 後的呼叫端:
  - `scripts/lumos:2365` 在 `except Exception` 內,只會印「跳過」。
  - `_gov_metric_events` 的呼叫端 `_doctor_metric_lines` 有 `is_file()` 守門,S18 外層也有 `except Exception`,接得住。
- `_local_ledger_writable`:
  - 捷徑、資料夾、管線都會回 False。
  - 檢查與開檔之間被換成管線的時間差理論上存在,但要攻擊者能在 docs 寫檔,沒有可行場景,不列。
  - 三個呼叫端:`_gate_event`、`_usage_log` 有包 try;`_append_governance_log` 的檢查在 try 外,Python 3.14 的 `Path.exists` 不丟 PermissionError。
- `_ensure_docs_gitignore` 其餘分支:
  - O_EXCL 撞到同時建檔,走回已存在那條路。若對方剛建出還沒寫完,追加與對方的寫入最後內容仍完整。
  - 捷徑、非一般檔、非 UTF-8、讀不了、唯讀,各自回 `[]` 並印出正確原因與兩行。
  - CRLF 與缺尾端換行的處理正確。
- doctor 本機帳提醒改走 `_lens_git`:
  - 逾時與 OSError 回 None 會被跳過。
  - 少接的 SubprocessError 其他子類實務上不出現。
  - `--` 分隔不影響 check-ignore 的回傳值意義。

只有兩條不阻擋的小問題,其餘各路徑逐一走過後都成立。
