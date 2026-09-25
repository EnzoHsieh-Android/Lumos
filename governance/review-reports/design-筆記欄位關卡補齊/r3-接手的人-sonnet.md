severity: major

## F1 about_code 新規則說「跟寫入指令一樣看磁碟」,但寫入指令根本沒有「不在圖譜資料夾裡」這條檢查——append 會悄悄成功,commit 才被擋

`做法`第二節寫 about_code 的判法「跟寫入指令(`append`、`new --code`)一樣看磁碟,lint 不去掃版本控制索引」,暗示 lint 新規則跟寫入端是同一套判準、行為一致。但寫入端 `_about_code_path`(`scripts/lumos:13652`)只驗「repo 相對路徑」「檔案存在」「大小寫跟磁碟一致」,完全沒有「不在圖譜資料夾裡」這一條;而 S9/做法二明確要求 lint 多驗這條。也就是說,今天在任何接了 lumos 的專案打 `lumos append <節點> about_code docs/xxx-knowledge/Projects/某計劃.md`,CLI 會直接印「✓ append」成功寫入——不會有任何警告。等到下一次 commit(gate=on 時)或往後 CI,lint 才第一次告訴你這個值是錯的。

這不是臆測:repo 現在就有一個真實案例證明寫入端漏了這條檢查——`docs/lumos-toolchain-knowledge/Issues/把自己的推論寫成repo明文寫過.md` 第 12 行 `about_code: - docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md`,這是一篇筆記路徑,能寫進去代表當初 `append` 沒有擋。計劃書的`做法`裡沒有任何一條提到要同步修 `_about_code_path` 加這條例外,`不做的`/`不在本案範圍`兩節也沒提到這個落差要不要修。對「接手的人」來說,這正是「lumos update 完,昨天的 append 沒事,今天 commit 被擋、只看得到 lint 訊息」的典型場景,而訊息本身也不會提示「你昨天的寫入指令本來就該擋卻沒擋」。

severity: major
blocking: yes

引句:「about_code:每一項要是磁碟上存在的檔,而且不在圖譜資料夾裡(筆記不是程式檔)。寫成單一字串而不是清單的,當成只有一項。判法跟寫入指令(`append`、`new --code`)一樣看磁碟,lint 不去掃版本控制索引。」

file: `scripts/lumos:13652-13670`(`_about_code_path`,寫入端驗證,無圖譜資料夾排除)
file: `docs/lumos-toolchain-knowledge/Issues/把自己的推論寫成repo明文寫過.md:11-12`(真實案例:about_code 指到筆記路徑,append 當初沒擋)

## F2 「9 篇違規」用的起算日跟規則本身寫的起算日對不上,9 篇裡有 5 篇落在規則管不到的區間

`摘要`FACT 行寫「09-11 起建、檔名以「_計劃」結尾卻沒寫落點 9 篇」,`做法`第五節逐篇點名這 9 篇要在這次改動裡補 `lands_in`。但 S10 與`做法`第二節都明講新規則「只管...建立日在 2026-09-12 以後的」。實際查這 9 篇的 `created:` 欄位,有 5 篇是 `2026-09-11`(紀律範本二次瘦身、代碼審資安席、推播miss量測、Python補棧、skills提示工程優化),不是 2026-09-12 以後——照 S10 字面,這 5 篇根本不在新規則的管轄範圍內,不寫 `lands_in` 也不會被擋。

這代表「9 篇」這個數字本身用的是跟規則不一樣的起算日(FACT 用「09-11 起」,規則用「09-12 以後」),兩處讀者會得出不同的落點規則邊界:照 S10 實作出來的人只會抓到 4 篇(空轉週報誤報復發 09-14、社群規則覆蓋每次提交 09-13、Flutter補棧 09-13、Java補棧 09-12),跟`做法`第五節列的 9 篇對不上。把多出的 5 篇也順手補齊不會出錯,但邊界定義本身自相矛盾,會讓照 S10 寫測試/程式碼的人跟照 FACT/步驟五核對數字的人得到不同答案,而且未來一篇 09-11 建立、沒寫 lands_in 的計劃(理論上跟這 5 篇同一批)不會被新規則擋下,卻沒人在誠實界線裡講清楚這個邊界差一天的後果。

severity: major
blocking: yes

引句:「計劃必須有 `lands_in`:只管 `type: project`、檔名以「_計劃」結尾、而且建立日在 2026-09-12 以後的(跟處置閘落點那一步的起算日一致;之前的舊計劃 141 篇多半沒寫,不回溯)。」

file: `docs/lumos-toolchain-knowledge/Projects/紀律範本二次瘦身_計劃.md:4`(`created: 2026-09-11`)
file: `docs/lumos-toolchain-knowledge/Projects/代碼審資安席_計劃.md:4`(`created: 2026-09-11`)
file: `docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:4`(`created: 2026-09-11`)
file: `docs/lumos-toolchain-knowledge/Projects/Python補棧_計劃.md:4`(`created: 2026-09-11`)
file: `docs/lumos-toolchain-knowledge/Projects/skills提示工程優化_計劃.md:4`(`created: 2026-09-11`)

## 其餘段落

一、健檢 L 段擴充:已讀、無 finding——`scripts/lumos:1196-1206` 的 L 段目前確實只印 `n.lint`(解析指紋),跟摘要描述一致;`_read_touched_list`(`scripts/lumos:974`)證實 L 段本來就不吃 touched,S5 的宣稱不影響現況。

三、專案開關 `note_lint.gate`:已讀、無 finding——沿用 `node_home.gate` 的三態與「看不懂當 on」跟 `_nodehome_config`(`scripts/lumos:21436-21462`)行為一致,可查證。

四、`lumos set responsibility`:已讀、無 finding——`_cmd_set_locked`(`scripts/lumos:13569`)目前對 `responsibility` 完全沒有長度/實字檢查,`_nodehome_resp_ok`(`scripts/lumos:21492`,10 字門檻)只用在 `new system`(`scripts/lumos:15052`)與每支檔有家段落,補進 `set` 確實是填補沒人查的洞,做法可行。

決策 `valid` 布林:已讀、無 finding——全圖譜 124 篇含 `decisions:` 的筆記,`valid:` 出現處全部已是 `true`/`false`(大小寫不拘),跟 FACT「0 條違規」吻合,S8 描述與現況一致。

實務隱患段:已讀、無 finding——四類風險逐條答覆(金流/對外送出/不可逆已排除,守衛面/舊筆記已承認並附開關降級路徑),符合鐵則四要求。

最嚴重 severity: major,blocking 共 2 條。
