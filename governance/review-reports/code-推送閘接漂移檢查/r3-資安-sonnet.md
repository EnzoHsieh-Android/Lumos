severity: clean

本席未提出 finding。以下為已驗過的攻擊面(附實驗),皆判不可利用。

## 逐項判定
1. 遠端名、ref 名當選項:`_push_mainline` 與 `_push_mainline_branch` 只把遠端名拼成 `refs/remotes/<遠端>/HEAD` 之類、開頭固定是 refs/;`_lens_git` 用參數陣列、不經 shell。實驗:在臨時 clone 對 `_push_range_start` 餵遠端名 `--upload-pack=touch /tmp/pwn`、`../../heads`、pushed_ref `refs/heads/--x`、`refs/heads/../main`,都只得到一般的「找不到主線/沒有新東西」結論,/tmp/pwn 沒被建立。`--diff` 起點另有 `_lens_range_ok` 擋開頭 `-` 與空白。
2. 路徑穿越:遠端名帶 `../` 只會讓 rev-parse 找不到 ref、退回無主線分支(舊值/空樹),不讀別處檔案。遠端名只來自本機 git 傳給掛鉤的 $1,CI 寫死 origin。
3. origin/HEAD、upstream 被改:這是本機設定,設它的人本來就能 `--no-verify`;CI 內 origin/HEAD 沒設、main@{upstream} 只在 checkout 的分支剛好是 main 時存在,且該情形正是「跳過就是這次推的那條」處理的對象。攻擊者無法在遠端側偽造 origin/main。tag 推送 pushed=None 不跳過,行為正確。
4. CI 的 env 與引號:BEFORE、SHA 走 env、`$GITHUB_REF` 為 shell 變數且加引號,沒有把 `${{ }}` 內插進 run 腳本,分支名(攻擊者可控)無法注入命令。
5. 訊號停下:rc≥128 只在被殺時發生,拿它繞閘沒有好處(停下=不放行);攻擊者要讓工具回非 0 非 1 才能在掛鉤放行,但那是本機掛鉤(本來可 --no-verify),CI 對其他非零仍是紅。
6. 未列為 finding 的既有取捨:被推送頂端的 `.lumos/config.json` 可寫 `drift_check.gate=off` 讓 CI 後盾靜默;force-push 主線且舊值不在時只查頂端最後一個提交(程式已照實說明)。兩者都不是這份 diff 新引入的,且需要有推送權限者,不交。

## 圖譜鏡頭
- 存量漂移守衛/每支檔有家/筆記內容閘/anchor-integrity(家):掛鉤改動未動它們的合約;資安面不影響。
- code-loop守衛main-direct盲區(事故):掛鉤新增訊號停下只會更嚴,不重開該盲區。
- 測試假綠形態、lumos-cli-lifecycle、lumos-cli-read(★INVARIANT★):diff 未動 re-inject sentinel、search 排除邏輯或還原翻紅釘,不影響。

最高等級:clean
