severity: clean

我沒找到會擋推的問題。下面先答你交代的四件事,最後附兩條 minor 備註。

**1. 會凍結、補凍、重算判定的入口,遇到非綠判定怎麼辦**

| 入口 | 遇到非綠判定 |
|---|---|
| `loop replay --freeze`(首次凍結) | 只有處置閘回 rc2 才擋。rc1 照樣凍,結束時印「已凍結」、rc 0。 |
| `loop replay --freeze --note`(重凍) | 同上。重凍紅燈迴圈,舊判定檔歸檔,新判定檔寫入 `{"rc":1,"fails":["留痕"]}`。 |
| `replay_weekly.py` 補凍 | 同上,只對沒有判定檔的迴圈做,而且不看現在是不是綠。 |
| `loop replay --golden`(回放) | 重算結果跟凍結不同就報邏輯漂移、rc 1。判準丟例外時,新程式判失敗而不是 traceback。 |
| `loop status --disposal` | 非綠就回 rc1,不放行。 |

- 前三個入口接受非綠,是既有行為,不是這次改動帶進來的。
- 我實跑確認了:在實驗複本裡重凍「消費專案接入靜默失效」,rc 0,判定檔存的是 rc 1。
- 帳上 307 份判定檔,有 5 份是 rc1,跟新增的 Issue 與計劃寫的數字相符。
- 這次改動沒有新增「凍結時把判準例外凍成紅燈」的路徑,也沒有讓凍結變更鬆。

**2. 舊帳在新程式下回放,是否完全一致**

- 我用改前提交 `cb832b56` 和現在的 `151c65b2` 各自 clone 一份,把 `governance/replay/*/verdict.json` 全部對跑 `--golden`。
- 改前有 306 份,現在多 1 份(「引句錨定整段比對」,新凍結的);這 1 份用改前程式回放也是 PASS。
- 這 306 份的 rc 與逐行輸出完全一致,唯一差別是多一行 `[disposal] 引句判準:legacy(帳上無章)`。
- 唯一的 rc1 是「消費專案接入靜默失效」(intake sha 不符),改前和現在都一樣。這是既有的紅燈,計劃裡已經有 Issue 記錄。
- `python3.14 scripts/test_lumos.py -k quote` 跑完 181 項全過。
- `quote-check --compare-rules` 對本 repo 的帳跑完要 22 秒,峰值記憶體約 1.5 GB;沒有崩潰或逾時。

**3. 還原這個提交後,帳上的欄位與事件**

- **`canary-log` 的 `quote_rule` 欄**:本 repo 帳上已有 3 列載體帶 `legacy` 章。
  - 我把改前程式放到這份帳上跑 `loop status --disposal`,三種章值(`legacy`、`full-span-v1`、亂填 `bogus`)和刪掉章,結果都是同一個 PASS,舊程式忽略這個欄位。
  - 新程式遇到亂填的 `bogus` 章會判失敗,遇到沒有章則照 `legacy`;這跟計劃寫的一致。
- **`governance-log` 的 `quote-rule:` 事件**:我寫入 3 筆真實格式的事件,對比兩版 `gov --stats`。
  - 改前程式把它們算進「缺 refuted-set」(3 變 6),總數不變。
  - 這點計劃的〈回退〉已經明文寫了(patch 第 250 行),所以不算新發現。

**4. 處置閘新增的輸出行,會不會影響解析輸出的腳本**

- 新增兩種行:`[disposal] 引句判準:…`(每次都印),以及失敗時縮排四格的 `    診斷:lumos quote-check <絕對路徑> --spec <絕對路徑> --rule <章>`。
- 我查了 `scripts/*`、`governance/autonomous_loop/`、`skills/`、`.github/`、`~/.claude/hooks`,沒有任何腳本逐行解析處置閘或 quote-check 的輸出。
- 唯一讀輸出的是 `replay_weekly.py`,它在 rc 不為 0 時對輸出全文找 `邏輯漂移`、`帳被動`、`凍結檔被動`、`佚失` 這幾個詞。目前 repo 路徑和卷證目錄名都沒有這些詞,不受影響。
- 判定檔裡存的 `fails` 標籤沒變,所以凍結檔與回放比對的格式沒動。

**備註(minor,不列為 finding)**

- 診斷行現在帶絕對路徑,若將來有迴圈目錄名或 repo 路徑含上面那幾個詞,且回放同時 rc 非 0,週跑會把「錯誤」誤分成「紅燈」。目前條件不成立。
- `_retro_read_bytes` 超限時的訊息寫死「256KB」,比較模式的上限是 128 MB 和 4 MB;訊息被 `except OSError` 吞掉、只計入「讀不到」,使用者看不到,實害為零。

實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/r4-回滾-sonnet/` 已刪除,沒有改動 repo。

總結:最高等級 clean,blocking 共 0 條
