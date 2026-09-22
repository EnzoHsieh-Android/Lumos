severity: blocker

## F1 新刻的路徑正規化沒有走既有的唯一算法,已知的 `../` 場景會安靜漏掉
severity: blocker
blocking: yes

`_norm_code_path`(patch 第 147-159 行)是這一輪新加的路徑正規化函式,只做「砍 `./` 前綴、砍重複 `/`、砍結尾 `/`」:

引句:「while s.startswith("./"):」
引句:「while "//" in s:」
引句:「return s.rstrip("/")」

但這個 repo 同一支檔案裡早就有「路徑比對鍵的共用正規化」`_posix_norm`(`scripts/lumos:196`),它的說明寫得很白:

`路徑比對鍵的共用正規化:反斜線轉斜線、去 ./ 與 a/../b(純字面,不查檔案);空的回空字串。工具自裝檔判別、about_code 的比對、排序加分讀 about_code 共用這一個(2026-09-10 代碼審 r3 架構席/整合席:原本三處各寫一份,排序那側只剝開頭的 ./,不解 ..)。`(`scripts/lumos:196-199`)

也就是說,2026-09-10 那一輪代碼審已經抓過「同一件事被寫成好幾份、而且各版正規化程度不一樣」這個坑,收斂成 `_posix_norm`/`_nodehome_key` 這一支「about_code 一項的比對鍵」共用函式(`scripts/lumos:21612-21614`),而且測試裡明確驗過 `../` 這個場景:

`scripts/test_lumos.py:1307-1312`:「⑮ 值寫成 src/../src/svc.py 也要對得上:排序這一側跟寫入側用同一個路徑正規化(2026-09-10 代碼審 r3 整合席)」。

這一輪的 `_guard_touched_hits`(patch 第 162-187 行)沒有呼叫 `_posix_norm`/`_nodehome_key`,而是另外刻了一份 `_norm_code_path`,結果就是不解 `..`。我直接把這一輪 patch 之後的 `scripts/lumos`(工作目錄現況,即這份 patch 套用後的樣子)當模組載進來實際跑:

```
touched = {"src/svc.py"}
hits, only_case = m._guard_touched_hits(["src/../src/svc.py"], touched)
# 結果:hits=[] only_case=[]
```

而同一份 repo 裡另一條走 `_posix_norm` 的路徑(排序加分那側),對同樣的輸入是判定「仍命中」(見上面 test ⑮)。兩邊對同一種寫法給出相反的答案。

為什麼是 bug 不是風格:這支函式存在的唯一理由就是「about_code 是人手寫的,寫法會跟 git 吐出來的不一樣,不正規化就會安靜漏掉」(patch 裡 `_norm_code_path` 自己的 docstring:「★不做這件事的話,本機那一層會安靜地失效★」)。`../` 正是這個 repo 自己認證過、而且已經在別處修過的「人手寫法」之一(2026-09-10 那輪就是為了同一個問題把三份正規化收斂成一份)。這一輪等於在明知道有現成、有測試背書的共用算法的情況下,又刻了第四份、而且刻得比既有那份弱,重新踩進「多處各刻一份、行為互相打架」的同一個坑——這正是本輪審查鏡頭要抓的「這裡又刻了一份」。而且踩中的正好是设计上明講「寧可多擋不可漏掉」的那個安全方向的反面:一支合約本來該擋的推送,會因為 about_code 寫成 `../` 形式而悄悄放行。

修法方向:`_guard_touched_hits`/`_norm_code_path` 應該直接改叫 `_nodehome_key`(或至少 `_posix_norm`),不要自己維護第二套規則;這樣也會一併補上 `_nodehome_key` 已經做、但 `_norm_code_path`沒做的 NFC 正規化(中文/重音字元兩種 Unicode 寫法,`scripts/lumos:21611-21614` 的註解原話就是在講這個)。

## F2 大小寫/資料夾容錯分支,對付的是既有 about_code 寫入合約本身已經擋掉的情況
severity: minor
blocking: no

`_guard_touched_hits` 新增「只有忽略大小寫才對得上也算碰到」與「家節點寫的是資料夾」兩種容錯(patch 第 162-187 行、summary 第 23 行)。但同一支檔案裡,`_about_code_path`(`scripts/lumos:13469-13500`,about_code 唯一的寫入驗證入口)已經明講兩件事都不該發生:

引句:「「{v}」不是這個 repo 裡的檔案(它是目錄;about_code 要寫到檔案)」

引句:「大小寫要跟磁碟上的真實檔名一致…大小寫不敏感的檔案系統上 SRC/A.TS 也通過 is_file,存進去就永遠對不上」

換句話說,透過 `lumos set/append/new --code` 寫入的 about_code,不可能是資料夾、也不可能跟磁碟大小寫對不上——這兩件事在寫入端就被擋掉了(而 CLAUDE.md 鐵則二本來就要求「開頭欄位用指令改,別手改」)。這一輪在讀取端另外刻了兩條分支去應付「寫入端已經保證不會發生」的情況,而沒有引用或提到 `_about_code_path` 這份既有合約(patch 裡的註解只講「寧可多擋」,沒有講為什麼要對抗一個寫入端已經擋掉的情況)。

不是說這兩條分支完全沒用(手改過的舊資料或繞過流程的檔案理論上還是可能存在),但它們的存在理由跟這個 repo「靠寫入端驗證 + 指令入口」的既有作法方向相反,而且沒有像 F1 引的那些函式一樣先查過既有合約再決定要不要多做這層——這正是本輪鏡頭要看的「這裡的正規化跟既有處理路徑一不一樣」,只是這次不影響對錯(方向是多擋不是漏擋),所以標 minor 不擋。

## F3 新測試多包了一層沒有作用的 sys.argv 防護,跟同檔其它 10 處同款測試不一樣
severity: minor
blocking: no

`t_guard_touched_path_forms_still_match`(patch 第 266-294 行)把主程式當模組載進來測內部函式,寫法是:

引句:「_argv = _sys.argv; _sys.argv = ["lumos"]」

`scripts/test_lumos.py` 裡至少還有 10 處用一模一樣的手法(`SourceFileLoader`/`spec_from_file_location` 把 `scripts/lumos` load 成模組,例如 `scripts/test_lumos.py:230-234`、`998-1001`、`1493-1496`、`1584-1587`、`2706-2707`、`3138-3139`),沒有一處做這個 `sys.argv` 存檔/還原。

我查過 `scripts/lumos` 全檔,`sys.argv` 只出現在 `main()` 裡面(`grep -n "sys\.argv" scripts/lumos` 只在 `main` 函式體內命中,模組最上層與其它函式都沒有讀它),而 `main()` 只在 `if __name__ == "__main__":` 底下才會被呼叫(`scripts/lumos` 檔尾)。`exec_module` 只執行到模組最上層的 def/class,不會觸發 `main()`,所以這個 repo 裡沒有任何一條路徑會讓「載入模組」這件事去讀 `sys.argv`。

為什麼值得標出來(但不到「非改不可」的程度):這段防護不會造成錯誤結果,純粹是多寫的、跟同檔其它同款測試風格不一致的複雜度,容易讓下一個人誤以為載入 `scripts/lumos` 真的會受 `sys.argv` 影響、照著抄一份到別的測試裡。既然同檔已有 10 個以上的先例可以直接照抄,這裡沒有理由多這一段。

---
（第一輪已折的七條:守衛欄位只取第一個、路徑不正規化的 blocker、收尾訊息自相矛盾等,這一輪的修正沒有重複踩上,不重報。）
