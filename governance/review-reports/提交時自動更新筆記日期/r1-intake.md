preflight-4: ran

# 提交時自動更新筆記日期 r1 前掃

前掃一席(sonnet,臨時 repo 實跑):①3 條(rtb/D4 未解釋、Gate UB 新名、部分暫存沒判準)②`_summary_line_rebuild` 不在本分支、03 檔改 updated 那句位置不明 ③2 條(被擋後已改的留在索引沒寫、訊號那句與 home check 規矩矛盾)④6 條語意命中。不動核心裁定(Enzo 裁提交時自動改),直接修真檔。

| 類 | 修改前 | 修改後 |
|---|---|---|
| ④ 最重 | 掛鉤裡 git add 一律可行 | `git commit <路徑>` 時 git 用臨時索引(實測:提交含改動、真正暫存區沒有,事後狀態 MM);改成偵測 GIT_INDEX_FILE 不是預設就跳過並講一句 |
| ④ | 照 home check 規矩、被訊號中斷停下 | pre-commit 沒有訊號處理慣例,刪掉停下那句,只照 rc1 擋、其他放行 |
| ④ | --diff-filter=AM | 改名又改內容會漏(實測狀態 R);加 --no-renames |
| ④ | 只認 MERGE_HEAD | cherry-pick、revert、rebase、merge --squash 也跳過 |
| ④ | git diff --quiet 不為 0 就算部分暫存 | 只認回 1,2 以上當工具出錯 |
| ④ | 每篇兩次 git show | 沿用 note-shape 的 `_nodehome_reader` 與 `_nodehome_cat_blobs` |
| ② | 改 updated 照 `_summary_line_rebuild` | 那支在別的分支,改成自寫一支只換那一行的小函式 |
| ③ | 沒寫被擋後已改的會留在索引 | 實務隱患補一條 |
| ① | 名詞 | 補部分暫存判準、Gate UB 標明新增、出處改白話 |

## 六席收貨

六席收齊才判讀。三道:引句全錨;報告已正規化(架構對齊席一行等級旁的 ⚠ 由 report-normalize 搬成獨立一行)。多條有兩席以上各自實跑(索引判法:正確性、邊界、整合、回滾、簡化五席;設計審整檔指紋:回滾、整合兩席)。Enzo 2026-10-06 看過這輪摘要後改裁「健檢列出加一鍵修」,提交掛鉤整段拿掉,下列發現全部隨之消失,記為折。

| id | 一句 | 重現 | 去向 |
|---|---|---|---|
| c-F1 | 預設索引沒定義,worktree 每個提交被跳過 | HIT:席位實跑 | 折:方向改成不碰提交 |
| c-F2 | -a 被誤判成指定路徑提交 | HIT | 折:同上 |
| c-F3 | 純改名被洗成今天 | HIT | 折:同上 |
| c-F4 | amend 比對基準 | HIT | 折:同上 |
| c-F5 | 擋下訊息教 git add 抵銷 add -p | HIT | 折:同上 |
| b-F1 | 索引判法 | HIT | 折:同上 |
| b-F2 | 檔名萬用字元 | HIT:席位實跑 | 折:同上 |
| b-F3 | CRLF 正文比對恆為有改 | HIT | 折:同上 |
| b-F4 | amend 看不出、基準錯 | HIT | 折:同上 |
| b-F5 | worktree 狀態檔位置 | HIT | 折:同上 |
| b-F6 | 400 篇 29 秒 | HIT:席位實跑 | 折:同上 |
| b-F7 | updated 欄寫法沒定義 | HIT | 折:新版走 lumos set 的寫入路徑 |
| b-F8 | NFC 與換行檔名 | HIT | 折:方向改成不碰提交 |
| b-F9 | 沒有原子寫入 | HIT | 折:新版走 lumos set 的寫入路徑 |
| b-F10 | 取消提交後 updated 不復原 | HIT | 折:方向改成不碰提交 |
| i-F1 | -a 被一起跳過 | HIT | 折:同上 |
| i-F2 | 設計審整檔指紋會失效 | HIT:`_hash_chain_check` | 折:同上;新版實務隱患寫明審中計劃審完再跑 |
| i-F3 | 自寫換行繞過寫入原語、併發帶進半成品 | HIT | 折:新版走 lumos set 的寫入路徑、不 git add |
| i-F4 | autocrlf 誤判 | HIT | 折:方向改成不碰提交 |
| i-F5 | 改過的判準跟 home check 不一致 | HIT | 折:同上 |
| i-F6 | updated 既有消費者訊號變鈍 | HIT | 折:同上 |
| i-F7 | 純改名、首次提交、amend 基準 | HIT | 折:同上 |
| i-F8 | worktree 狀態檔 | HIT | 折:同上 |
| i-F9 | 單次跳過不記帳 | HIT | 折:新版沒有跳過開關 |
| i-F10 | 版本錯位噪音、效能、lands_in | HIT | 折:方向改成不碰提交 |
| r-F1 | 索引判法 | HIT | 折:同上 |
| r-F2 | 多會談 git add 帶進半成品 | HIT | 折:同上 |
| r-F3 | 半成品與 rc≥128 | HIT | 折:同上 |
| r-F4 | 設計審整檔指紋失效 | HIT:`scripts/lumos` 第 10275 行 | 折:同上 |
| r-F5 | 悄悄消掉翻案提醒 | HIT:`scripts/lumos` 第 2486 行起 | 折:同上;新版由人手動跑,跟手改日期一樣 |
| r-F6 | 日期倒退 | HIT | 折:新版只改成今天、已是今天跳過 |
| r-F7 | amend 基準 | HIT | 折:方向改成不碰提交 |
| r-F8 | 沒有長期關閉開關 | HIT | 折:同上 |
| r-F9 | updated 行寫法、CRLF | HIT | 折:新版走 lumos set |
| r-F10 | 測試沒有時鐘注入 | HIT | 折:新版測試用跟工具同一個本機日期算法 |
| r-F11 | 天花板沒列被跳過的提交形態 | HIT | 折:方向改成不碰提交 |
| s-F1 | 預設索引判法 | HIT | 折:同上 |
| s-F2 | 部分暫存擋下帶出一串零件 | HIT | 折:同上 |
| s-F3 | 跳過條件可合併 | HIT | 折:同上 |
| s-F4 | 跳過開關記帳 | HIT | 折:同上 |
| s-F5 | REVISIT 量測沒意義 | HIT | 折:拿掉 |
| s-F6 | 新頂層指令同步五處 | HIT | 折:新版仍要一個指令,同步清單寫進範圍 |
| a-F1 | 另寫換行函式繞過寫入原語 | HIT | 折:新版走 `_cmd_set_locked` |
| a-F2 | 直呼 git diff、另刻合併判法 | HIT | 折:方向改成不碰提交 |
| a-F3 | 跳過沒記帳、首道改檔掛鉤無前例、lands_in | HIT | 折:同上 |
