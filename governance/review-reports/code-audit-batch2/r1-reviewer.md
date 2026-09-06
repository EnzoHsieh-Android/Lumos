severity: blocker

- [blocker] 把 governance/* 加進 pre-commit 的 should_exclude,等於把整棵治理目錄從「改 code 沒動圖譜就擋」的硬閘裡放掉,而那底下有真程式。
  位置:`scripts/hooks/pre-commit:140`
  引句：「docs/*|governance/*|*/node_modules/*|*/bin/*|*/obj/*|*/.git/*|*/dist/*|*/build/*|*/__pycache__/*) return 0;;」
  why: governance/ 底下有 28 支實際在維護的 python/shell(autonomous_loop/gap_select.py、replay_weekly.py、eval/*.py、governance_flex_builder.py、autonomous-loop.sh…),不是 commit 訊息說的「帳本與散文」。乾淨 clone 實測:帶這個改動,改 gap_select.py 不動圖譜可以直接 commit(rc 0);把那一句還原就硬擋(rc 1,印「這次 commit 改了程式碼,但知識筆記一個字都沒動」)。這跟作者宣稱的方向相反——對這道閘是永久而且靜默地更寬鬆。兩份清單目的不同:delguard 那份是慢而吵的建議性搜尋,pre-commit 那份是硬擋文件同步;既有漂移守衛逼它們逐字相同,這份 patch 就靠機械照抄滿足了守衛,沒有檢查對硬閘的語意是否安全。

- [major] 新測試只比對常數內容,沒有跑真正的過濾邏輯,擋不住機制壞掉。
  位置:`scripts/test_lumos.py:868`
  引句：「ex = list(getattr(m, "_DELGUARD_EXCLUDE_DIRS", []))」
  why: 在乾淨 clone 把 _delguard_parse_diff 裡真正的排除判斷改成 excl = False(等於整個排除機制失效,速度與語意兩個目的都落空),測試仍 4 passed 0 failed。真的回歸(邊界邏輯打錯、運算子寫反、安裝時清單被截斷)會靜默出貨。

- [major] doctor 新測試把所有 ⚠ 行都當成軟提醒,只要 repo 有一個普通硬問題就會在產品沒壞的情況下翻紅。
  位置:`scripts/test_lumos.py:906`
  引句：「soft_printed = out.count("  ⚠ ")」
  why: warn() 對硬問題與那唯一的空清單軟提醒印的是同一種行,但只有空清單那種會加進軟段計數——這對收尾行的語意是對的(硬問題已經算在「N 個 issue」裡,不該重複計)。測試卻假設 issues 恆為 0。乾淨 clone 實測:在一篇節點加一個壞連結(普通硬問題),doctor 正確印 issues=1 與「另有 8 段」,但所有 ⚠ 行是 9 行,斷言 8==9 失敗。目前只是潛伏,因為審查當下這個 repo 剛好 0 硬問題。

其餘查過:字首比對對 xdocs/ 這種撞名是安全的(要求前面有 /);_delguard_confidence 的方向如作者所稱(排除更多只會讓 token 更容易判成 high,不會壓掉命中);空 tuple 的所有消費點都是單純迭代,沒有假設非空;測試的 argv 索引對得上,實跑 install_global_hook_sync 13 passed;刪檔後全 repo 沒有還會執行到的殘留引用。
