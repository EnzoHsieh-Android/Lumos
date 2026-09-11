---
name: python-idioms
description: 寫或審 Python（asyncio 長跑服務、機器人、排程、資料處理腳本）代碼前必讀——通用不變量層的慣例規則：並行等待與有界並行、不阻塞事件迴圈、task 參照與取消、外呼逾時與重試、例外與程序生命週期、金額用 Decimal、時間帶時區、資源釋放、邊界驗證與秘密。每條附壞例→好例與機檢對照（ruff／mypy／bandit）。框架選擇（Django vs FastAPI、SQLAlchemy vs 其他 ORM、pandas vs polars、requests vs httpx）不在此裁——查該專案圖譜。
---

# Python 慣例（通用不變量層）

**這份文件治的病**：AI 寫出「正確但笨、或正確但會在半夜炸」的 Python——`async def` 裡塞了 `time.sleep` 和 `requests.get` 讓整個事件迴圈停擺、`asyncio.create_task` 的回傳值沒存（task 可能半路被回收、例外無聲蒸發）、`requests` 沒給 timeout（對方掛了你永遠卡住）、金額用 `float` 算到差一分錢、`datetime.now()` 不帶時區讓跨時區比對全錯、`except Exception: pass` 把真正的錯吞掉。這些不炸在單元測試上，炸在長跑幾天之後、在網路抖一下的那一刻。

**分層原則**：只寫不隨框架選擇改變的原則。Django 還是 FastAPI、哪個 ORM、pandas 還是 polars——查該專案的知識圖譜與 CLAUDE.md（`lumos search <關鍵字>` 起手）。規則以「可注入」「runtime schema」等能力措辭，不點名框架。

**機檢欄說明**：`ruff:代碼`＝Ruff 規則（⚠ Ruff 預設只開 `E`／`F` 兩族，下面引用的 `ASYNC`／`RUF`／`S`／`DTZ`／`B`／`G`／`T20`／`SIM`／`PERF`／`TRY`／`BLE` 要在 `pyproject.toml` 的 `select` 明確開，沒開等於沒裝，接法見文末接線表）；`mypy`＝型別檢查（`--strict`）；`bandit:代碼`＝Bandit；`自訂`＝可寫 ast-grep 規則；`不可機檢`＝只有本文件與審查鏡頭能守——排最前面。

> **誠實邊界（2026-09-11）**：本文件是官方文件整理，規則代號全部用本機 `ruff 0.16.7` 的 `ruff rule <代號>` 逐條核對過；**尚未在任何真 Python 專案上實跑**。第一個接入的是一個自動交易專案（asyncio 長連線＋pandas 回測），它踩到的坑要回填進來。

---

## 一、async 紀律（本文件存在的理由）

> **審查時機管道**：本文標「⚠ 不可機檢」的效能／適用性條目，其載重問已由 lumos 效能檢核機制在三時機自動推送（動手前 impact hook 注入／push 前 pitfalls advisory／終審 code-loop 鏡頭；內容源＝lumos-toolchain 圖譜 Systems/效能檢核目錄 Python 段，雙向同步義務）——可機檢條目歸 Ruff，勿靠人記。

### R1. 互不依賴的等待必須並行 ⚠ 不可機檢，頭號條款
```python
# ✗ 笨（延遲相加）
balance = await client.balance()
positions = await client.positions()

# ✓ 一起飛（3.11+ 優先用 TaskGroup：一個失敗會取消其他，例外不會被吞）
async with asyncio.TaskGroup() as tg:
    b = tg.create_task(client.balance())
    p = tg.create_task(client.positions())
balance, positions = b.result(), p.result()
# 個別失敗不連坐、要每個結果 → asyncio.gather(..., return_exceptions=True)
```
- 判斷順序：先確認無資料依賴，再確認無共享資源（同一個 DB transaction／同一條連線的查詢**不准**平行），才並行。
- 依據：[Python docs — asyncio.TaskGroup](https://docs.python.org/3/library/asyncio-task.html#task-groups)

### R2. `gather` 不是佇列、不是限流器 ⚠ 不可機檢，生產最常炸
```python
# ✗ 一千個代號同時打 API：吃到對方速率限制被封、或打爆自己的連線池
await asyncio.gather(*(fetch(sym) for sym in symbols))

# ✓ 有界並行
sem = asyncio.Semaphore(10)   # 上限依對方的速率限制算，寫成常數並註明依據
async def bounded(sym):
    async with sem:
        return await fetch(sym)
await asyncio.gather(*(bounded(s) for s in symbols))
```
- 集合大小不是你控制的（來自 DB／外部輸入／交易所清單）就一律有界。

### R3. `create_task` 的回傳值要存起來，例外要有人接
```python
# ✗ 事件迴圈只留弱參照：task 可能跑到一半被回收；裡面的例外沒人看見
asyncio.create_task(heartbeat())

# ✓ 存強參照，完成時移除並檢查例外
background = set()
t = asyncio.create_task(heartbeat())
background.add(t)
t.add_done_callback(background.discard)
# 更好：放進 TaskGroup，生命週期跟著作用域走
```
- 機檢：`ruff:RUF006`（asyncio-dangling-task）。
- 依據：[Python docs — asyncio.create_task「Important」段](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task)

### R4. `async def` 裡禁同步阻塞；CPU 重活離開事件迴圈
- `time.sleep`、`requests.*`、`urllib.request.urlopen`、同步 `open()` 讀大檔、`subprocess.run`、大 JSON 解析、大迴圈——任一個在 coroutine 裡＝所有 task 一起停（行情漏收、心跳逾時、WebSocket 被伺服器斷線）。
- 換法：`asyncio.sleep`、非同步 client（能力措辭：支援 async 的 HTTP client）、`asyncio.to_thread(同步函式)`；CPU 重活用 `ProcessPoolExecutor`（標準 CPython 有 GIL，執行緒不會讓 CPU 重活變快）。
- 「`while True:` + `sleep` 輪詢」優先改成等事件、佇列或交易所推播。
- 機檢：`ruff:ASYNC251`（time.sleep）、`ruff:ASYNC210`（阻塞 HTTP）、`ruff:ASYNC230`（阻塞 open）、`ruff:ASYNC220`（同步建子程序）、`ruff:ASYNC110`（忙等迴圈）。

### R5. 每個外呼都有逾時；重試有退避、有上限 ⚠ 部分不可機檢
```python
# ✗ requests 預設不逾時：對方不回，你就永遠卡在這行
r = requests.get(url)

# ✓ 同步：明確 timeout（連線, 讀取）
r = requests.get(url, timeout=(3.05, 10))
# ✓ 非同步：整段加上限（3.11+）
async with asyncio.timeout(10):
    data = await client.get(url)
```
- 重試：指數退避＋上限＋只重試「可安全重做」的操作；不可逆操作（下單、付款、寄信）的重試規則見 R17。
- 連線／session／client 在程序生命週期建一次重用，不要每次請求新建。
- 機檢：`ruff:S113`（requests 無 timeout）、`ruff:ASYNC109`（async 函式自帶 timeout 參數，改用 `asyncio.timeout`）。
- 依據：[Requests docs — Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)、[Python docs — asyncio.timeout](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout)

### R6. 不准吞例外；不准吞取消
```python
# ✗ 什麼錯都當沒發生
try:
    place_order(o)
except:            # 連 KeyboardInterrupt、CancelledError 都吞
    pass

# ✓ 只接你知道怎麼處理的，其他往上丟
try:
    place_order(o)
except OrderRejected as e:
    log.warning("order rejected: %s", e.reason)
```
- `asyncio.CancelledError` 是 `BaseException`（3.8 起），`except Exception` 接不到它——這是對的；但裸 `except:` 或 `except BaseException:` 會把取消吞掉，關閉流程就卡住。真的要接取消做清理，清理完**重新 raise**。
- 機檢：`ruff:E722`（裸 except）、`ruff:BLE001`（接太寬）、`ruff:S110`（try-except-pass）。

---

## 二、錯誤與程序生命週期

### R7. 例外要保留原因；邊界才轉換
```python
# ✗ 原始例外斷掉，stack 看不到真兇
except KeyError:
    raise ConfigError("missing key")

# ✓
except KeyError as e:
    raise ConfigError("missing key") from e
```
- 在 `except` 裡記錄錯誤用 `log.exception(...)`（自動帶 stack），不用 `log.error(...)`。
- 機檢：`ruff:B904`（except 內 raise 沒 from）、`ruff:TRY400`（except 內用 error 而非 exception）。

### R8. 長跑程序要有優雅關閉 ⚠ 不可機檢
- 收到 `SIGTERM`／`SIGINT` → 停止接新工作 → 取消背景 task 並等它們收尾 → 關連線／session → 退出。沒這條，每次重啟都可能留下半途的狀態（掛單沒記錄、檔案寫一半）。
- 能力措辭：`loop.add_signal_handler`（Unix）或框架提供的 lifespan 掛鉤；重啟交給外部 supervisor（systemd、launchd、容器平台）。
- library 碼不准 `sys.exit()`，只有入口檔可以。

### R9. 日誌用 logging，不用 print；log 參數用延遲格式化
```python
# ✗
print(f"filled {qty} @ {price}")
log.info(f"filled {qty} @ {price}")     # 就算這個等級沒開也照樣先組字串

# ✓
log.info("filled %s @ %s", qty, price)
```
- 機檢：`ruff:T201`（print）、`ruff:G004`（logging 用 f-string）。

---

## 三、資料與數值

### R10. 金額、價格、數量用 `Decimal`，不用 `float`；`Decimal` 從字串建 ⚠ 部分不可機檢
```python
# ✗ 二進位浮點：0.1 + 0.2 != 0.3；累加與比較會漂
total = 0.1 + 0.2
qty = Decimal(0.1)                 # 已經是錯的值：Decimal('0.1000000000000000055511151231257827…')

# ✓
from decimal import Decimal, ROUND_DOWN
qty = Decimal("0.1")
qty = (raw_qty / step).to_integral_value(rounding=ROUND_DOWN) * step   # 對齊外部系統給的精度規則
```
- 外部系統（交易所、金流）回的數字用字串接進 `Decimal`，捨入方向寫明（`ROUND_DOWN`／`ROUND_HALF_UP`）且只在一處做。
- 統計與回測的大量運算用 float／numpy 可以，**要送出去的那個數字**（下單量、價格、金額）在邊界轉成 `Decimal` 並對齊精度。
- 機檢：`ruff:RUF032`（Decimal 用 float 常數建）；「金額用了 float」本身不可機檢。
- 依據：[Python docs — decimal](https://docs.python.org/3/library/decimal.html)

### R11. 時間一律帶時區（存 UTC，顯示才轉）；量時間間隔用單調時鐘
```python
# ✗ naive datetime：跟帶時區的比會直接炸，或默默用錯時區
now = datetime.now()
now = datetime.utcnow()            # 3.12 起棄用，而且回的還是 naive

# ✓
now = datetime.now(timezone.utc)
t0 = time.monotonic()              # 算逾時、間隔用這個；系統時間被校時會跳
```
- 機檢：`ruff:DTZ005`（now 不帶 tz）、`ruff:DTZ003`（utcnow）。

### R12. 不准可變預設參數；閉包別抓迴圈變數
```python
# ✗ 所有呼叫共用同一個 list
def add(order, book=[]): ...
# ✓
def add(order, book=None):
    book = [] if book is None else book
```
- 類別層可變屬性（`items: list = []`）同理，所有實例共用。
- 機檢：`ruff:B006`（可變預設參數）、`ruff:RUF012`（類別層可變預設）、`ruff:B023`（閉包抓迴圈變數）。

---

## 四、資源與記憶體

### R13. 檔案、連線、鎖一律用 `with`／`async with` 管
- 例外路徑也要釋放；session／client／連線池在程序層建一次（見 R5），不要在函式裡建了不關。
- 機檢：`ruff:SIM115`（open 沒用 context manager）。

### R14. 大資料逐塊處理；長活集合有上限 ⚠ 不可機檢
- 大檔逐行或分塊讀（`for line in f`、`read_csv(chunksize=…)`）、大查詢用 cursor 分批，不用 `read()`／`fetchall()` 整包進記憶體。
- 模組層的 dict／list 當快取＝沒有上限的洩漏；要快取就用有上限的（`lru_cache(maxsize=N)`，不是 `maxsize=None`）或有 TTL 的實作。
- pandas 熱路徑不用 `iterrows`／`apply(axis=1)`／迴圈裡 `concat`，改向量化或先收成 list 最後一次建（效能題 `py-hotpath` 會在審查時問）。

---

## 五、邊界、型別與安全

### R15. 外部輸入在邊界驗證後才進領域層；型別檢查開 strict
```python
# ✗ 把外部 JSON 直接當領域物件用
price = msg["p"]                       # KeyError、型別是字串還是數字都不知道

# ✓ runtime schema 驗證（能力措辭；pydantic／attrs＋cattrs／自寫都行）→ 得到窄型別
tick = Tick.model_validate(msg)        # 驗證失敗在邊界就擋下
```
- 型別：新專案 `mypy --strict`；公開函式都要有型別註記，`Any` 要有理由。
- 機檢：`mypy --strict`（`disallow_any_generics`、`disallow_untyped_defs`…）。

### R16. 秘密不進 log、不進錯誤訊息、不進 repo
- API key／secret 從環境變數或秘密管理讀；`.env` 進 `.gitignore`；log 物件序列化前遮罩；錯誤對外只給錯誤碼。
- 機檢：`ruff:S105`（寫死的密碼字串）、`bandit`；`自訂`（log 呼叫帶 `secret`／`api_key` 欄位）。

### R17. 不可逆的外部動作（下單、付款、寄信、刪資料）要冪等或有守衛 ⚠ 不可機檢
- 重試機制（R5）、斷線重連、程序重啟都保證同一動作會再來一次：用冪等 key（例如自己產生的 client order id）、去重表、或送出前「查一下是不是已經做過」，擇一並寫進節點的 `[guard:]`。
- 對應圖譜 ★IRREVERSIBLE★ 合約的 rollback／guard 要求。

### R18. 不反序列化不信任的資料；不用 shell 拼指令
- `pickle.load` 不信任的來源＝任意程式碼執行；子程序用參數列表，不用 `shell=True` 拼字串。
- 機檢：`ruff:S301`（pickle）、`ruff:S602`（shell=True）。

---

## 接線表（裝了不等於開了）

| 規則 | 工具 | 前提 | 動作 |
|---|---|---|---|
| R3–R6、R9–R13、R16、R18 | Ruff | `select` 要明確開下面這些族 | 見下方設定 |
| R15 型別 | mypy | `--strict` | CI 當閘；★沒有 SARIF 輸出★（只有 `--output json`），不登進 `.lumos/lint.json` |
| R16、R18 資安 | Bandit | 裝 `bandit[sarif]` | `bandit -r src -f sarif -o {LINT_SARIF_OUT}` 可登進 `.lumos/lint.json` |
| 依賴漏洞 | pip-audit | — | CI 報表；無 SARIF（只有 json／cyclonedx） |
| 全部 Ruff 告警 | SARIF 進審查 | Ruff 內建 | `.lumos/lint.json`：`{"py": ["ruff check --output-format sarif -o {LINT_SARIF_OUT} src"]}`，接好跑 `lumos lint-check --smoke` |

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "B", "ASYNC", "RUF", "S", "DTZ", "G", "T20", "SIM", "PERF", "TRY", "BLE"]
# 中文註解與說明文字的全形標點不是混淆字元——沒這行，RUF001/002/003 會把每個「：（）」都報成錯
# (2026-09-11 首個接入專案第一次跑 ruff 就踩到)
allowed-confusables = ["：", "，", "（", "）", "；", "！", "？", "～", "｜"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]    # 測試裡用 assert 是正常的

[tool.mypy]
strict = true
```

**依據總表**：[Python docs — Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)、[Python docs — Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)、[Python docs — decimal](https://docs.python.org/3/library/decimal.html)、[Requests — Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)、[Ruff rules](https://docs.astral.sh/ruff/rules/)、[mypy — strict](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)、[Bandit](https://bandit.readthedocs.io/)。
