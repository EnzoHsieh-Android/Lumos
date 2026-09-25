severity: clean

## 立場說明
我扮演「消費專案更新 lumos 工具後,第一個撞到這批新規則的人」。逐條檢查:錯誤訊息夠不夠讓我自己修好、跟既有健檢/lint/pre-commit/pre-push/install-update 會不會互打架、測試有沒有真的測到宣稱的路徑。用 `/tmp/lumos-review`(`git clone /Users/enzo/harness/lumos-toolchain`)做全部實驗,沒碰過原 repo 的任何寫入指令。

## 已驗過:每條新規則的錯誤訊息都給得出可執行的下一步
四條新規則(status 必填、日期格式、決策 valid、about_code 存在性、lands_in)的錯誤訊息裡建議的指令(`lumos set <節點> status <值>`、`lumos append <計劃> lands_in Systems/<名稱>`、`lumos remove <節點> about_code <值>`)在 `scripts/lumos` 裡全部真的存在且接受對應欄位:`SCALAR_KEYS` 含 `status`,`LIST_KEYS` 含 `about_code`、`lands_in`(`scripts/lumos:13266`-`13267`),`remove` 子指令存在(`scripts/lumos:13870`)。不是空頭建議。
引句:「沒填 status(寫成空白也算),篩選與健檢各段都靠它判狀態」

## 已驗過:doctor L 段擴充跟 pre-commit/pre-push 不重複報、不互打架
`pre-commit` 的 Gate L 只對「本次 staged 的那幾篇」跑 `lumos lint`(`scripts/hooks/pre-commit:99`-`103`);`pre-push` 跑 `lumos doctor --ci`,才是這批新加的「整個圖譜」掃描(`scripts/hooks/pre-push:179`)。兩層是「本地快擋 vs 推送前全圖擋」,職責不重疊,是既有分工的延伸,不是新衝突。doctor L 段本身也做了防重複:同一份 `_lint_collect` 算出的 error 會先排掉已經在原本 L 段列過的那份(`n.lint`,frontmatter 指紋),只把差集加新規則的結果印出來,不會同一個問題印兩次。
引句:「解析指紋上面已經列過,不重複」

## 已驗過:mutation test——lands_in 規則測試真的測到它宣稱的路徑
把 `_lint_new_rules` 裡 lands_in 整段判斷拿掉後,`t_lint_plan_requires_lands_in` 的 ② ③ 兩個斷言確實翻紅(其餘不受影響的照樣綠),行為跟 docstring 的翻紅釘宣稱一致(還原後我把改動的檔還原,未留在 clone 裡影響後續)。
引句:「翻紅釘:拿掉落點規則 → ②③紅」

## 已驗過:本 repo 把開關設成 on 之後,自己沒把自己絆倒
`.lumos/config.json` 這批新增了 `"note_lint": {"gate": "on"}`。用 clone 實跑 `lumos doctor --ci`(不寫回原 repo):557 篇筆記、`0 issues`,rc=0,跟宣稱一致(新增規則沒有回溯性地把既有 557 篇舊筆記卡住,因為推送前已經全部回填過)。另外全套相關單測(`-k note_lint` 等)17 案例全綠,`t_repo_graph_passes_note_lint` 直接繞過開關對整庫跑 `_lint_collect`+`_lint_new_rules` 也全過。
引句:「本 repo 開關 on,558 篇零違規,健檢多花約 0.1 秒」

## 已驗過:about_code 新規則的判斷順序與適用範圍
`_about_code_path` 新增的「在圖譜資料夾裡就擋」檢查排在既有的存在性檢查之後、大小寫檢查之前(`scripts/lumos:13809`-`13817`),不會在檔案根本不存在時搶先報成「是筆記」這種誤導訊息。`_vault_repo_root` 保證 repo 根一定是 vault 的祖先目錄而非同一層(`scripts/lumos:7425`-`7433`;測試用的 `mkvault()` 也是巢狀結構),所以「vault==repo_root 導致所有 about_code 都被誤判成筆記」這種情境在目前的節點佈局規則下不會出現,沒有找到可重現的誤擋場景。
引句:「「{v}」在圖譜資料夾裡,是筆記不是程式檔——要連結別篇就寫進 related」

## 已驗過:`lumos new` 生成的骨架不會被新規則立刻打臉
四種模板(`system`/`verification`/`issue`/`project`)在 `TEMPLATES` 裡本來就都帶 `status:` 有值(`scripts/lumos:15133`-`15146`),跟這批新增的「status 必填」規則不衝突,不會出現「一建檔立刻被自己的新規則擋」的自打嘴巴情況。`project` 模板沒有預填 `lands_in`,若使用者建的是 `..._計劃.md` 且開關為 on,建檔當下 lint 就會立刻要求補 `lands_in`——這是設計本身要的行為(逼寫落點),訊息本身已經給了指令,不算缺陷。

## 沒發現嚴重問題;實際驗過的路徑
- 四條新規則(status/日期/valid/about_code/lands_in)個別單測全綠,並對 lands_in 做過拿掉規則的翻紅驗證。
- `note_lint.gate` 四種狀態(未設/warn/on/off/壞值)的行為單測全綠,並讀原始碼確認 `warn()` 會計入 `issues`(影響 rc)、`warn_soft()` 不會(`scripts/lumos:1008`-`1043`),跟 on 擋、warn 不擋的宣稱一致。
- pre-commit/pre-push 的呼叫路徑讀過,確認新規則接進去的位置跟既有分工沒有互相打架。
- 用 clone 對本 repo 實跑 `doctor --ci`,557 篇 0 issues,確認宣稱的「開關已經打開、沒被自己絆倒」為真。
