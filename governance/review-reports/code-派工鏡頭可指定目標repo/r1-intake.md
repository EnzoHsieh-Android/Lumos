# code-派工鏡頭可指定目標repo r1 收貨紀錄

七席全回(正確性、併發、邊界、合約、通才、架構對齊、資安),report-normalize 都不用改、quote-check 全數錨定。共 23 條:正1–2、併1–2、邊1–2、合1–7、通1、架1–5、資1–4。

## 根因分組與處置

同輪有 major(邊1、架1、資1),accepted 必空,23 條全部折入。

- G1 連結節點讀到圖譜外(資1):`[[Systems/../../..]]` 或指向 repo 外的符號連結節點,會讀圖譜外的 .md 並把合約行附進派工詞;落點那條有檢查,連結那條沒有(工作樹寫法原本就有這個洞)。→ 連結節點套用跟落點同一支路徑檢查,解析後必須在圖譜資料夾裡;兩種寫法都改。
- G2 提交寫法遇到 NUL 崩潰(邊1、正1):反引號路徑含 NUL 時 `_lens_git` 丟 ValueError,沒有 lens_fail,掛鉤靜默放空;工作樹寫法同一份計劃正常。邊界席判 major、正確性席判 minor,取嚴。→ 候選路徑先擋 NUL(同 `_spec_commit_has`),`_lens_git` 一併接 ValueError。
- G3 提交寫法的 git 呼叫數沒有上限(邊2、正2、併1):找不到的候選與連結每個都跑一次 git,大計劃會讓掛鉤逾時。→ 改成批次查(一次 `ls-tree -r` 或 `cat-file --batch-check`),並把這幾處收進同一個時間預算。
- G4 載入掛鉤檔另起一套(架1):`_spec_freeze_hook_lumos` 自組載入,沒設 `dont_write_bytecode`,會在掛鉤目錄留 `__pycache__`。→ 把既有的 `_handoff_load_hook` 一般化成「給路徑與必備函式名」,兩處共用。
- G5 spec-freeze 的輸出位置與寫法(資2、併2、架2):`--out` 可以寫到任何位置(自動建多層目錄、寫進系統設定目錄、跟著符號連結上層);中斷時暫存檔殘留;原子寫入多一份。→ `--out` 必須在 repo 內(或 governance/review-reports 底下)、上層每一段不准是符號連結;暫存檔清理接 BaseException;共用 `_write_lf` 的位元組核心。
- G6 自由文字進派工詞(資3):計劃路徑沒過嚴格字元集,原樣印進「計劃來源」那行。→ 路徑用跟節點名同一套字元集,不合只印「路徑含不收的字元」。
- G7 git replace(資4):跟其他三個分支同一族。→ lumos 主程式入口加 `os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"`(四個分支逐字同一行,強制設值,不用 setdefault)。
- G8 寫法對齊(架3、架4、架5、通1):記事件兩種寫法、例外清單變窄;掛鉤失敗代碼清單沒有守衛;spec-freeze 的失敗代碼沒登記。→ 記事件收成一種、例外接回 Exception;代碼清單由同一份推導並加守衛;spec-freeze 代碼登記成常數。
- G9 文件與測試缺口(合1–合7):節點內容取哪一版沒有測試能分辨;NFD 守衛、5 個上限、可執行權限、`only_in_commit`、注入框沒有測試;派工單記 `spec_commit` 沒寫進 SKILL.md 與 templates;工作副本、快照、指紋三者怎麼對齊沒寫;lands_in 的那篇沒改;實作紀錄漏列兩處偏離(目標架構段的 vault 取法、記事件例外範圍)。→ 逐條補測試(各做一次拿掉就紅的變異);手冊寫明「設計審派工前先 spec-freeze,席位材料、快照、--reviewed 都用它產生的那份」與派工單欄位;改 lands_in 那篇;補實作紀錄。

## 修補因果核對

第一輪,沒有上一輪修補。

refuted-set:none。

## 記帳的審查行數

程式各席與資安席記 r1-code.patch(965 行),邊界席記 r1-code.patch 加 r1-tests.patch(1707 行),合約席記 r1-docs.patch 加 r1-tests.patch(1391 行)。
