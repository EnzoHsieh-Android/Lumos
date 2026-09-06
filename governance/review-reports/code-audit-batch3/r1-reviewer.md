severity: blocker

- [blocker] 聯集合併用集合判「有沒有」,會靜默丟掉內容相同但確實是不同事件的帳列,跟這批自己宣稱的「不丟任何一行」相反。
  位置:`scripts/lumos:11135`
  引句：「extra = [l for l in old_lines if l not in have]」
  why: JSONL 是事件序列不是集合。這不是假想:對本 repo 跑 sort docs/.governance-log.jsonl | uniq -d | wc -l 得 487 行內容重複,usage-log 也有 8 行(某一筆 context 查詢在同一秒出現三次,是三次真的呼叫)。模擬「本機加了一行,而遠端剛好也加了同樣內容」的情境,兩筆真的不同事件只留下一筆。這是 append-only 稽核軌跡的靜默資料遺失,而 gov/replay/freeze 的正確性都靠它。

- [blocker] 備份只在記憶體,而且寫回失敗時的救援指示是錯的,等於把罕見 IO 錯誤變成永久且靜默的資料遺失,還告訴操作者一條不存在的救援路。
  位置:`scripts/lumos:11141`
  引句：「print(f"  ⚠ {rel} 併回失敗(那幾行還在 git 的物件庫裡,`git checkout HEAD@{{1}} -- {rel}` 可救):{e}",」
  why: saved[rel] 在 git checkout 覆蓋工作檔之前從沒落盤也沒提交。之後寫回若拋 OSError(磁碟滿、權限、路徑變目錄),那幾行的唯一副本就是行程內的 python 變數,行程一結束就沒了。而訊息宣稱「還在 git 的物件庫裡」並叫人跑 git checkout HEAD@{1} —— 未提交的行從沒進過任何 git 物件或 reflog,那個指令救不回來。

- [major] 「更新拿舊副本覆蓋全域」只修了一半,另一條還活著的路徑會完整重現原 bug,而新 docstring 還指錯了誰是安全的呼叫者。
  位置:`scripts/lumos:11736`
  引句：「_install_hooks_py(root)」
  why: 相容外殼仍然把設路徑與全域同步綁在一起、前面沒有任何自癒。它唯一剩下的呼叫者是 cmd_bootstrap 的「已是專案 → 接 hooks」分支,任何人對「vendored 檔沒被 update 刷新過」的既有專案跑 bootstrap 就會走到,而那條路上沒有 pull 也沒有 copy2 自癒。實測重現:專案裡放舊的 check-graph-sync.py,呼叫 _install_hooks_py(root),舊內容直接被推進(沙箱的)全域 hooks,同時印「✓ 全域已同步」——正是這批 commit 訊息說修掉的那種靜默降版加綠燈。而且新 docstring 說這個外殼「留給來源就是最新的呼叫點(cmd_init 的新建路徑)」——cmd_init 的新建路徑實際走的是 _vendor_toolchain(已修的拆分版),不是這支;docstring 描述了一個不使用這支函式的呼叫者,真正的呼叫者完全沒有新鮮度保證。

- [major] 暫停修法的新測試只比對 gate 的文字位置,從不驗證它真的擋住執行,所以完全打掉暫停的回歸仍然是綠的。
  位置:`scripts/test_lumos.py:26130`
  引句：「check("暫停開關: ★所有週期觀測都排在開關之前(關掉派工不會連它們一起關)★", not after, str(after))」
  why: 把兩支腳本複製到暫存目錄,只刪掉 if 區塊裡的 exit 0、保留 if 與 log ——暫停變成空操作、派工每天照跑。用測試的位置邏輯跑變異後的檔:每一條(找得到 gate、觀測都在它之前、wrapper 沒有自己的 gate、wrapper 無條件呼叫)全部照過,因為沒有一條在看 if 的身體做了什麼。測試名字說守的是「暫停只停派工」,但它抓不到「暫停什麼都沒停」。次要同型:t_update_syncs_global_from_fresh_not_stale 把同步來源從 root 換成 src 仍然全綠(自癒讓兩邊那支檔相同);t_update_unions_bookkeeping_instead_of_blocking 的夾具只合併不重複的內容,結構上就抓不到上面那個集合去重的資料遺失。

- [clean] 新的 exit 0 對鎖與 finalize 的影響:讀完 finalize 全文確認 GAP_JSON 在新 gate 處仍是空字串,trap 走 GAP_JSON 空的分支,鎖會釋放、不記結局帳、不 requeue、不發連敗通知,跟既有「今天沒日報」的早退同款,不是新風險。

- [minor] wrapper 無條件呼叫:考卷/nags/replay 都是本機且有週或七天閘,沒有成本問題;run_probe 是唯一有外部配額成本的(真的起 claude CLI),閘是每 ISO 週。歷史檔空或不存在的機器,改動後第一次跑就會立刻花掉那週配額,沒有「第一次先跳過」的守衛。

- [minor] porcelain 解析:含空白的路徑 git 會加引號,strip('"') 處理得掉(實測過);改名 (R) 的 old -> new 會變成一個對不上白名單的字串,於是 mergeable 為假、落回安全的擋下路徑(實測過),不會誤併,但對改名的處理脆弱且沒寫明。
