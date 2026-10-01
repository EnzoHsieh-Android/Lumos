severity: minor

審查範圍:讀—改—寫是否整段在鎖內、鎖重入、原子寫入、子程序逾時與成本、P2 讀檔次數。
結論先講:鎖的結構是對的(無遺失更新、無重入死結),只有「鎖內做了不該做的慢事」與一個快取缺口。

已查證沒問題的項目(不是 finding):
- kill-add:`env.find` 在鎖外只用來取路徑,`load_raw_for_edit`、判重、`_kill_add_warn`、`atomic_write_verify` 全在 `_guard_kill_add_locked` 內,沒有鎖外讀到舊內容再寫回。
- kill-rm:`load_raw_for_edit`、`_kill_read_recipes`、算身分、重寫、`atomic_write_verify` 全在 `_guard_kill_rm_locked` 內,同一把鎖。
- 重入:`_vault_write_lock` 有 `_VAULT_LOCK_HELD` 巢狀直接過;`_kill_add_warn`/`_kill_recipe_judge` 一族沒有再拿鎖,不會死結。
- 原子寫入:兩邊都走 `atomic_write_verify`(寫暫存、自驗、換名),沒有自己 open 寫。
- P2 讀檔:`ctx["texts"]` 以 (repo 頂, 相對路徑) 為鍵,同一檔多配方只讀一次;`ls-tree` 每個 repo 頂只跑一次(成功時)。

## F1 鎖內做了無逾時的 git 子程序與讀檔,而鎖 30 秒就視為過期可被接手
severity: minor
blocking: 否
引句:「    # 判重之後、寫入之前:這次實際要寫進去的那一條原文還對不對得上」
佐證行:file: `scripts/lumos:15697`(`_VAULT_LOCK_STALE_SEC = 30`,註解寫「一次筆記寫入不到一秒」)
佐證行:file: `scripts/lumos:37098`(`_excl_lock_try` 鎖檔超過 stale_sec 就用 rename 接手)
1. 原本 kill-add 的鎖內工作是純記憶體加一次寫檔;這次把 `_kill_add_warn` 放進鎖內,它會跑 `git rev-parse`、`git ls-tree -r`(整個 HEAD 樹)、必要時 `git cat-file`,以及讀目標檔全文。這些 `subprocess.run` 都沒有 `timeout`。
2. 鎖的過期假設是「一次寫入不到一秒、30 秒沒放掉就當持鎖者死了」。若這幾個子程序因大 repo(百萬檔級的 monorepo)、網路掛載或磁碟卡住超過 30 秒,另一個 set/append/kill-rm 會用 rename 接手鎖,兩邊同時讀—改—寫同一篇,後寫的蓋掉先寫的(遺失更新)——正是這次改動要用鎖防的那件事。
3. 本 repo 實測 `git ls-tree -r -z` 約 0.03 秒(5734 檔),正常情況遠低於 30 秒,所以日常不會觸發;觸發要大 repo 或掛載卡住。**未能重現**(需要讓 git 卡 30 秒以上),故定 minor。
4. 建議:提醒判斷(純唯讀、不依賴筆記內容的部分)移到鎖外先算——它只需要 `recipe`,不需要讀筆記;但目前 `recipe` 在判重後才確定(只更新 covers 時用既有那條),所以可改成鎖內算出 recipe、鎖外印提醒,或對 git 子程序加 `timeout=`(例如 10 秒),逾時走既有的「判斷時出錯、只印一行、照舊寫入」分支。

## F2 ls-tree 失敗不快取,doctor P2 每條配方各重跑一次
severity: minor
blocking: 否
引句:「        r = subprocess.run(["git", "-C", key, "ls-tree", "-r", "-z", "--full-tree", "HEAD"], capture_output=True)」
佐證行:file: `scripts/lumos:13000`(同函式 `_kill_tree`:`if key not in ctx["trees"]:` 之後 `raise RuntimeError` 發生在寫入 `ctx["trees"][key]` 之前)
1. `_kill_tree` 只在成功時才把結果存進 `ctx["trees"]`;`returncode != 0` 時直接 `raise RuntimeError`,下一條指到同一個 repo 頂的配方又會重跑一次 `ls-tree`(失敗路徑沒有負向快取)。
2. 場景:某個平台根所在 repo 的 HEAD 物件損壞或 `ls-tree` 因故失敗(rtb 有 73 條配方、多數指同一 repo),P2 對每條配方各跑一次失敗的 `ls-tree`(成本是失敗的次數乘上每次的耗時,若每次要等到卡住才失敗則更慢),且 `_kill_p2_one` 會為每條各產一行「這條判不了」,輸出被同一原因洗版。
3. 建議:失敗也寫進快取(例如存例外或哨兵值,後續直接重丟同一個錯),並在 P2 合併成一行(比照 `noroot` 的聚合做法)。
4. 僅在 git 出錯時發生,日常成功路徑已正確只跑一次,故 minor。

最高等級:minor
