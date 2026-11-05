# r1 收貨紀錄(code-推送只跑受影響測試)

## 收貨

- 第 1 輪,分級 high(pitfalls --diff 文字輸出 tier high;改到推送前掛鉤這種把關程式),七席全 sonnet:正確性、邊界、資源、合約圖譜、通才(八角度)、架構對齊、資安(工具鏈三類)。外家席預設不派,收斂結論照實寫成「單家族視角下」。
- 七席全數交回後一次存檔(從各席逐字稿取原文,不用完成通知的跳脫版)。存檔前沒有動工作樹;收齊後 `git status` 只多了卷證目錄與治理帳(席位跑唯讀 lumos 指令留的),repo 沒被改。
- 合約圖譜席報告說它停掉背景變異實驗時還有兩個程序在它的臨時目錄;收貨時查 PID 40758、40759 已不存在,臨時目錄已刪。
- 圖譜鏡頭:本機 main 落後遠端(98dbcd775,遠端 1ac3fac37),派工鏡頭只信本機主線可達的 base,自動附加算不出;改成手動 `lumos impact --diff` 取固定席前 8 篇、在共用規則裡列名要席位自己讀。合約圖譜席用 `lumos contracts` 逐篇答了 8 篇;正確性、邊界、資源三席自承沒逐篇讀,通才只讀合約行與 PITFALL 行。這輪圖譜面靠合約圖譜席那一份。
- 資源席自承沒讀 manifest;manifest 這次只有測試檔與掛鉤上的既有 lint 項(沒有內建題),邊界、正確性兩席已判誤報。
- 派工單初版把材料寫在各席物件裡,seat-check 讀頂層 `materials`,判 vacuous;收貨時在頂層補上同一份凍結 patch 重跑。七席都報「報告沒提到材料路徑」(只觀測):席位直接引原文沒寫檔名,引句 quote-check 全錨(合約圖譜 #4 例外,見重現表)。

## 機械三道

- report-normalize:七份都已是正規化格式。
- quote-check:六份全錨;合約圖譜 5 句有 1 句(#4,README)錨不到——那句引的是掛鉤提示句加了 diff 的 + 號,README 本身不在凍結 patch 裡。
- refcheck:各席引用對得上;邊界席一個 missing 是它寫「約 61995 行」這種非標準座標。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 合1 | 合約圖譜 #1 | 掛鉤 spec-gate light 段把 `_suite_this="light"` 改成 `_suite_this="light"; _SUITE_BRANCH_DOWN=1`,跑 `-k prepush_feature_branch` | HIT:16 passed 0 failed(六支功能分支測試全綠,席位原輸出);編排者補測試後同一改壞 `-k prepush_docs_and_light` 18 passed 2 failed,還原後 20 passed |
| 合4 | 合約圖譜 #4(引句錨不到) | `sed -n 481p README.md` | HIT:「不能調的:…Lumos 自己 repo 的全套測試沒過」沒說明功能分支改由 PR 的 CI 跑 |
| 正1/合5 | 正確性 #1、合約圖譜 #5 | `grep -n 嫌久可 scripts/hooks/pre-push` | HIT:974、976 兩行全套開跑提示仍有「嫌久可 --no-verify,CI 會兜底」;計劃做法 3 列的「開跑前提示」就是這兩行 |
| 架1 | 架構對齊 #1 | 臨時 repo 改一支 .py,把 `_test_suite_for_range` 最後一條回傳的 computed 拿掉,跑 pitfalls --json --pushed-ref refs/heads/feat | 修後(直接索引)rc1、stdout 0 位元組、KeyError → 掛鉤 pf_json 空照全套;修前 `.get(…, True)` 會輸出 suite_computed true |
| 邊1/源1 | 邊界 #1、資源 #1 | 席位實跑:沒有 refs/remotes/<遠端>/HEAD、推 refs/heads/develop | HIT:pushed_mainline false;補 symbolic-ref 後 true |

refuted: none

## 先查世界

- PRIOR-ART: 缺欄位時往哪邊失敗(架1)——查 OWASP「Fail securely」(https://wiki.owasp.org/index.php/Fail_securely)與 OWASP Top 10 2025 A10 例外處理(https://owasp-top-10.pages.dev/A10_Exceptional_Conditions.html):例外與缺值要走跟「拒絕」同一條路,預設值不能讓守衛放行。採用:讀端改直接索引,缺鍵就讓 pitfalls 失敗、掛鉤照全套;不另加預設值。
- PRIOR-ART: 掛鉤兩段複製(架3/通3)——查 Google Shell Style Guide(https://google.github.io/styleguide/shellguide.html)只談函式位置與 main,沒有專講去重;採用同檔既有先例(pre-push 的 pp_range_for 註解「抽成一份免得兩處各寫」),把兩條降級條件先算出 `_down`,共用一段取關鍵字。不另立函式,因為只在一個迴圈內用一次。
- PRIOR-ART: 條款沒測試守(合1)——照專案〈實作測試品質〉與 Systems/測試假綠形態:先紅後綠,補「現場成立」前置斷言(功能分支 light 那趟真的跑 docs+keys)再斷言不印降級行。
- PRIOR-ART: 文件同步(合2–合5、通2)與同族掃描——同一類「承諾推完 CI 一定跑」的句子,掛鉤裡另有三處(檔頭 Bypass 註解、簽名不符逃生第 3 點、測試紅逃生第 2 點兩處)不在席位清單,照「同族一次掃完」一起改成「推 main 或開了 PR 才有 CI」。

## 逐條去向(10 折、6 放行、0 駁回;合5 與正1、通3 與架3 各是同一件)

| id | 席報告原條 | 去向 |
|---|---|---|
| 合1 | 合約圖譜 #1(major) | 折:t_prepush_docs_and_light_run_subset 補「推 main 不印降級行」「功能分支 light 跑 docs+keys(現場成立)且不印降級行」;掛鉤改成先判 `_down`,原本判 light 的不設 _SUITE_BRANCH_DOWN |
| 合2 | 合約圖譜 #2 | 折:bound-tests-gate 2026-09-18 那行兩處「CI 會跑全套當後盾」「CI 對 light 照跑全套當後盾」改成講明推 main 與 PR 才有 CI |
| 合3 | 合約圖譜 #3 | 折:CLAUDE.md 段首句改成「留給推送前的閘(推 main 時)與 PR 的 CI(推功能分支時)」 |
| 合4 | 合約圖譜 #4 | 折:README.md 與 README.en.md「不能調的」那句補功能分支由 PR 的 CI 跑 |
| 正1 | 正確性 #1 | 折:全套兩句開跑提示拿掉「嫌久可 --no-verify,CI 會兜底」,同族三處一起改 |
| 合5 | 合約圖譜 #5 | 折:同正1 |
| 通2 | 通才 #2 | 折:_test_suite_for_range docstring 補 computed 語意與守衛檔在功能分支會被降級 |
| 通3 | 通才 #3 | 折:同架3 |
| 架1 | 架構對齊 #1 | 折:兩處 `_sr.get("computed", True)` 改 `_sr["computed"]` |
| 架3 | 架構對齊 #3 | 折:兩段降級合成「先算 _down、共用一段」 |
| 正2 | 正確性 #2 | 放行:放行檔理由措辭不精確(「分支數沒變」與括號裡「多一個 if」),放行本身成立(兩條 C901 原本就在,假新增來自定義行改字);放行檔是留痕帳不改舊條 |
| 邊1 | 邊界 #1 | 放行:主線不叫 main/master 且遠端 HEAD 沒設才會誤判;本 repo 主線是 main,而全套降級只發生在有 test_lumos.py 的工具鏈本 repo(消費專案掛鉤不跑這套);這種分支本來就沒有 push 事件 CI,誤判不繞過任何 CI |
| 源1 | 資源 #1 | 放行:同邊1(逾時 10 秒只剩固定名,推 main 照樣判主線) |
| 安1 | 資安 #1 | 放行:同邊1族,席位自標推論;release/develop 這類分支在本 repo 不存在,計劃本意放寬範圍的邊緣 |
| 架2 | 架構對齊 #2 | 放行:判主線不看遠端名(_note_reread_mainline_names 明寫),成對要求沒有作用;旗標說明已寫「只判主線,不改 --diff 的範圍」 |
| 通1 | 通才 #1 | 放行:只改測試檔的功能分支本機不跑測試是計劃 [S6] 明寫的取捨,補償是 PR 的 CI 全套且合併前等綠 |
