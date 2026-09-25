severity: major

## F1 about_code「不在圖譜資料夾裡」是新規則,不是跟寫入指令一致;連稿子自己舉的例子都算錯類

spec 宣稱 S9 的 about_code 檢查「判法跟寫入指令(`append`、`new --code`)一樣看磁碟」,把「磁碟上存在」與「不在圖譜資料夾裡」這兩件事包成同一句話講。查程式碼:`append`/`new --code` 共用的唯一檢查函式是 `_about_code_path`(`scripts/lumos:13652-13681`),裡面只驗絕對路徑、跑出 repo 根、是不是檔案、大小寫跟磁碟一不一致——**完全沒有「不在圖譜資料夾裡」這道排除**;`root = _vault_repo_root(env).resolve()`(`scripts/lumos:13663`)比對的是整個 repo 根,不是排除 vault 資料夾。也就是說,今天用 `lumos append <節點> about_code docs/lumos-toolchain-knowledge/Projects/任一筆記.md` 會直接寫入成功(檔案存在、路徑合法、大小寫對),寫入端完全不會擋。新規則在 lint/健檢那邊卻要擋這種值——寫入端放行、lint 端擋下,是兩套標準,不是「一樣」。

稿子自己舉的違規例子就踩到這個落差:摘要 FACT 行寫「about_code 指到不存在的檔 1(Issues/把自己的推論寫成repo明文寫過 寫了一篇筆記路徑)」,把這篇歸類成「指到不存在的檔」。但實際查那篇 Issue(`docs/lumos-toolchain-knowledge/Issues/把自己的推論寫成repo明文寫過.md:11`)的 about_code 寫的是 `docs/lumos-toolchain-knowledge/Projects/中文無空白查詢回退_計劃.md`,那支檔案確實存在於磁碟(25306 bytes,`ls` 驗過)。它違規的原因是「在圖譜資料夾裡」,不是「不存在」——連盤點自己都把這唯一一條違規分錯類,說明「about_code 判法跟寫入指令一致」這個前提本身沒查證過就寫進稿子。

實作時若真的照「跟寫入指令一樣」去寫,S9 的「不在圖譜資料夾裡」這條會漏掉;若照 S9 字面實作,又跟摘要聲稱的「跟寫入指令一致」矛盾,而且寫入端會繼續放行 lint 端擋下的值(使用者用 append 寫成功、下一次提交卻被擋,體驗上是自己打自己)。這條差異該不該同步進寫入端(`_about_code_path`),整份稿子沒有一句提到。

引句:「判法跟寫入指令(`append`、`new --code`)一樣看磁碟,lint 不去掃版本控制索引」
引句:「about_code 指到不存在的檔 1(Issues/把自己的推論寫成repo明文寫過 寫了一篇筆記路徑)」
file: `scripts/lumos:13652-13681`
file: `scripts/lumos:13663`
file: `docs/lumos-toolchain-knowledge/Issues/把自己的推論寫成repo明文寫過.md:11`

severity: major
blocking: yes

## F2 lands_in 起算日「一致」只是同一個日期字串,判準基準不同

S10 說「建立日在 2026-09-12 以後的筆記沒有 lands_in」才擋,並宣稱「跟處置閘落點那一步的起算日一致」。查處置閘那支函式 `_disposal_landing_step`(`scripts/lumos:17920-17934`),它的 skip 判準是「迴圈首筆帳早於 `_LANDING_GATE_SINCE`」——看的是**審查迴圈第一筆記帳的時間戳**(`keys = [_loop_ts_key(x) ...]`、`min(keys) < _loop_ts_key(_LANDING_GATE_SINCE)`),不是計劃筆記的 `created` 欄位。而 S10 的判準是筆記自己的建立日期。兩者常數值相同(都是 2026-09-12),但比對的量不是同一個東西。

具體會不一致的場景:一篇 2026-08 建立、當初沒寫 lands_in 的舊計劃(屬於稿子自己說「之前的舊計劃 141 篇多半沒寫,不回溯」那批),如果今天(或之後)重新被派進一輪設計審查迴圈,處置閘用的是「迴圈首筆帳」時間,落在 cutoff 之後 → 會被落點步驟擋下(`bad = _lands_in_bad(items)` 或 `items` 空 → fail);但 lint 端看的是 `created` 欄位,早於 2026-09-12 → 判定不受管、不會報錯。結果是同一篇筆記在 lint/健檢那關一路綠燈,推進設計審查迴圈時卻在處置閘卡住——「起算日一致」這句話只在兩邊都不動的情況下成立,一旦舊計劃被重新啟用審查,兩套機制就會對同一篇筆記給出不同答案,而且沒有任何一處事先提醒作者。

引句:「跟處置閘落點那一步的起算日一致;之前的舊計劃 141 篇多半沒寫,不回溯」
引句:「建立日在 2026-09-12 以後的筆記沒有 lands_in」
file: `scripts/lumos:17906`
file: `scripts/lumos:17930-17934`

severity: minor
blocking: no

---
最嚴重 severity: major;blocking 共 1 條。
