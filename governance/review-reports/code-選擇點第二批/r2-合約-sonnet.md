severity: minor

## k1 計劃的 REVISIT 日期與驗證筆記的 REVISIT 日期對不上,修補只改了一邊
severity: minor
blocking: 否 這是文件不一致,但照文件做不會出錯,也不會讓推送被擋。
- 引句:「REVISIT:2027-01-17 上線滿兩個月,讀 gov --stats 選擇點段「依列號」C-32 到 C-37 各列的殺掉、存活、跑不出結果與放行理由」
- 另一邊,計劃第 31 行:「REVISIT:2027-01-15 最晚這天跟第一版的 REVISIT 一起看第二批各列的殺掉率、跑不出結果比例與放行理由」
- 兩條 REVISIT 要做同一件事,日期卻不同。
  - 計劃寫的是「最晚這天」,驗證筆記改成的 01-17 比它晚,字面上矛盾。
  - doctor 會在 01-15 先點名計劃那條。這時 RETIRE-IF「上線日起滿兩個月」(上線日 2026-11-17,滿兩個月是 01-17)還沒到。依列號的數字在 01-15 還不能判列去留。
- 歸因:有證據的修復回歸。
  - 修前 eebb8459:驗證筆記是 `REVISIT:2027-01-15`,跟計劃一致。
  - 修後 6cc9ad8c:驗證筆記改成 01-17,計劃仍是 01-15(`git grep -n "REVISIT:2027" 6cc9ad8c` 可見)。
- 佐證:`docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:31`、`docs/lumos-toolchain-knowledge/Verification/2026-11-17_選擇點第二批上線前實測.md:53`

最嚴重:minor;blocking 共 0 條

## 圖譜鏡頭固定席
- `Systems/kotlin規則包`
  - 不影響。我核對過它改的三處:
    - about_code 有 `nul.yml` 與 `samples/choice-batch2.kt`,檔案確實存在於 6cc9ad8c。
    - WHY 指向的 `t_choice_samples_batch2` 存在,實跑通過。
    - 新 PITFALL 的 repro 是 300 層 `remember` 的巢狀輸出和 1500 個 `?.p` 長鏈。我用 ast-grep 0.51.2 重跑:長鏈 7.5MB,跟文字一致。300 層巢狀是 0.25MB,文字寫 0.44MB,生成方式不同,仍在「遠小於 64MB」的同一結論內。
- `bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`測試假綠形態`、`lumos-cli-read` 的 ★INVARIANT★:不影響。
  - 這次文件包只動計劃、kotlin規則包、Verification 三篇。
  - 那五篇的合約行沒被改到,綁定測試是它們自己的。
- `pitfalls-code-loop`、`loop-convergence-recording`:不影響。這份文件差異沒碰它們,牽連只來自 `scripts/lumos` 的程式變動。
- 「這次新增的殘留」段:
  - 該段算不出來(派工鏡頭時間預算用完),我沒有自己翻 `governance/residual-index.json` 和治理帳,所以本席沒答這題,未判定。
  - 文件差異本身沒有碰殘留問答,但「沒換編號或改字重問」這件事沒有憑據可寫。

## 已驗正向主張(三問)
我在 6cc9ad8c 的臨時 clone 跑的結果如下。

1. 原問題的修復效果:
   - claim:「報樣本標記指向不在表裡的列」不用 `--sg` 也查。
   - input:`choice-batch2.kt` 末尾加 `// MISS C-99`,PATH 不含 ast-grep,跑 `check.py --catalog-only`。
   - expected:報出該列。
   - after:印出「C-99: 樣本 choice-batch2.kt 第 60 行標 MISS C-99,表裡沒有這一列」,並顯示「型錄問題 1 個」。
   - before:未驗(沒有取 eebb8459 對照)。結論限於修後行為成立。
2. 修補處的正常、錯誤與相鄰路徑:
   - 型錄統計「選擇點表:37 列」、C-32 到 C-37 共 6 列,數字對得上。
   - `已撤列號:(無)` 與 check.py 的 `_CHOICE_RETIRED_RE` 解析一致。
   - `-k choice_samples_batch2` 與 `-k choice_table`:25 passed、0 failed。
   - `check.py --catalog-only`:型錄問題 0 個。
   - C-34 規則的實際內容與計劃新增的句子一致:排除字元字面值和負號數字,排除沒大括號的分支。
   - 驗證筆記的 20 個提交加總也對:甲 102→109,乙 16→20,合計多 11 個,平均 0.55。
3. 新發現的同一案例修前修後:只有 k1,結果如上。

未驗範圍:
- 沒有跑任何不帶 `-k` 的全套測試。
- 沒驗 `gov --stats`「依列號」小節的程式行為,這屬於程式鏡頭,不在本席的文件對照範圍。
- 沒驗 444MB 修前的數字,只驗了修後輸出量級。

臨時目錄 `/tmp/lumos-seat-work/code-選擇點第二批/合約-sonnet/` 內自己建的 clone 與測試檔已用字面絕對路徑刪除。
