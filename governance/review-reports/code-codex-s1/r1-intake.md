preflight-4: ran

# r1 收貨紀錄(code-codex-s1,standard)

## 前掃
- 代碼迴圈無四類前掃;manifest 見 r1-manifest.json;patch 行數見 dispatch 當下紀錄。

## 外家否決(Codex)5 條(4 major 1 minor;引句 4/5 錨定,#5 錨不到不入 set、內容仍折)
- #1「輪次邊界不只 event_msg/user_message」HIT:今日逐字稿 event_msg/user_message 27 筆、response_item/message role=user 54 筆(含系統注入的 recommended_plugins 與真使用者輸入;順序 R,R,E),exec 模式兩種都在但不能只認一種 → 折入:兩種都當邊界(反向掃遇到任一即停)。
- #2「exec_command 有 {cmd:} 無引號形」HIT:`grep -oh 'tools\.exec_command({[^:]*:'` 今日 31 筆有引號、30 筆無引號、1 筆換行縮排 → 折入:正規式 `["']?cmd["']?\s*:`;真逐字稿重驗抽到。
- #3「席號用 remaining 推算會撞號」HIT(理論競態,席自陳未能穩定重現):折入:席號=token 檔自己的編號(tok-02→第 2 席),測試手動認領 01、03 後 claim 得 2。
- #4「驗收把單一形狀外推成已讀懂真逐字稿」HIT:折入:驗證筆記改寫(只證當時那一個形狀;#1/#2 兩形狀補進 fixture),fixture 版本守衛不變。
- #5 四個模式旗標互斥(minor):折入 argparse 層擋 rc2。
## 架構對齊 3 minor(嚴重度行正規化後 12 行;引句 6/11 錨定——錨不到的 5 句多為引既有碼或多行拼接,不入 set)
- (1) SubagentStart 分支失敗路徑補 `_debug`(對齊同檔 main)。(2) `_lens_cache_path` 的 repo 部分改 realpath,與 `_lens_repo_key` 同一種算法(舊快取自然 miss)。(3) `_lens_arm_dir_ok` 補 group/other 不可寫檢查(對齊 `_lens_cache_read`)。
## 單reviewer 6 條(4 major 2 minor;引句 6/6、行號 10/10)
- F1(major)HIT:單檔 Claude 路徑 timeout 被多檔預算縮成 19.99(mock 量到)→ 折入:`len(paths)==1` 固定 30;紅測 `s1-r1④`。
- F2=外家 #3、F3=外家 #2、F4=外家 #1、F5=外家 #5(同題,已折;席各自獨立重現,互為佐證)。
- F6(minor,測試品質):並發測試視窗窄抓不到 F2 → 席號改 token 編號後競態不存在;測試改為手動認領 01/03 後驗第 2 席(確定性)。
- 派工鏡頭:席回報尾端既無「lumos 自動附加」也無「圖譜沒有釘到節點」——base `aeb0aea` 是未推的本機 commit、不在主線 Lumos/main 歷史上,hook 照設計靜默放行(rc4 路徑);不是缺陷,是本輪 base 選法的代價(下次用 Lumos/main..HEAD 再由席自己剔 S0 部分,或先推 S0)。
