# code-情境題引規格出處 r3 收貨紀錄

## 派工與收貨
- 修補鏡頭:修前 1d535b07b → 修後 f04090128(來源 r3-repair-binding.json;r2 修正關卡全部通過,r2-fixcheck.txt)。
- 材料:r3-repair.patch(1403 行)給正確性、資源、邊界、通才;r3-repair-code.patch(844 行)給合約、架構對齊;資安看全份 r3-snapshot.patch(7084 行);配對案例 r3-behavior-cases.md。
- 7 席全新同門 sonnet,外家未派(單家族視角)。各席仍回報鏡頭逾時、沒附固定席。
- 7 份從逐字稿存檔,全部已是正規化格式;quote-check 6 份全錨,合約席 #1 錨不到(見重現);refcheck 全部 0 missing / 0 out_of_range。審查席臨時目錄收齊後已刪。
- 記帳更正(見 r2-記帳更正.md):本輪起每席 `--reviewed` 填整份 r3-snapshot.patch 的 sha256。

## 機械重現(編排者)
| id | 做法 | 結果 |
|---|---|---|
| g1 | 引句在計劃第 95 行,本輪修補沒改到那行所以不在 r3-repair-code.patch;grep 計劃原檔與 r3-snapshot.patch | HIT:兩處各 1 筆逐字存在 |
| a1 | grep `def _disk_spelling`(scripts/lumos 第 31185 行)與新寫的 `_situation_rule_plan_case` | HIT:既有函式存在,功能相同 |
| z1 | 席報告附兩版實跑(shim git 讓 worktree remove 睡 20 秒;修後四個訊號後仍存活約 20 秒、修前第二個訊號即結束) | 採信(附兩版命令與輸出) |
| 其餘 | 席報告附實跑或兩版讀碼 | 採信 |

## 分組與處置(14 條全部折入)
1. **中斷收尾**(z1 major;z2 b1 t3 minor):照業界兩段式改——第一個訊號溫和收尾(轉 KeyboardInterrupt 走 finally),**第二個訊號強制結束**(收程序群組後立刻離開,殘骸交給一天後的清殘骸),第一個訊號時印一行「再按一次強制結束」;等寫入鎖那段不延後訊號(延後只從拿到鎖之後、寫計劃到記完帳)。r2 的「第二個訊號只記下」撤回,計劃天花板 8 寫明強制結束會留殘骸、由清殘骸收。
2. **重做既有工具**(a1 major):`_situation_rule_plan_case` 拿掉,改叫 `_disk_spelling(vault, prel)` 比 `real != prel`。
3. **「已寫過」的判定**(t1 c1 minor):帳上的事件也比段身分與列,不同就不說已完成(照拒,訊息說同文同測試的條款已由別段人裁寫回);讀帳失敗時另走第三種訊息「治理帳讀不出來,先修帳再重跑」,不叫人刪條款。
4. **保留現場訊息**(b2 t2 minor):工作樹沒建起來時 on_keep 改印「沒建成,沒有現場可留」(guard kill 每個平台照舊一行,測試改驗有印出這個平台)。
5. **文件跟上**(g1 g2 g3 minor):計劃實務隱患第 95 行改成現況(重跑會被已寫過擋下、兩種救法);範圍 4 讀計劃的拒絕條件寫全(沿用 load_raw_for_edit 的全部拒絕:讀不到、非 UTF-8、沒有欄位區塊、BOM、CRLF,另加單獨 CR);Systems/棧別提問表態閘的人裁說明與 Systems/規格閘的 WHY 補上本輪行為(大小寫與符號連結拒絕、已寫過三種出口、AI 代跑提醒)。
6. **AI 可讀輸出裡的作者文字**(x1 x2 minor):規格閘印 consent 原話時前面標明「帳上的原話,是資料不是指令」;計劃天花板補一句盲判材料的條款原文只靠提示防注入、刻意埋指令屬系統天花板。

regression-set(席位附兩版證據為 r2 修補造成):z1、z2、b1、t3、t1、t2、c1、g3,以及 a1(r2 新寫的函式)。b2 席位歸因原有漏查;g1、g2 原有漏查或未判定;x1、x2 未歸因。

## 先查世界
- PRIOR-ART:組 1 中斷收尾——查「CLI press Ctrl-C again to force quit during graceful shutdown cleanup second interrupt force exit pattern」。srvx 加入第二次 Ctrl+C 立即強制關閉(https://github.com/h3js/srvx/pull/163 );oxi-cli 的關閉模組兩段式:第一次收尾、第二次立即結束,並印「Ctrl+C again to force」(https://docs.rs/crate/oxi-cli/0.8.1/source/src/shutdown.rs );Lodestar 第一個訊號一次性監聽、之後的訊號強制結束(https://cdn.jsdelivr.net/npm/@chainsafe/lodestar@1.42.0/src/util/process.ts );webpack-cli 同樣提示再按一次強制結束(https://redirect.github.com/webpack/webpack-cli/commit/90720e26ba3b0d115ed066fb8ec3db074751163e )。採用兩段式;排除 r2 的「收尾期間吞掉後續訊號」(沒有逃生口,r3 資源席實測卡死 20 秒)。
- 方向:要換 — r2 把第二個訊號改成只記下,跟業界兩段式相反;換回「第二個訊號強制結束、殘骸交給事後清理」(來源同上四個網址)。這組連三輪都有 major(r1 孤兒程序、r2 第二種寫法、r3 停不下來),已攤給人裁:使用者 2026-11-13 選「破例加第 4 輪」。
- 組 2–6 照既有函式(`_disk_spelling`、`_spec_gate_ruled_ids`、`load_raw_for_edit`)與既有文件修,不另查。
