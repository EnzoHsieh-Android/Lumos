severity: minor

沒有 hook 附上的固定席節點(LUMOS-LENS 說鏡頭計算超時),所以本報告沒逐條答固定席。

1. 沒關上的註記括號讓每個單獨一行的 // BAD 都掃到檔尾,工作量變成二次方
severity: minor
blocking: 否
引句:「while i < len(code):」
file: `configs/ast-grep/kotlin-android/check.py:1119`(修後 `_balanced_end`;呼叫鏈是 `_next_statement` → `_annotation_end` → `_one_annotation_end` → `_balanced_end`)
具體失敗場景:壞例檔裡每個單獨一行的 `// BAD` 後面,若接一個括號到檔尾都沒關的註記(例 `@A(`),`_balanced_end` 就從開括號逐字元掃到檔尾才回 None。`_annotation_end` 把它當成不是註記,`_next_statement` 因此停在這行。M 個標記乘上 N 行,工作量是 M×N。實測 `"// BAD\n@A(\n"` 重複 4000 次,耗時 2.47 秒;1000 次 0.15 秒、2000 次 0.62 秒,翻倍約四倍。壞例檔是作者自己寫的小檔,而且這種寫法本身就是壞語法,所以不會擋到正常操作,只是比修前慢。
歸因:有證據的修復回歸(修前只往下找第一個非註記行,近線性)
查證命令與結果:
- 修後:對 `scripts/lumos` 載入的 `lumos`,呼叫修後 `check._bad_lines_in(lumos, text)`,上述輸入 4000 次耗時 2.47 秒。
- 修前:取 6d53943 版 `check.py`,以 `old._bad_lines` 對同一內容(4000 組)的壞例目錄跑,耗時 0.10 秒。

資源面其他已驗的部分:
- 子程序與執行緒:新增的 `_balanced_end`、`_annotation_end`、`_next_statement`、`_bad_lines_in` 與範本圍欄守衛都是純字串運算,沒有開子程序或執行緒,也沒有逾時預算,所以沒有孤兒或 Ctrl-C 殘留的路徑。
- 無窮迴圈:`_annotation_end` 的 `while True` 每圈要嘛回傳、要嘛游標至少前進一格,`_next_statement` 的回傳值必定大於 nxt 才會繼續,讀碼確認會終止。
- 大輸入:壞例檔只有「單一未關括號 + 20 萬行」一種,實測 0.06 秒。`--catalog-only` 在修後工作目錄實測 0.96 秒、輸出「型錄問題 0 個」,跟作者的 0.9 秒表態相符。
- 範本圍欄守衛:`_template_route_problems` 每次多呼叫一次 `_fence_regions`,對範本行數是線性。整支型錄自檢已含這個守衛,仍在 0.96 秒內,所以沒有能量到的預算問題。

三問:
- ① 原問題的修復效果:本席只看資源面,沒有重現原本「註記跨行」的語意修復。要判斷修復是否有效,還要由正確性席用 r4-behavior-cases.md 的案例對修前後各跑一次。我能確認的只有修後在這輪的正常輸入上沒有可量到的退化(`--catalog-only` 0.96 秒、型錄問題 0 個)。
- ② 修補處的正常、錯誤與相鄰呼叫路徑:正常路徑(整行只有註記、註記後同一行接程式、沒有註記)都會終止。錯誤路徑是括號沒關,回 None 後退回原行,不會拋例外。相鄰的 `_bad_lines` 呼叫端已改成走 `_bad_lines_in`,行數對不上時仍回問題訊息。唯一的資源差異就是上面那條二次方。
- ③ 新發現的同一案例,修前與修後:`"// BAD\n@A(\n"` 重複 4000 次,修前 0.10 秒,修後 2.47 秒。

未驗範圍:巢狀 `<` 泛型把 `->` 的 `>` 當收尾而提早配對,那是正確性問題不是資源問題,我沒有往下驗。我也沒有量真實壞例目錄(`samples/bad`)的整體耗時,只量了 `--catalog-only`。

總結:最高等級 minor,共 1 條
