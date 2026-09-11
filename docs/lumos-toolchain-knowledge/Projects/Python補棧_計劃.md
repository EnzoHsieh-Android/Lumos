---
type: project
status: doing
created: 2026-09-11
updated: 2026-09-11
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
aliases:
  - Python 補棧
  - python-idioms
  - py 效能追問
related:
  - "[[Projects/iOS與Node後端補棧_計劃]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/棧別提問表態閘]]"
  - "[[Systems/arch-alignment-lens]]"
  - "[[Projects/CheckT-Python-profile_計劃]]"
  - "[[Projects/idioms自維護迴路_計劃]]"
summary: |-
  FLAG:DECISION
  KEY:★立案(2026-09-11 Enzo 要開一個幣安自動交易專案:「挑一個你覺得自動交易合適的語言,lumos 沒適配就幫她做好」)★——選 Python;對照 iOS/Node 補棧那七格盤點,Python 早就有測試 profile(2026-07-25)、符號 profile、CODE_EXTS_T 也收了 .py,缺四格:①_STACK_QUESTION_SPECS 沒有 py 題組 ②_ARCH_IDIOM_SKILL 沒有 .py→慣例 skill ③沒有 python-idioms skill ④linter精選目錄與效能檢核目錄沒有 Python 段
  KEY:補法照 iOS/Node 補棧版型,零新機制——py 五題(py-eventloop/py-parallel/py-external/py-memory/py-hotpath)接進既有三時機;.py→python-idioms;新 skill python-idioms 18 條;兩份目錄各加 Python 段、題目 id 對照表加五列;ONBOARDING 與 design-loop 範本的 idioms 清單同步 [test:t_python_stack_wiring] [test:t_stack_question_triggers]
  KEY:★題組刻意偏「長跑程序/機器人/資料處理」,不收 Django/FastAPI 特有題★——首個消費端是自動交易機器人(asyncio 長連線+pandas 回測);Web 框架專題等第一個 Web 消費端出現再評估
  KEY:世界事實(2026-09-11 本機實跑核對,不信網文)——ruff 0.16.7 內建 --output-format sarif、skill 引用的 28 條規則代號逐條 `ruff rule` 查過都存在;bandit -f sarif 要裝 bandit[sarif];mypy 2.3.1 只有 --output json;ty 0.0.80 只有 full/concise/gitlab/github;pip-audit 2.10.1 無 SARIF;lint.json 的鍵是副檔名,Python 寫 "py" 不用改程式
  KEY:刻意沒做——design-loop(照 iOS/Node 先例:散文 skill 走首個接入專案實跑回填,程式部分只加表格條目且有測試與翻紅驗證);docstring 內的觸發詞會誤觸發(_stack_norm_line 不認三引號跨行字串,寧多問不漏問,未修)
  PRIOR-ART:借既有 profile 制與 iOS/Node 補棧七格版型(零新機制);idioms 版型借 node-idioms;規則代號與輸出格式以本機實跑為準
  DEP:scripts/lumos(_STACK_QUESTION_SPECS/_ARCH_IDIOM_SKILL)｜skills/python-idioms｜Systems/效能檢核目錄、Systems/linter精選目錄｜ONBOARDING.md｜skills/lumos-design-loop/templates.md
decisions:
  - content: "Python 效能追問題組偏長跑程序/機器人/資料處理,不收 Web 框架特有題"
    context: "Python 用途很散(Web、資料、腳本、機器人);題數會被測試釘住只能折不能加,一開始收錯方向之後很難調;首個消費端是幣安自動交易機器人(asyncio 長連線+pandas 回測)"
    alternatives_considered:
      - "照 Node 題組的形狀,偏 Web 後端(請求路徑阻塞、ORM N+1、連線池):跟其他後端棧一致,但首個消費端大半題用不上"
      - "兩邊都收(八到十題):覆蓋廣,但觸發面太寬,每次改 .py 都亮一堆題,表態成本變高"
      - "偏長跑程序/資料處理(事件迴圈、有界並行、外呼逾時重試、記憶體、pandas 熱路徑):對首個消費端最載重"
    why_chosen: "五題裡事件迴圈、並行、外呼、記憶體四題對 Web 後端也成立,只有 py-hotpath 偏資料處理;等於用最少的題同時照顧兩種用途,又對首個消費端最有用"
    trade_offs: "Django/FastAPI 特有的坑(ORM 惰性載入、middleware 同步阻塞)沒有專題;第一個 Web 消費端接入時要評估是否折進 py-memory/py-eventloop 或加題"
    decided: 2026-09-11
    valid: true
---
# Python 補棧（2026-09-11）

> 白話：Enzo 要開一個幣安自動交易專案，讓我挑語言，lumos 不支援就補上。我選了 Python。lumos 大部分功能不看語言，綁語言的只有「工具對這個技術棧知道什麼」那一類。Python 在其中一半早就有了（測試怎麼認、符號長什麼樣子），缺的是審查時該問的效能題、寫碼慣例 skill，以及兩份目錄的 Python 段。這篇把缺的補齊。**全部只在合成樣本上測過，第一個真的用到的是那個交易專案。**

## 盤點：Python 在七格裡的狀態

| 格子 | 補之前 | 這次 |
|---|---|---|
| 測試綁定 profile | ✅ 已有（[[Projects/CheckT-Python-profile_計劃]]） | 不動 |
| 符號形狀 profile | ✅ 已有 | 不動 |
| 程式碼副檔名清單 | ✅ 已收 `.py` | 不動 |
| 效能追問題組 | ❌ | 加 `py` 五題 |
| 副檔名→慣例 skill | ❌ | `.py` → `python-idioms` |
| linter 目錄 | ❌ | 加 Python 段（ruff／mypy／bandit／pip-audit／ty） |
| 效能檢核目錄 | ❌ | 加 Python 段＋題目 id 對照五列 |
| 慣例 skill | ❌ | 新增 `python-idioms` 18 條 |

## 五題怎麼選的

- **事件迴圈（py-eventloop）**：`async def` 裡的同步阻塞。對交易機器人最致命——一個 `time.sleep` 讓行情漏收、心跳逾時被交易所斷線。
- **並行與上限（py-parallel）**：`gather`／`TaskGroup` 並行、`Semaphore` 有界、`create_task` 回傳值要存。
- **外呼與重試（py-external）**：`requests` 預設不逾時；重試要有退避上限，且不能對下單這類不可逆操作盲目重送。
- **記憶體與資料量（py-memory）**：整包讀進記憶體、無上限快取、迴圈逐筆查。
- **熱路徑（py-hotpath）**：pandas 的 `iterrows`／`apply(axis=1)`／迴圈 `concat`，回測會踩。
- **沒收的**：「迴圈裡重複編譯 regex」——Python 的 `re` 模組自己有編譯快取，這條在 Python 不是真問題，收了等於教錯。

觸發字照既有家規：範式詞（`asyncio.gather`、`TaskGroup`）＋反面詞（舊法會出現的字：`threading.Thread`、`time.sleep`、`urllib.request`、`range(len(`），讓「用舊寫法寫同一件事」也會亮同一題。

## 驗證

- 新測試 `t_python_stack_wiring`：.py 改動附五題、asyncio.gather 讓 py-parallel 適用、測試檔不附、.py 派 python-idioms、對映表指到的 skill 都真的存在。
- 既有 `t_stack_question_triggers`：全表 id 集合加五個 py id；加 py 的命中／不命中樣本、舊法樣本、log 字串假命中樣本。
- 翻紅驗證（2026-09-11 實跑）：拿掉 `.py→python-idioms` 對應 → 兩條翻紅；把 skill 資料夾改名 → 存在性那條翻紅；還原後全綠。
- 相關子集全綠：stack_question 75、pitfalls_stack 9、pitfalls_diff_arch 4、impact_hook_stack 16、python_profile 10、checky_ 14、dispositions 100。

## 誠實邊界與回頭條件

- **零真專案**：五題的觸發字、skill 的 18 條都只在合成樣本和文件上成立。第一個接入的交易專案跑一輪真的代碼審後，要回來看：哪題從來沒亮過、哪題亮了但每次都答「不適用」（死題候選）、哪些坑 skill 沒收。
- REVISIT:2026-11-11 交易專案若已跑過至少一次代碼審，用 gov --stats 看 py 五題的表態分佈並回填 skill；若兩個月內沒有任何 Python 專案接入，這批標成未實證
- **首個接入專案的第一筆回填（2026-09-11，當天）**：交易專案第一次跑 ruff 就被 `RUF001/002/003` 擋——它把中文註解裡的全形標點（：，（））當成「長得像 ASCII 的混淆字元」。python-idioms 的 pyproject 範例已補 `allowed-confusables`；中文團隊的 Python 專案一律要帶這行。
- **docstring 誤觸發**：比對前只剝單行字串，三引號跨行的 docstring 裡出現 `asyncio.gather` 也會讓題亮起來。代價是多問一題，不會漏問，這次不修。
- **合併時機**：這個分支開在獨立工作副本上；工具鏈主目錄另有 session 未提交的改動（治理帳、錨點基準線、MOC），合併前要跟那邊協調，錨點基準線兩邊都動了會衝突。
