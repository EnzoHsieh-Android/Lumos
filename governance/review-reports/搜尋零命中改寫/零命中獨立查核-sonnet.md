# 調查報告:過去一個月 `lumos search` 0 筆情況(乾淨 agent 獨立查核,2026-09-11;問題原樣給、不給編排者的數字與結論)

## 怎麼找的

掃了 `~/.claude/projects/` 底下三個對應目錄(lumos-toolchain 本體、governance 子目錄、LandmarkMember)共 2280 份 Claude Code 逐字稿,以及 `~/.codex/sessions/2026/08` 與 `2026/09` 共 393 份 Codex 逐字稿(按 cwd 篩出屬於這兩個 repo 的部分)。從 Bash/exec 工具呼叫裡抓出指令文字含 `lumos search` 的那些,配對回它們的輸出,先用「共 N 篇候選」「(候選 N;…)」(較舊版措辭)「"candidates": N」等機器可判的標記自動分類零/非零,再對自動判不出來的(多個查詢黏在同一次呼叫、輸出被 `head` 截斷、fallback 訊息交錯等)逐條人工核對原始輸出,必要時用同一指令裡其他查詢詞的結果互相印證(例如同一段同時查中文詞跟英文詞,能直接看出是不是換個說法就找得到)。

## 總量與 0 筆次數

| 來源 | 查詢次數(約) | 0 筆次數 | 看不出結果(輸出被截等) |
|---|---|---|---|
| Claude Code · lumos-toolchain | ~1716 | 71 | 個位數(≤10,多半靠上下文還原出來了) |
| Claude Code · LandmarkMember | ~27 | 8 | 0 |
| Codex · lumos-toolchain | ~116 | 2 | 0 |
| Codex · LandmarkMember | 0(找到 7 場 session 但沒人跑過 `lumos search`) | 0 | 0 |
| **合計** | **~1859** | **81** | **少量** |

另外發現 10 次「不算 0 筆,但也沒查到東西」的情況,不計入上面 81 次:LandmarkMember 有 7 次是忘記加引號(`lumos search 對帳 儀表板` 這種,中文詞黏著空白會被 argparse 當成多餘參數直接報錯,根本沒跑到搜尋邏輯);Codex 有 3 次是用了不存在的旗標 `--limit`(正確旗標是 `--top`)。這兩種都是「用法錯誤」,不是「搜尋跑了但沒東西」。

## 81 次 0 筆逐一分類

**(a) 真的在找概念、用詞對不上(這功能能救的)—— 34 次**

| 查詢詞 | 專案 | 備註 |
|---|---|---|
| 效能鏡頭 安全鏡頭 沒有鏡頭負責 | lumos-toolchain | |
| 圖譜同步覆蓋點名 sync-only | lumos-toolchain | |
| 提交後 自動複查 | lumos-toolchain | ×2(同一天查兩次) |
| 使用紀錄 | lumos-toolchain | 兩字黏著沒空白 |
| 推播漏網量測怎麼算冷卻窗 | lumos-toolchain | 同指令內換成「推播 漏網 冷卻」就找到 |
| 引用率 | lumos-toolchain | |
| 通用不變量層 | lumos-toolchain | |
| post-checkout | lumos-toolchain | ×2;同指令內查中文說法(hooks/錨點)找得到 |
| quickstart | lumos-toolchain | 同指令內查「教學」「上手」都找到,查英文字面沒有 |
| unverified-push | lumos-toolchain | ×2 |
| bypassPermissions | lumos-toolchain | |
| 死人開關 | lumos-toolchain | 同指令拆成「心跳 排程」就找到 |
| shuffle | lumos-toolchain | ×2;同指令查「測試 隨機」找到 |
| 治理過頭 | lumos-toolchain | ×4(同一詞不同天被查了 4 次都 0) |
| 你是不是要找 | lumos-toolchain | |
| requires_core | lumos-toolchain | 同指令查「核心 掛載」找到 |
| 人派人 工具記帳 | lumos-toolchain | |
| 智財 版權 | lumos-toolchain | |
| 新手上手指南怎麼裝 | lumos-toolchain | |
| 供應鏈 | lumos-toolchain | |
| spec-driven | lumos-toolchain | 同指令查「spec 驅動 開發」找到 |
| 基準圖 | lumos-toolchain | |
| holdout 保留組 | lumos-toolchain | |
| risky hasAssertions | lumos-toolchain | 同指令查「無斷言 測試」找到 |
| 會員登入流程 | LandmarkMember | ×3(不同天各查一次都 0,同一詞) |
| VoucherLinkIncomplete | LandmarkMember | 同指令查「綁券 不完整 拆列」找到 |

**(b) 故意測工具行為 / 查測試函式名·日期·版本號這種本來就不在筆記裡的東西 —— 40 次**

主要是:`t_bad_command_gives_near_name_not_wall_of_text`(測試函式名)、`作廢訂單點數怎麼收回`(×4,CLAUDE.md 自己舉的範例,反覆用來驗證黏字提示訊息)、`薛丁格 貓量子 疊加態呀`、`こんにちはせかい`(日文測試字串)、`龘靐 齉爩`(刻意挑生僻字測 CJK 判斷)、`zzqxj不存在的詞`/`zzzz不存在的詞qqqq`/`zzzz-no-such-term-912837`/`這個詞絕對查不到的字串xyzzy12345`/`quokkazzzz whompiter blorgnaxfoo`/`asdfqwertyzxcvneverexists12345`(各種明擺著亂打的測試字串,共約 12 次)、`多詞回退預設`(×4,測「多詞回退」這個搜尋功能自己的行為)、`★圖譜攔截★日:20[0-9][0-9]-`(測 `--regex` 能不能撈)、`seq0`/`lumos-calls`(×4)/`sitecustomize`/`TIMEOUT_OVERRIDE`/`parse_known_args`(這幾個是程式碼識別碼/檔名,不是自然語言概念,本來就不會寫進散文筆記)、LandmarkMember 的日期字串 `2026-08-14`、版本號 `v2.43.0`、`v2.43`。

**(c) 其他 —— 7 次**

`8句 3句 0筆`(在查 CLAUDE.md 自己引用的一個統計數字,不是概念)、`Diátaxis`(×2)、`MADR`(外部文件框架/格式的專有名詞,查的是「圖譜有沒有提過這個外部方法論」,不是同義詞問題)、`Phabricator`(外部工具專有名詞)、`FullWake`(macOS 特定 API 名稱)、`orphan-relink`(LandmarkMember,像是在查一個特定機制名稱是否存在,沒有在同指令證明可被同義詞救回)。

## 一句話結論

**(a) 類(真概念、換個說法就查得到)一個月大概 34 次**,平均一天略多於 1 次,幾乎全部發生在 lumos-toolchain 自己的開發/治理工作裡(30 次),LandmarkMember 只有 4 次(其中「會員登入流程」一個詞就查了 3 遍還是 0)。這個量體對「0 筆時自動建議換詞」這個功能來說,值得做——尤其這些案例裡有一半以上,同一次指令裡換個詞就真的找到了,證明建議是可行的。

## 這個方法可能漏掉什麼

- **只認得兩種訊息格式**:目前工具的零筆訊息是「共 0 篇候選」,但 8 月中以前有些逐字稿用的是更舊的「(候選 0;相關性排序…)」——我另外掃了一次抓到 7 次,但不保證沒有更早的第三種措辭沒被我認出來。
- **一次指令塞多個查詢時的對應關係是用人工核對出來的**,不是完全機械可重現;複雜的 shell 組合(`||`、`echo` 分隔、`| head` 截斷)偶爾會讓我把某個 0 筆結果配錯詞,雖然逐條都有交叉核對(用同指令內其他查詢的結果互證)。
- **LandmarkMember 的樣本數本來就很小**(約 27 次查詢),月統計上結論沒有 lumos-toolchain 那邊穩。
- **子代理(subagent)逐字稿**算在對應專案目錄底下一起掃了,但如果有子代理在完全獨立的暫存 repo(`lumos-probe-*`、`scratchpad`)跑查詢,我刻意排除了,因為那些不是使用者實際在這兩個專案裡工作。
- **Codex 側的 LandmarkMember 完全沒有 `lumos search` 呼叫紀錄**,但我看到有 7 場 Codex session cwd 指向 LandmarkMember——不排除是他們做的事本來就不需要查圖譜,但也可能是我的日期窗口或指令擷取漏掉了什麼。
