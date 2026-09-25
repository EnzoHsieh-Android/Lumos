severity: major

## F1 about_code 新規則宣稱「跟寫入指令同一種判法」,但寫入端根本沒有「不在圖譜資料夾裡」這條檢查

S9 要求 about_code 每一項「不在圖譜資料夾裡」,並宣稱判法跟 `append`/`new --code` 一致、只是看磁碟。實際查 `_about_code_path`(scripts/lumos:13652-13681,`append`/`new --code` 共用的唯一寫入端驗證)只檢查:非絕對路徑、解析後仍在 repo 內、目標是檔案、大小寫跟磁碟一致——全程沒有任何一步排除「在 docs/lumos-toolchain-knowledge(圖譜資料夾)裡」的路徑。也就是說,只要那個路徑是一支存在的檔,寫入端現在、以後都會放行,不會提醒也不會擋。

這不是空想:圖譜裡現存的那一條違規正是這樣寫進去的——`docs/lumos-toolchain-knowledge/Issues/把自己的推論寫成repo明文寫過.md:11` 的 `about_code:` 指到 `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md`,這支檔在磁碟上真實存在(25306 bytes),所以當初用 `append` 寫入時完全過關。計劃摘要的 FACT 行把這條違規歸類成「about_code 指到不存在的檔 1」,但那支檔其實存在,真正的問題是「檔案存在但在圖譜資料夾裡」——連這條計劃自己盤點時都把違規原因寫錯了,可見這個新限制目前完全是 lint 專屬、寫入端從未真的比照。

引句:「判法跟寫入指令(`append`、`new --code`)一樣看磁碟」
引句:「about_code 不查版本控制索引(r2):lint 只看單篇筆記,不掃 repo;跟寫入指令用同一種判法」

severity: major
blocking: yes

實作完這個功能之後,任何人再用 `lumos append <節點> about_code docs/lumos-toolchain-knowledge/某篇.md` 都還是會成功寫入、零提醒——下一次 `lumos lint` 或健檢才會報錯,跟「跟寫入指令同一種判法」的宣稱矛盾。要嘛把 `_about_code_path` 也補上這條限制,要嘛把宣稱改成「只有 lint 端多這條、寫入端目前沒有」。

## F2 S10 落點規則的起算日跟它宣稱比照的處置閘,量的其實是兩個不同的時間點

S10 用筆記自己的 `created` 欄位跟 2026-09-12 比,並宣稱「跟處置閘落點那一步的起算日一致」。但處置閘那一步(`_disposal_landing_step`,scripts/lumos:17920-17934)量的起算日不是計劃筆記的 `created`,而是**設計迴圈帳本第一筆紀錄的時間戳**(`tss = [str(r.get("ts", "")) for r in rows ...]`、`min(keys) < _loop_ts_key(_LANDING_GATE_SINCE)` 才 skip)。這兩個判準只是門檻值(2026-09-12)相同,依據的欄位完全不同。

具體會誤判的情境:一篇 09-12 以前建立的舊計劃(lint 的 S10 判定「更早的計劃不受影響」,不會報 lands_in 缺漏),之後在 09-12 之後才第一次進設計迴圈重審——處置閘會因為迴圈帳本的首筆時間戳晚於 09-12 而要求它補 lands_in、沒補就 fail;可是同一篇筆記拿去跑 `lumos lint` 或健檢,S10 完全不會提醒。這代表「lint 乾淨」不保證「處置閘會過」,跟計劃反覆強調的「跟處置閘同一支判斷、同一個起算日」矛盾——這句話只對「格式判斷」(`_lands_in_bad`)成立,對「要不要管這篇」的起算日並不成立。

引句:「跟處置閘落點那一步的起算日一致」
引句:「之前的舊計劃 141 篇多半沒寫,不回溯」

file: `scripts/lumos:17906`(`_LANDING_GATE_SINCE` 常數)
file: `scripts/lumos:17930-17934`(處置閘用迴圈帳本 ts、不是筆記 created 欄位判起算日)

severity: major
blocking: yes

## F3 決策 valid 欄位「不寫」時該不該算錯,spec 沒講清楚,跟現有兩套讀法都對不上

S8 只規定「valid 不分大小寫後不是 true/false 就報」,沒講 valid 欄位整個不存在時算不算數。現有程式碼對這件事本身就有兩種不同對待:`fmt_decision`(scripts/lumos:12276)讀值時用 `d.get("valid", "true")` 當預設,沒寫 valid 一律當 ✅ 有效顯示,不當錯誤;但 `cmd_decision_supersede`(scripts/lumos:14077-14078)遇到同一種情況(`valid_line is None`)卻直接 `raise ValueError`,判定「工具不敢自動翻案」。

如果照字面實作 S8(`str(d.get("valid")).lower() not in ("true","false")` 這種寫法),`d.get("valid")` 在鍵不存在時是 `None`,`str(None).lower()` = `"none"`,會被判成違規——這會把「沒寫 valid、目前讀成有效」的既有寫法(手改過、沒走 `lumos decision-add` 的決策項)全部打成 lint error,跟 `fmt_decision` 的容忍讀法直接衝突。目前圖譜 125 條決策全部都有寫 valid(機械查證,0 缺漏),所以這個落差還沒炸;但 S8 沒有明講「沒寫算不算」,兩種實作(嚴格報錯 vs 沿用 fmt_decision 的預設 true)都說得通,卻會導致完全不同的行為,spec 应该挑明。

引句:「只能是 true 或 false,不分大小寫(跟現在讀的地方一致:它們都先轉小寫再比)」

file: `scripts/lumos:12276`(`fmt_decision` 對缺 valid 的預設「true」)
file: `scripts/lumos:14077-14078`(`cmd_decision_supersede` 對缺 valid 直接拒絕,兩套現行行為不一致)

severity: major
blocking: yes

最嚴重 severity: major;blocking 共 3 條。
