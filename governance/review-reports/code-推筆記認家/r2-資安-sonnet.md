severity: minor

1. 【驗證上一輪 major:路徑穿越】`safe_under()` 把 repo 根與拼出來的路徑都先 `resolve()`(解符號連結、解 `..`),再用 `relative_to(base)` 檢查是否還在 repo 內,不在就回 `None`,`cmd_sample` 收到 `None` 就不讀檔、只印一句「跑出專案外面」。
   誰:能改圖譜 `.md` 筆記 `about_code` 欄位的人(惡意 PR、或別人分享的圖譜)。從哪裡:`about_code` 值。送什麼:對這個圖譜跑 `home_audit.py sample`。拿到什麼:上一輪能拿到 repo 外任意檔內容並寫進輸出 JSON,這一輪——實測結果如下。
   實測:自建 5 種攻擊變體(`../outside/secret.env`、絕對路徑 `/tmp/.../secret.env`、`./../outside/secret.env`、repo 內符號連結指向外面的檔、`about_code: .` 剛好等於 repo 根),對含機密字串 `SECRET_OUTSIDE_CONTENT_zzz123` 的外部檔跑 `sample --vault ... --repo ...`。5 種全部被擋:前 4 種印出「這一項的路徑跑出專案外面,沒有讀它」,第 5 種(等於 repo 根)因為不是檔案被 `head_of` 的 `OSError` 分支接住印「讀不到:IsADirectoryError」。輸出 JSON 全文 grep 不到那個機密字串(`grep -c SECRET_OUTSIDE_CONTENT` = 0)。
   引句:「p = (base / rel).resolve()」
severity: clean
   blocking: 否

2. 【`--lumos` 路徑收窄】同一支 `safe_under()` 拿來擋 `--lumos`,擋的是「會被當程式執行」的路徑,不只是讀檔。
   誰:本機使用者(或能塞命令列參數給這支腳本的人)。從哪裡:`--lumos <路徑>`。送什麼:分別試絕對路徑外部檔、`governance/eval/../../../../../../tmp/evil.py` 這種 `..` 疊法、repo 內建一個符號連結指到 repo 外的 `.py` 再指過去。拿到什麼:三種全部被擋(`rc=2`,印「--lumos 只能指專案裡的檔,而且要存在」);對照組用 repo 內正常相對路徑 `./scripts/lumos` 照樣放行(功能沒被誤傷)。
   引句:「inside = safe_under(ROOT, Path(path))」
severity: clean
   blocking: 否

3. 【新正規表示式的 ReDoS 風險】`_PATH_IN_TEXT_RE` 從白名單字元類改成排除法(`[^排除字元]+(?:/[^排除字元]+)+`),結構上兩段都是單一字元類的確定性貪婪匹配,沒有像 `(a+)+` 那種可以用多種方式切分同一段字元的巢狀模糊性,理論上不具備指數回溯的條件。
   實測:對三種構造的長字串(①`"a/"*n` 重複到 300 萬字元、②隨機中英文夾雜含大量 `/`、③純字母無 `/` 逼它在每個起點失敗)分別在 n=1000 到 300 萬字元之間量時間,全部呈線性成長(300 萬字元約 0.47 秒),沒有出現二次或指數放大。
   引句:「★不要把字元類寫死成 ASCII★:中文資料夾與檔名在這套工具鏈服務的專案裡很常見,」
severity: clean
   blocking: 否

4. 【新整詞比對函式 `_home_mentions`】用 `str.find` 迴圈找 `token` 出現位置、檢查前後字元是否落在 `_HOME_MENTION_BOUNDARY`(僅 ASCII 檔名字元)之外來判定整詞邊界,邏輯本身沒有引入新的反序列化/shell/路徑讀取面——它只讀已經在記憶體裡的 `scan_text` 字串做比對,不碰檔案系統。這支函式的迴圈在 token 於 scan_text 裡重疊出現極多次時是 O(n·k) 而非 O(n),但屬於資源耗盡類、不屬於本次要報的範圍(且不是正規表示式回溯)。
   引句:「所以命中位置的前後要是非檔名字元(或字串邊界)才算。」
severity: clean
   blocking: 否

六類逐項判定:
1. 不可信輸入流到危險操作:見發現 1、2——上一輪的路徑穿越經自建 5 種攻擊變體實測已堵住,`--lumos` 動態載入面也用同一函式收窄且無法繞過。
2. 正規表示式:見發現 3——新字元類排除法規則實測線性、無 ReDoS。
3. 密鑰與個資:被擋下的路徑不再讀檔、也不印檔案內容(只印路徑本身供人去改 about_code);repo 內合法路徑的 `head` 仍原樣寫入會被提交的 JSON,這是 r1 已認列的 minor #3(縱深防禦缺口,本輪只加了一句存檔前人工檢查的提醒,沒有機械遮罩),沿用 r1 的 minor 判定,不重複計分。
4. 執行邊界:`home_audit.py` 仍無任何 hook/CI 自動呼叫(已重新 grep 全 repo,只有圖譜筆記與審查報告提到它);`_impact_repo_files` 改走 `_nodehome_git`(`subprocess.run` 傳 list 而非 shell 字串,`repo_root` 不會被拼進 shell)取代自己開 `subprocess.run(text=True)`,執行邊界沒有放寬,R18 無新增風險。
5. 加密與傳輸、行動端:這次沒碰,已看,無。
6. 新依賴:這批修正沒新增任何 import,`_impact_repo_files` 拿掉了它自己的 `import subprocess`、改用既有 `_nodehome_git` 包裝,依賴面收斂而非擴張;已看,無。

驗證過程中在 `/tmp` 建立的測試 repo 與惡意檔已刪除,`governance/eval/evil_link.py` 測試用符號連結已刪除。`git status --short` 顯示 `docs/.governance-log.jsonl`、`governance/review-reports/code-推筆記認家/r2-sha.txt`、`governance/review-reports/code-推筆記認家/r2-snapshot.patch`、`scripts/lumos` 四個非我建立/非我編輯的檔在共用 clone 上仍顯示改動(比對內容,`scripts/lumos` 那兩行是把本次 r2 diff 引入的字串拼接還原回舊寫法,`.governance-log.jsonl` 多了兩筆 `delguard`/`nodehome-check` 紀錄)——這些改動的時間點與內容跟我這次唯讀 grep/sed/Read 動作對不上,判斷是同一個共用 clone 上另一個並行 session 的寫入,不是我這次審查造成;我自己沒有對這四個檔案做過任何 Edit/Write。

```
$ git status --short
 M docs/.governance-log.jsonl
 M "governance/review-reports/code-\346\216\250\347\255\206\350\250\230\350\252\215\345\256\266/r2-sha.txt"
 M "governance/review-reports/code-\346\216\250\347\255\206\350\250\230\350\252\215\345\256\266/r2-snapshot.patch"
 M scripts/lumos
```
