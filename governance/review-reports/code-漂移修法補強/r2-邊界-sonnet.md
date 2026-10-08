severity: minor

# 邊界-sonnet 第 2 輪報告(邊界與輸入鏡頭)

實驗環境:clone 到臨時目錄,直譯器 python3.14;腳本在 /private/tmp/claude-501/ 底下 edge_*.py(檔案系統上,不在 repo)。

## F1 同一個卷證目錄在 git 原名與檔案系統名 NFC 等價但不同時,被列兩次且都不標「兩者」
severity: minor
blocking: 否
引句:「if d and d not in out and nfc(d) in keys:」
佐證行:file: `scripts/lumos:_drift_c4_dirs`(patch 內 by_name 用檔案系統名、same 用 git 原名,兩邊照原名對)
1. 歷史提交裡卷證目錄路徑是 NFD(用 update-index --cacheinfo 造,等同 core.precomposeunicode=false 或別台機器提交),現在檔案系統上的目錄名是 NFC。
2. plan_refs 指到 `code-é測試_計劃`,`_drift_c4_dirs` 回傳 [('code-é測試','同提交'), ('code-é測試','計劃名')],兩行肉眼一樣、第一行是 NFD、第二行是 NFC,來源沒合成「兩者」,排序也被拆開。
3. 在分正規化的檔案系統上,第一行(git 原名)是不存在的路徑;修正想避開的問題(印不存在路徑)在這個組合仍會發生,還多了重複行。
重現:`python3.14 edge_c4b.py <clone> <暫存repo>` 印出 `[('code-é測試', '同提交'), ('code-é測試', '計劃名')] [(True, False), (False, True)]`。

## F2 「另有 N 個」的數量與貼上去的 git 指令輸出不一致(頂層散檔被當成目錄)
severity: minor
blocking: 否
引句:「return f"git --literal-pathspecs -c core.quotePath=off {src} | cut -d/ -f3 | sort -u"」
佐證行:file: `scripts/lumos:_drift_c4_more_cmd`
1. governance/review-reports/ 直接放一個 `loose.txt`(三段路徑),再放 21 個目錄、同一提交加入。
2. 證據頁印「另有 1 個沒列出」,貼那條指令輸出 22 行,第 22 行是 `loose.txt`(cut -f3 對三段路徑取到檔名)。
3. 目錄剛好 20 個時不印指令、剛好 21 個時印,邊界本身正確(實跑 20→20 列且無尾巴、21→列 20 + 尾巴)。只有散檔造成計數對不上。

## F3 刪除守衛讀「工作目錄」的工具檔判斷原封不動,暫存區(實際被提交的內容)不同時會漏掃
severity: minor
blocking: 否
引句:「else _vendored_state(root)[0])」
佐證行:file: `scripts/lumos:24511`(同族的每支檔有家在暫存模式用 `_vendored_state(root, "")` 讀索引);file: `scripts/lumos:24643`(同上,`"" if staged`)
1. 消費專案:HEAD 的 scripts/lumos 含 zzGoneFn,安裝清單記的是「新版工具檔」的指紋。專案把自己改過的版本(刪掉 zzGoneFn)暫存,之後跑 `lumos update` 把工作目錄換回安裝版與清單。
2. 暫存區是專案自己改的內容,工作目錄卻跟清單一致 → 跳過集合含 scripts/lumos → zzGoneFn 沒被抽、note 記 `vendored-skip=1 files=scripts/lumos`,圖譜還在講它卻不提醒。實跑 stage_custom_then_update 輸出 `tokens=0 hits=0 ... vendored-skip=1`。
3. 同類:把暫存區的 scripts/lumos 換成指向安裝版副本的 symlink(typechange),工作目錄讀 symlink 目標→一致→跳過,實跑 symlink_tool 同樣 tokens=0。
4. 作者在程式註解裡已承認「少見情形少掃」;這裡補的是:同族呼叫端在暫存模式都用 ref="" 讀索引,delguard 是唯一不同,而註解說「跟推送前分級等處同一支」。用 `_vendored_state(root, "")` 可對齊(讀索引要跑 git,得算進 deadline)。

## F4 註解與程式行為矛盾:git-sha> 註解說不算,實際會被擋
severity: minor
blocking: 否
引句:「sha 前面不能接英數(git-sha> 之類不算)」
佐證行:file: `scripts/lumos:_set_cond_slot_variant_re`(before 的 lookbehind 只排 `[A-Za-z0-9_]`,連字號放行)
1. 實跑 `_SET_COND_SLOT_VARIANTS` 對 "git-sha> 之類" 命中 `sha>`(擋),註解宣稱不算。
2. 另兩個同族實測結果供參考,不另列:`a < sha`、`if x <sha then`(開括號那側不要求閉括號、`<` 後接空白加 sha 結尾)也命中;`<卷證 目錄>` 命中 `<卷證`。都是散文裡少見的寫法,所以只提註解與行為的不一致。

## 已實跑、判無問題的邊界(不列 finding)
- 安裝清單壞掉:空檔、`null`、`[]`、`files` 為 list/null、值為整數/list、非 JSON、BOM、指紋大寫、指紋尾巴多空白、清單路徑是目錄 → 一律不跳、照抽(delguard 端到端 note 都不帶 vendored-skip)。清單 JSON 內含 CRLF 仍正常解析並跳。
- 工具檔本身 CRLF(指紋先換 LF)→ 仍算原封不動;安全方向。
- 改名:來源路徑有空白、中文(core.quotePath=off)時 `rename from` 抽對;diff.srcPrefix/dstPrefix 自訂前綴不影響(git 端已固定)。
- 卷證目錄名含空白、中文:git 指令實測可用,--literal-pathspecs 下目錄前綴正常。
- c1:missing 零句回空(不印尾巴)、一句與逐句相同、三句以「、」接成一句只出現一次尾巴;settle 端維持逐句。
- 佔位字變體:多行值(含 `<\nsha>`)、反引號包住、`<sha256>`、`<SHA-1>`、`<卷證目錄>`、泛型 `Foo<Sha>` 之外的合法角括號照收。

## 圖譜鏡頭逐條判定
- Systems/存量漂移守衛:c4 證據頁與 c1 訊息改動不破壞其「drift fix 只列證據、不代寫 c4」與 c1 補改宣告;F1、F2 只影響證據頁顯示。
- Systems/bound-tests-gate:本改動不動綁定測試的判定路徑,不影響。
- Systems/guard-kill、lumos-cli-read、lumos-cli-lifecycle、design-loop、測試假綠形態:diff 未碰其合約行為,不影響。
- Systems/授權與歸屬:`_VENDORED_TOOLKIT` 未動,LICENSE 不在跳過集合;delguard 改用 `_vendored_state`(限白名單內)只會更窄,不影響。

最高等級:minor
