severity: minor

我沒有找到 blocking 級的問題。新判準第一階段(`_QUOTE_WRITE_RULE` 為 legacy)下,舊帳回放與改前完全一致;還原提交後帳上多出的欄位與事件,只有一處統計歸類的副作用。實驗目錄已刪,repo 沒動。

1. 還原提交後,舊版 `gov --stats` 會把引句擋下事件歸進「缺 refuted-set」
severity: minor
blocking: 否
引句:「_rn = sum(1 for r in _rest if "report-not-normalized" in _d(r))」
file: `scripts/lumos:9530`
- 實測:往改前提交 cb832b56 的 clone 追加一筆 `note` 以 `quote-rule:` 開頭的 canary blocked 事件。舊碼印「缺 refuted-set 1」,新碼印「引句判準 1」。
- 舊碼歸類只靠 `"report-not-normalized" in _d(r)` 這類包含判斷。事件的 `quote=` 片段是審查席可控的文字,而審查報告常常引用這兩個字串,所以還原後這批事件可能被算成別格。
- 計劃〈回退〉的不可逆項只寫「欄與事件留在帳本」,沒提還原後統計會被污染。這只影響統計,不影響判定。

2. 處置閘接住判準例外後,凍結入口會把例外固定成紅色標準答案
severity: minor
blocking: 否
引句:「★判準本身丟例外 → 判失敗、不 traceback★」
file: `scripts/lumos:26541`
- 改前,判準丟例外會讓 `loop replay --freeze` 崩潰,不寫 verdict。改後變成 `fails=["quote"]`、rc=1。
- 凍結入口只擋 rc2,所以 rc1 照樣凍進 `verdict.json`。週跑補凍(`replay_weekly.py`)沒有人看著,也會無聲地凍成紅。
- 這是計劃已記的「凍結接受非綠判定」的新入口,不是新毛病。第一階段 legacy 不會丟例外,所以現在打不到。第二階段若 v1 分支有 bug,會先凍成紅,等修好後才報邏輯漂移。
- 建議在 Issue〈凍結接受非綠判定〉的修好條件裡寫明「判準例外被轉成 rc1」這條來源。

3. 拿掉比較模式後留下的殘骸:`quote-check` 參數宣告與說明沒收乾淨
severity: minor
blocking: 否
引句:「help="一般模式必填(手動檢查,缺了擋下 rc2)"」
file: `scripts/lumos:53321`
- 「一般模式」是相對於比較模式才有意義的說法,現在只剩一種模式。
- `qc_report` 仍是 `nargs="?"`、`--spec` 仍是 `default=None`,缺參數由函式內擋下。`lumos quote-check` 不帶參數時,原本是 argparse 用法錯誤,現在變成自訂訊息,仍是 rc2。
- 測試標題「一般模式缺 --spec」同樣是殘留說法。
- 功能沒壞,只是兩個舊設計的痕跡。

4. 章值不認得時,錯誤訊息把帳上的值完整印出,沒有長度上限
severity: minor
blocking: 否
引句:「return None, None, f"引句判準欄不認得:{v!r},可能是新版程式寫的或帳被手改"」
file: `scripts/lumos:25809`
- 帳被手改成超長字串時,`{v!r}` 整串進 stdout。同一段別處的例外訊息都有截 120 字。
- 只有手改帳才會碰到,而手改帳本來就是這條要攔的情境。屬一致性問題,不是弱點。

以下是你要我答的幾項。

**會凍結、補凍、重算判定的入口(共四個,最後一個是重算)**

| 入口 | 遇到非綠判定 |
|---|---|
| 處置閘 | rc1,不放行 |
| 手動 `loop replay --freeze` | 只擋 rc2,rc1 照樣凍 |
| 重凍(`--freeze --note`) | 同上 |
| 週跑補凍 | 同上,也不看是否為綠 |
| 回放 `--golden` | 紅就喊,golden 過期只指路重凍 |

- 帳上 307 份判定檔有 5 份 rc1,我用程式數過,和 Issue 寫的一致。
- 已知問題的處置,和上面第 2 條的新來源,都在計劃的〈實務隱患〉與 Issue 裡。

**舊帳在新程式下回放**
- 我把 cb832b56 與 HEAD 各 clone 一份,對 307 個判定檔逐一跑 `loop replay --golden`。
- 新碼 307 個裡 306 個 rc 0、1 個 rc 1。舊碼 306 個判定檔(少了 HEAD 才新凍的「引句錨定整段比對」)裡 305 個 rc 0、1 個 rc 1。
- 唯一的 rc 1 兩邊都是「消費專案接入靜默失效」,和計劃一致。
- 兩邊輸出逐檔比對:新碼只多一行 `[disposal] 引句判準:legacy(帳上無章)`,共 282 檔。stderr 都是空的。
- 把全部帳列與判定檔列加上 `quote_rule: legacy`,改回舊碼(cb832b56)後重跑:306 個 rc 0、1 個 rc 1。所以舊碼對這個多出的欄位沒有異常,計劃〈回退〉說的「逐欄 `.get`」站得住。
- `_quote_rows_legacy` 的本體與改前的 `_quote_rows` 逐字相同。
- `-k quote` 的 173 個測試全過。

**還原這個提交後帳上的樣子**
- 帳上會留 `quote_rule: legacy` 欄(目前 `docs/.canary-log.jsonl` 有 4 列,都是本迴圈 r1 到 r4 的載體列),以及 `quote-rule:` 開頭的 blocked 事件。
- 舊碼判定不變,只有第 1 條的統計歸類副作用。
- 判定檔的 `engine_rev` 沒推進,所以還原後沒有任何一個判定檔被判成過期。

**處置閘新行會不會影響解析輸出的腳本**
- 會讀處置閘輸出的只有 `replay_weekly.py`,它看紅標記字串和 rc。新行是「引句判準:…」、診斷行和例外行,不含「邏輯漂移 / 帳被動 / 凍結檔被動 / 佚失」這些字。
- 例外行的 `str(e)[:120]` 不在這個範圍,但目前打不到。
- 我實跑 307 個回放,rc 與紅標記判定和改前一致。
- `quote-check` 非 JSON 模式多了第一行「引句判準:…」,JSON 多了 `rule` 欄。repo 內沒有程式解析這個輸出。

**效能**
- full-span-v1 對 100 萬個開引號、2 萬條未閉合標籤、200 萬個收尾引號都在 0.2 秒內。
- 舊判準對 2 萬條未閉合標籤要 20.8 秒,這是原本就有的二次方成本,Issue 已記。
- 第二階段寫側擋下時會多算一次舊判準,這個成本也已寫進計劃。

總結:最高等級 minor,blocking 共 0 條
