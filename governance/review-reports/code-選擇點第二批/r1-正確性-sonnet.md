severity: major

## c1 C-34 `.let`→`also` 的「回傳值有被用到」判法對沒大括號的 if/for/while/else/when 分支判反,把回傳值沒人用的 `.let` 也收進來
severity: major
blocking: 是(會產出必然等價、殺不掉的壞法,每次要人 lint-waive;違反規則自己寫的「只收回傳值有被用到的」)

- 輸入:`if (c) a.let { println(it) }`,另外 `for (i in 1..2) a.let {…}`、`while (c) a.let {…}`、`} else a.let {…}`、`when (c) { true -> a.let {…} … }`。
- 路徑:這幾種寫法的 `call_expression` 直接掛在 `control_structure_body` 底下,不在 `statements` 裡。`value-pos` 的第一支 `not: {inside: {kind: statements}}` 因此成立,`value-used` 判為「值有用到」,C-34 命中。
- 預期 vs 實際:預期是 if/for/while 當陳述用、值沒人拿,不命中(跟 S6「單獨成陳述 → 不命中」同理)。實際在 `kotlin-choice` 設定下 ast-grep 命中 C-34 的行是 2、3、4、7、8。`_choice_file_points` 也真的挑出壞法 `if (c) a.also { println(it) }`,這個壞法行為相同,殺不掉。
- 根因:`sbr.yml` 的 `value-pos` 本來是「不確定是不是值就不刪」的保守判法。C-34 照抄它,但用途反過來,變成「不確定是不是值就收」,保守方向顛倒了。
- 現有樣本 `choice-batch2.kt` 沒有沒大括號的 if 分支,所以 S6 樣本核對沒抓到。

引句:「    inside: {kind: call_expression, matches: value-used}」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:181`(判法來源 `:160`)

重現:
1. 把下列內容存成 `t3.kt`:`fun f(a: String, c: Boolean) {\n    if (c) a.let { println(it) }\n    for (i in 1..2) a.let { println(it) }\n}`。
2. 在 `/tmp/lumos-seat-work/code-選擇點第二批/正確性-sonnet/w`(clone 在 eebb84593)用 `m._choice_scan` 掃,再用 `m._choice_file_points("A.kt", src, [2,3], scan, tables)` 挑壞法。
3. 輸出:`2 mutant ('C-34','also','    if (c) a.also { println(it) }')`、`3 mutant ('C-34','also','    for (i in 1..2) a.also { println(it) }')`。
4. 現成腳本是 `/tmp/lumos-seat-work/code-選擇點第二批/正確性-sonnet/h.py`,輸入檔是 `t3.kt`。

## c2 S8 測試抓不到「放行只算最後一筆」和「終態不看時間先後」被改壞,而且測試文件宣稱會紅的改壞其實是綠的
severity: major
blocking: 是(被保護的是條款 S8 與範圍 5 寫明的口徑,有具體改壞而測試照綠)

- 改壞一:放行改成「第一筆贏」,也就是 `if wk not in c["row_waive"]:`。跑 `-k t_gov_stats_choice_by_row` 得 `2 passed, 0 failed`。原因是測試裡兩筆放行的列號和標籤都是「等價」,誰贏看不出來。
- 改壞二:壞法終態改成「最後一筆贏」,也就是 `c["row_mut"][(file, fp, row)] = {v}`。同樣 `2 passed`。原因是乙的事件順序是先存活、後殺掉,最後一筆剛好也是殺掉。
- 測試 docstring 寫「終態取最後一筆(同提交打平)→ 乙算存活、殺掉 1 紅」,實測不成立。只有「第一筆贏」會紅,「最後一筆贏」不會。
- 沒有測到「先殺掉、後存活」仍算殺掉,也就是計劃寫明接受的代價。測試沒有任何一筆放行是標籤或列號不同的兩筆,所以沒檢查放行「取最後那筆」。

引句:「            if wk not in c["row_waive"] or ts >= c["row_waive"][wk][0]:」
file: `scripts/lumos:17914`、`scripts/lumos:17974`、`scripts/test_lumos.py:146125`

重現:
1. 在臨時副本改 `scripts/lumos`。
2. 先用 `python3.14 scripts/test_lumos.py -k t_gov_stats_choice_by_row` 跑原版,得 2 passed。
3. 套上任一改壞(放行第一筆贏,或終態最後一筆贏)後重跑,仍是 `2 passed, 0 failed`。
4. 反向確認測試有效:把終態改成 `setdefault(key, {v})`(第一筆贏)會紅。

## c3 `?.` 另起一行時插 `!!` 的位移是位元組,測試完全沒有多位元組輸入,改成字元數照綠
severity: major
blocking: 是(多位元組字元的行列換算是本鏡頭點名的邊界;實作對,但守衛缺口有具體改壞)

- 實作的 `len(b[:op[0]].rstrip())` 是 bytes 長度,是對的。
- 改壞:把它換成 `len(b[:op[0]].decode("utf-8").rstrip())`(字元數當位元組位移)。
  - `t_choice_points_nul_safecall` 仍是 3 passed。
  - `t_choice_points_*`、`t_choice_samples_*` 沒有因此新增失敗。
  - 我只確認了 `nul_safecall` 一條測試是綠的;`t_choice_points` 整組在我的子集跑超時,被我中止。
- 同一改壞對輸入 `val é = "價格"; val u = r\n        ?.n`,實際壞法變成 `val é = "價格"; val !!u = r`(`!!` 插到識別字中間)。正確版是 `val u = r!!\n        .n`。
- 新增的 S2 測試只有 ASCII 輸入。第一版的 S2 就有一條多位元組案例,這次新位移計算沒有補。

引句:「        p = len(b[:op[0]].rstrip())」(此行在 `_choice_anchor_edits`,diff 內引句為 `p = len(b[:op[0]].rstrip())`)
file: `scripts/lumos:77351`

## c4 C-36/C-37 的「字面值」判法把負數字面值(`-1`)當非字面值,收進必然等價的壞法
severity: minor
blocking: 否(是規則精度問題,只有 `remember(-1)`、`LaunchedEffect(-1)` 這類少見寫法會中,放行即可)

- 輸入:`val b = remember(-1) { 3 }`。
- `-1` 在語法樹是 `prefix_expression`,不在 `literal-arg` 的清單裡,所以 `value_arguments` 被命中。C-37 的 `(刪掉)` 壞法是 `remember { 3 }`,常數 key 拿掉必然等價。
- 規則自己的註解寫「字面值:…數字…;全是常數的 key 換成 Unit 必然等價」,跟實際不符。
- 重現:`h.py` 的 `run` 對 t2.kt 第 14 行,輸出 `14 mutant ('C-37','delete','    val b = remember { 3 }')`。

引句:「# 條件同 C-36(帶尾隨 lambda、至少一個引數、不全是字面值):remember() 刪掉括號、全是常數的 key 拿掉都必然等價」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-37 規則上方註解)

## 逐項走查後確認沒問題的部分
- `?:` 錨點:註解在 `?:` 前後、`?:` 在續行、`a ?: b ?: c` 巢狀、`return`、括號內、`if` 條件內,都挑出正確壞法;`x ?: null` 與 `null ?: x` 都不產生。
- `?.` 的註解排除:行註解、區塊註解、鏈中、`x!!` 後,共 7 種擺法都正確不命中。前一行內有註解的 `foo(1, // c\n 2)\n ?.q` 照常命中。
- 同位置兩條編輯:`(p,p,"!!")` 與 `(p,p+2,".")` 在 `_choice_identity` 用「(起,迄) 由大到小」套用,結果是 `!!.`,沒有 `?.` 緊貼接收者時的重疊問題。
- 引數錨點:跨行、只改中間一行、尾端逗號都正確。範圍內沒改動行就回節點開頭,不會被選到。
- `check.py --catalog-only` 回「型錄問題 0 個」。新增測試 `nul`、`batch2`、`compose`、`table_batch2`、`samples_batch2` 在原版都綠。
- 帳的新舊互讀:`_gov_row` 欄位沒動,舊帳讀進來新計數正常。
- 規模:1500 個 `.let` 的大函式掃描輸出 5.9MB、1.7 秒,沒有 sbr.yml 註解警告的「輸出放大」問題。
- 後端角色卡:`be-api-compat` 這次沒有欄位改名、刪除或預設值變動;`be-authz` 沒有新增端點,不適用。

## 圖譜鏡頭
這次沒附固定席節點(鏡頭計算超時),我沒逐條判。以 diff 判斷,`_gov_row` 沒新增欄位、既有帳讀法不變,不影響治理帳合約。「依列號」小節跟計劃寫的範圍 5 一致,終態與去重口徑見 c2。

## 臨時資料
實驗放在 `/tmp/lumos-seat-work/code-選擇點第二批/正確性-sonnet/`。裡面有 `w`(clone)、`big`、`h.py` 和 `t1.kt` 到 `t5.kt`,收貨後請編排者刪除。

我中途對自己的背景測試程序下了一次 `pkill -f "w/scripts/test_lumos.py"`,模式只可能比對到這個 clone 路徑。

最嚴重:major;blocking 共 3 條
