severity: minor

圖譜鏡頭:hook 這次沒附固定席節點(鏡頭計算超時,沒有節點清單可逐條判)。我只能照 diff 判:這次改動只動規則包、型錄檢查、挑壞法和 gov 統計,沒碰推送閘的判定順序或帳的寫入格式,沒有「不影響」以外的牽連可指。

## r1 一般密度的大 Kotlin 檔會讓整批輸出超過 64MB,該檔記成驗不了
severity: minor
blocking: 否 守衛只是對那一檔降成「沒檢查到」,沒有做出錯的行為,而且畫面上看得到。

- 輸入:一支 1.16MB、約 17.7k 行的檔。每行像 `fun f1(u: U?) = u?.profile?.name?.trim() ?: u?.alt ?: "x"`,每行 4 個 `?.`、2 個 `?:`。
- 路徑:`_choice_scan` 先整批掃,再退回逐檔,最後 `_choice_scan_one` 擋輸出上限。
- ast-grep 輸出:共 103,147,324 位元組。其中 C-33 有 70,964 筆、共 65.6MB;C-32 有 35,482 筆、共 34.6MB。每筆約 0.9 到 1.2KB。
- 原因:每個命中都帶 `metaVariables` 和 `labels`。`inside:` 關係會把外層節點的文字和座標放進 secondary 標籤。
- 預期:跟第一版一樣能驗。這支檔在第一版的規則下沒有 C-32、C-33,輸出不會超限。
- 實際:該檔記成驗不了。重現指令是在臨時 repo 對這支檔的新增提交跑 `python3.14 scripts/lumos choice-points --diff HEAD~1..HEAD`,輸出如下。
  ```
  沒檢查到:1 支檔語法樹掃描算不出來(其他檔照列):app/src/main/kotlin/A.kt(ast-grep 掃描回 -25)
  ```
  回 -25 是 SIGXFSZ。工作樹模式的 RLIMIT_FSIZE 在 64MB 加餘量處把 ast-grep 殺掉。
- 邊界:同一支檔砍半(8870 行)只有約 50MB,不超限,pick 全程約 5.8 秒。門檻大約是每 20 到 30 位元組一個 `?.` 或 `?:`。作者量過的兩個真實專案沒到這個密度。
- 好的一面:磁碟沒被寫爆。RLIMIT_FSIZE 擋住了,ast-grep 的記憶體也跟著被限在上限附近。

引句:「inside: {kind: navigation_expression}」
file: `configs/ast-grep/kotlin-choice/rules-choice/nul.yml:16`(patch 內 nul.yml 的 C-33 規則)
file: `scripts/lumos:77132`(`_choice_scan_one` 的超限判斷在 `_LINT_SARIF_MAX_BYTES`)

## r2 C-33、C-37 的輸出對「單行鏈長」和「巢狀深度」平方成長,小檔就撞上限
severity: minor
blocking: 否 要很極端的輸入才會到,結果跟 r1 一樣是記驗不了,不損壞資料。

- 重現一:單行 `val y = x` 後接 5000 個 `?.p`,檔只有 15,028 位元組。輸出 154,048,438 位元組,全是 C-33 的 5000 筆。每筆約 30KB,因為帶了整行的 `lines` 和整條外層 navigation_expression。
- 重現二:`val r0 = remember(k) {` 巢狀 300 層,檔 97,722 位元組。輸出 115,931,651 位元組,全是 C-37 的 300 筆。命中文字只有 `(k)`,但 `metaVariables` 的 secondary 約 295KB,因為外層 `call_expression` 帶著整個尾隨 lambda。
- 重現三:多行 elvis 鏈 5000 層,檔 53,918 位元組。輸出 583MB。作者說的「深層巢狀 elvis 已知平方」是這一條。鏈 10000 層時檔 108,918 位元組,輸出 2.37GB,ast-grep 記憶體 2.39GB,耗時 11 秒。這次是自己直接跑 ast-grep,沒有經過工作樹模式的 RLIMIT_FSIZE。
- 預期:大小跟檔案成線性。
- 實際:C-37 約在 220 層、C-33 約在 1700 個 `?.` 就撞 64MB。

引句:「has: {kind: simple_identifier, nthChild: 1, regex: '^remember$'}」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-37 的 `rule:` 段,id 在 patch 的 api.yml 新增段)

## 逐題結論(沒有 finding 的部分)
- ② 引數錨點:`_choice_anchor` 的 `for ln in range(hit["line"], hit["end_line"]+1)` 每個命中只掃自己引數清單的行數,`ln in changed` 是集合查詢。總成本是「引數清單行數 × 巢狀深度」,在 ast-grep 輸出先撞上限之前不會變平方。
  - `_choice_anchor_edits` 的 `len(b[:op[0]].rstrip())` 每個候選複製一次檔案前綴。1MB 檔做 2 萬次共 0.37 秒,可忽略。
  - 已撤列號和樣本標記檢查只讀型錄文字和樣本目錄一次,沒有二次方。
- ③ 15 秒挑壞法時限:718KB、19998 行全改、三種新規則混合,整個指令 8.7 秒,`_choice_file_points` 約 3 到 4.7 秒。每行 4 個 `?.` 加 2 個 `?:` 的 8870 行檔整個指令 5.9 秒。新錨點和編輯沒有讓挑壞法逼近 `_CHOICE_PICK_BUDGET`。
- ④ gov --stats 依列號:12 萬筆的合成帳,`row_mut` 約 40MB、`row_waive` 約 22MB(這些鍵的字串與帳列共用,不另佔)。相對 12 萬筆帳本身的 dict 是小頭,不構成問題。
- 孤兒子程序:新程式沒有新開子程序。ast-grep 仍走 `_choice_sg_run`,逾時收整組、`finally` 登記取消,沒有新的洩漏路徑。

重現用的暫存放在 `/tmp/lumos-seat-work/code-選擇點第二批/資源-sonnet/`。repo 本身沒動。

最嚴重:minor;blocking 共 0 條
