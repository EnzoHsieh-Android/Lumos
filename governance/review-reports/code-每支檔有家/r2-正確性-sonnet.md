severity: minor

### G1 cmd_new 的 --code/responsibility 例外路徑會印兩則重複訊息,跟同函式 plan_rels/sys_rels 段的錯誤處理不一致
severity: minor
blocking: 否 — 不影響 rc 判定(rc_own 仍正確變 2、函式仍正確回傳 2),只是訊息重複,不是會翻紅的誤擋/漏擋
引句:「提醒:筆記建好了,但 --code {relp} 沒寫進 about_code: {e}」
- 佐證:file: `scripts/lumos:12501` except 區塊先印一次「...沒寫進 about_code: {e}」,緊接 file: `scripts/lumos:12504` 的 `if _rc != 0:` 又印一次「...沒寫進 about_code(上面有原因),照原因補」——同一次失敗連印兩則。
- 同函式的 plan_rels/sys_rels 兩段(`rc_side |= cmd_append(...)` 那兩圈)遇到例外只印一則就設 rc_side,沒有這種「except 印一次、外層 if 再印一次」的雙重結構,三段本應同一套模式卻有一段多印。
- 已用真跑重現:對一個已存在的 `src/a.py` 呼叫 `cmd_new(..., code=["src/a.py"], responsibility=...)` 並讓 `cmd_append` 對 `about_code` 拋 RuntimeError,stderr 印出兩行提醒(「...沒寫進 about_code: 等了 60 秒還輪不到寫入」+「...沒寫進 about_code(上面有原因),照原因補」),rc=2。

## 第一輪修法驗收
F1:修到 — 真跑重現:新增檔喚醒舊節點裡剛好同名的檔名,擋下訊息確實改成「另開一個只改筆記的提交先改」並分兩種改法;照著兩步做(commit1 code+新家、commit2 純改筆記)後,推送前用 `--diff <base>..<tip>` 整段比對 rc0(通過),兩步走得通。
F2:修到 — 真跑重現:捷徑檔換成真的 python 檔(git 標 T)、extension-less 檔補上 `#!`(git 標 M)都會被 `home check --staged` 判成 rc1 新增沒家擋下,不再降成「舊檔只提醒」。
F3:修到 — 真跑重現:`--diff main...feature`(三個點)回 rc2「擋下:--diff 要給 <起點>..<終點>...」,不再放行;`--diff <empty-tree-sha>..<tip>`、`--diff <sha>..<sha>`(推送前掛鉤實際會組出的兩種範圍)都正確判成合法範圍、rc0/rc1 正常判定,沒有被新寫法誤判成 rc2。
F5:修到 — 真跑重現:`--staged --diff main..feature` 同給回 rc2「擋下:--staged 和 --diff 不能一起用...」,中文訊息,且判斷順序在「兩者皆無」檢查之前,不會被後者蓋掉。
F11:修到 — 真跑重現:設定 `diff.renames=copies` 後複製一支已有家的檔,`git diff --cached --name-status -M` 仍標 `A`(不標 `C`),`home check` 正確把複製出來的新檔當「新增沒家」擋下,行為本來就對,只是先前說明寫錯,這輪只改了說明。

總結:最高 severity minor,blocking 共 0 條
