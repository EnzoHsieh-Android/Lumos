severity: minor

**入口清單(凍結、補凍、重算判定)與遇到非綠判定的處理**
- `loop status --disposal`(以及 `loop next` 代問處置閘):非綠回 rc1,不放行。`loop next` 把輸出收進緩衝,只有 rc2 才轉印 stderr,多印的診斷行不外漏。
- `loop replay --freeze`(首次凍結)與 `--freeze --note`(重凍):只擋 rc2。rc1(判不過)照樣把 `{"rc":1,"fails":[...]}` 寫進 verdict。這是既有行為,Issue〈凍結接受非綠判定〉與計劃〈實務隱患〉都已寫明。
- 週跑補凍 `governance/autonomous_loop/replay_weekly.py`:對有收斂紀錄但沒判定檔的迴圈自動呼叫 `--freeze`,同樣只看 rc。
- `loop replay --golden`:判準丟例外會判失敗,報邏輯漂移(紅燈)。判準章不認得也判失敗。MemoryError 現在照常往外丟,不再被當成判準的錯。
- 我實查帳上 `governance/replay/` 有 307 份 verdict,其中 5 份 rc1,跟 Issue 列的五個迴圈一致。Issue 和計劃寫的「305 份」是舊數字。

**舊帳回放對照(實際跑過)**
- 我在實驗目錄分別 clone 了改前的 cb832b56 和現在的 9ef31b97,各自把 307 個迴圈全部回放一遍,用同一份帳與卷證,只換程式。
- 兩邊輸出逐字比對:除了新程式多印的 282 行 `[disposal] 引句判準:legacy(帳上無章)` 之外完全一致。
- 唯一 rc1 的迴圈是「消費專案接入靜默失效」(intake sha256 不符),改前和現在都一樣。確認是主線既有,不是這次造成。
- 其餘 306 個「回放一致」。
- 舊判準函式(`_quote_rows_legacy`)的函式簽名、說明和函式本體,與改前的 `_quote_rows` 逐字相同。

**note 欄位順序**
- 全部本機工作樹的 `docs/.governance-log.jsonl` 和改前提交的帳裡,都沒有任何 `quote-rule:` 事件,所以不存在舊順序事件。
- 唯一的讀者是 `gov --stats`(用 `startswith("quote-rule:")` 分格),不看欄位順序。

**處置閘多印的診斷行**
- repo 內沒有程式解析處置閘的 stdout。唯一的文字比對者 `replay_weekly.py` 找的是 `邏輯漂移`、`帳被動`、`凍結檔被動`、`佚失`、`golden 過期`。新增的兩種行(判準標籤、診斷指令)不含這些字,現有迴圈目錄名也沒有。

1. REVISIT 2026-12-20 的判讀指令讀不到 `quote=` 片段
severity: minor
blocking: 否
引句:「逐筆讀 note 裡的 `quote=` 片段」
file: `docs/lumos-toolchain-knowledge/Projects/引句錨定整段比對_計劃.md:33`
- 輸入:我在實驗 clone 的 `docs/.governance-log.jsonl` 補了一筆 `quote-rule:full-span-v1 kind=new-only ... quote=...XYZEND` 事件,再跑計劃寫的 `lumos gov --since 60 --full`。
- 結果:`gov` 只印 `detail[:50]`。輸出是 `quote-rule:full-span-v1 kind=new-only cats=stray r`,`report=`、`id=`、`quote=` 全被截掉。
- 影響:上一輪把 `quote=` 排到 note 最後,等於確定它永遠看不到。照 REVISIT 的指令走不下去,只能改讀 jsonl 原檔。
- `grep 'kind=new-only'` 那半段可用(在前 50 字內)。
- 建議:REVISIT 與計劃〈量測與留痕〉那段改寫成「用 `grep` 直接讀 `docs/.governance-log.jsonl` 取 note」,或讓 `gov --full` 不截斷 `quote-rule:` 事件。

2. 計劃與 Issue 的判定檔份數過期
severity: minor
blocking: 否
引句:「2026-10-13 帳上 305 份判定檔有 5 份是 rc1」
file: `docs/lumos-toolchain-knowledge/Issues/凍結接受非綠判定.md:21`
- 現況是 307 個 `verdict.json`,5 份 rc1 的名單仍正確。
- 計劃〈實務隱患〉也寫「帳上 305 份有 5 份 rc1」,同樣過期。
- 影響只有讀者對不上數字。

**沒找到問題的部分**
- 比較模式的路徑防線:我讀程式推演,NUL、孤立代理字元、repo 外絕對路徑、目錄、非一般檔都落到 OSError 算「讀不到」,非 UTF-8 另算。這幾種輸入我沒另外實跑。
- 實跑 `quote-check --compare-rules` 約 23.4 秒、尖峰約 1.38 GB,與計劃寫的實測值相符。
- 擋下事件的 dedup 鍵是 `ts+note`,note 內含 `id=` 隨機碼,順序改動不影響去重。
- 帳上現有一列真實的 `"quote_rule": "legacy"`(迴圈 `code-引句錨定整段比對`,由新程式寫入)。舊程式忽略這個欄位,判準與無章時相同,第一階段還原不產生漂移。

實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/r2-回滾-sonnet/` 已刪除(確認無程序占用),唯讀 repo 未改動。

總結:最高等級 minor,blocking 共 0 條
