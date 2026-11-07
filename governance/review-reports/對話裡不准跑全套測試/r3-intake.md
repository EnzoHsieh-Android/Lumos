# r3 收貨紀錄(對話裡不准跑全套測試)

四席(正確性、通才、繞過、架構對齊)全數交回後一次寫進卷證(提交 4ccb3f9c3)。report-normalize 都不用改;quote-check:正確性、通才、繞過全數錨定;架構對齊 #2 一句錨不到——席位把快照原文「這一條在」寫成「這條在」,其餘字逐字相同。編排者不改席報告;那條講的是「隔離之後才判,HOME 已換成拋棄式目錄」,跟通才 F2(blocker)、正確性 F2 是同一件事,兩席引句都錨得到,機械重現見下表,撈回併入同一處置。

編號:正確性 C1–C5、通才 T1–T7、繞過 R1–R6、架構對齊 A1–A5,共 23 條。

## 先查世界

- PRIOR-ART:三輪同類(用旗標、支數、估耗時猜這次會跑多久)連續被打穿。查的方向:pytest 沒有「依執行環境拒跑」的內建機制,社群做法是在 `conftest.py` 的 `pytest_configure`/`pytest_collection_modifyitems` 依環境變數改行為(https://docs.pytest.org/en/stable/reference/reference.html#pytest.hookspec.pytest_collection_modifyitems ),判斷都是「有沒有帶選擇條件」這種旗標層,不估耗時;CI 端的超時是外層 timeout。採用:回到最簡單的旗標層判斷(沒帶任何篩選就擋),估耗時整段拿掉;繞法(`-k t_`、分片輪流)不再追,寫進天花板,使用者 2026-11-08 人裁接受。

## 人裁

使用者 2026-11-08:「照你建議」。編排者前一則的建議原文:「接受風險、縮成最小形狀:對話裡沒帶 `-k`、`--suite`、`--list`(或只帶 `--shard`)就擋;進入點先存環境值;隔離前記下真的 HOME;照既有附加寫法記計數;掛鉤提示改 `-k <名字>`;`-k t_` 與分片輪流的繞法留在天花板」。

## 重現

| id | 編排者重現 | 結果 |
|---|---|---|
| C1 | 讀第三版做 1:「判斷讀的是當下環境變數;判斷完才把 CLAUDECODE 拿掉」與「這一步在參數解析之後、_fanout_wanted 之前」 | HIT:拿掉在判斷之前,判斷讀不到 |
| T2 | `_isolate_environment()` 改 HOME(`scripts/test_lumos.py` 的 `_isolate_environment`) | HIT |
| A2 | 同 T2 | HIT |
| C3 | 掛鉤 grep 的是 `✗ ` 斷言行,不是測試名;執行器另印 `✗ FAILED <測試名>` | HIT |
| R1 | 第三版只看佔比 | HIT |
| R2 | `--shard i/16` 每片約 6% | HIT |
| 其餘 | 讀計劃與程式對照 | HIT |
