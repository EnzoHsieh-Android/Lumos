severity: minor

審查範圍:`/tmp/code-macrobench-r4.patch`(repo 在 `macrobench-receipt`,補丁已套上,行號以該 repo 為準)。結論:程式本體跟 `_compose_metrics_mode` 一族是同一套做法,沒有第二種做法。不對齊共 2 條,都在測試守門與文件同步,結構沒問題。

## 問 1:分層與依賴方向

一致,沒有跨層直呼。

- **放的位置**:新碼緊接在 `_compose_metrics_mode` 之後、`_lint_watch_mode` 之前(`scripts/lumos:39349` 起),跟鄰居同一個「vault-free 轉接器」區塊。
- **呼叫鏈**:`main()` 的 `if args.cmd == "macrobench":` 分派 `_macrobench_mode`。這跟 `compose-metrics` 的分派寫法一樣(`scripts/lumos` 的 compose-metrics 分派段)。
- **子命令註冊**:`--repo` 的 `dest="macrobench_repo"`、`--json` 的 `dest="as_json"`、`--update-baseline` 都照 compose-metrics 那段 argparse。`HELP_WHEN` 也補了一列。
- **共用工具**:寫基準檔用 `_write_lf`(`scripts/lumos:28446`,全專案的原子寫入原語)。數值判斷用 `_secev_num`(`scripts/lumos:8554`)。兩者都是既有工具,沒有自創。
  - 鄰居 `_compose_metrics_mode` 寫基準檔用裸 `open(...)`(約 `scripts/lumos:39289`)。新碼改用 `_write_lf`,是往專案原語靠,不算分歧。
  - `_secev_num` 的名字帶 secev 前綴,借用到別的功能家族。它是通用的 JSON 數值判斷,我不當成不一致。
- **函式拆分**:鄰居是一支約 270 行的單體。新碼拆成十幾個小函式。這是切法不同,不是依賴方向問題。

## 問 2:命名與錯誤處理

一致,沒有不對齊項。

- **命名**:`_macrobench_*` 私有函式、`MACROBENCH_*` 常數,對應 `_compose_*`、`COMPOSE_RATIO_EPS`。
- **設定壞掉**:stderr 印 `擋下:…`,回 rc2。鄰居是同一套(`scripts/lumos:39190` 附近的 compose-metrics 設定檢查)。
- **有退步或基準缺失**:回 rc0。基準讀不了時「不比、也不蓋掉」,跟鄰居的 `baseline_unreadable` 同一種做法。
- **日誌**:只用 `print`,沒有 logging 模組。這跟鄰居一樣。
- **缺設定檔時的輸出**:鄰居在非 JSON 模式印空字串,新碼印一句「沒接 Macrobenchmark」。這是形狀略有出入,但沒有害處,我不算進不對齊。

## 問 3:第二種做法

測試結構一致,只有「讀 repo 內真資料檔」的守門寫法跟主流不同。文件同步有一處漏列。

測試部分已核對的對齊點:

- 純函式測試用 `_load_lumos_inproc()`(`scripts/test_lumos.py:238`),比鄰居 `t_compose_diff` 自己 `SourceFileLoader` 載入更靠近共用 helper。
- CLI 測試用 `sp.run([sys.executable, GRAPHCTL, ...])`,跟 `t_compose_metrics_cli`(`scripts/test_lumos.py:17284`)一樣。
- 驗證用 `check(...)`,暫存目錄用 `TemporaryDirectory`。
- 讀 repo 資料檔的路徑寫法 `Path(GRAPHCTL).resolve().parent.parent / "governance" / …`,跟既有測試相同(例:`scripts/test_lumos.py:1131`)。這個寫法還是 `rx_real` 正規式(`scripts/test_lumos.py:98`)明文認得的。

文件同步已核對:

- `ARCHITECTURE.md` 的 94 個命令數與社群 linter 橋那格已改。
- `reference.md` 的計數、子命令全覽與表格列已改。
- `commands/INDEX.md` 的 04 列已改,`04-自檢與健康.md` 已新增一列。
- 命令數漂移守衛 `t_docs_enumeration_drift` 抓得到的部分都對上了。

張力一(測試守門):
- 既有:讀「來源 repo 才有」的產物前,用 `_need_src(...)` 守門(全檔 188 處),消費端沒有就記成 skip(`scripts/test_lumos.py:146`)。
- 隱患:`governance/research/macrobench/…` 若不存在(例如消費端或精簡副本跑測試),這兩支測試的失敗方式不同。KDS 那支靠自寫的 `check("前置…", real.exists())`,會變成紅,不是 skip。實機那支沒有任何守門,`shutil.copy` 直接噴例外。同一份補丁裡也有兩種寫法。
- 這次:兩支測試各自守門,而且寫法不同。
- 不一致:1 檔(`scripts/test_lumos.py`)。

張力二(文件同步):
- 既有:同類轉接器 `lint-watch`、`compose-metrics` 在 `docs/methodology/圖譜即合約.md` 的轉接工具總表各有一列。`compose-metrics-adapter` 在 `MOC/index.md` 的「技術棧知識與 linter 橋接」節也有一行。
- 隱患:新指令及其 `Systems/macrobenchmark-adapter` 節點,兩處都沒列。讀總表或總索引的人會看不到這個指令。
- 這次:補了 `ARCHITECTURE.md`、`reference.md`、`INDEX.md`、`04-自檢與健康.md`,漏了這兩處。
- 不一致:2 檔。

**P1**
severity: minor
blocking: 否
引句:「check("前置:真結果檔在 repo 裡", real.exists(), str(real))」
佐證:新碼 `scripts/test_lumos.py:17555`(KDS 那支自寫前置檢查)和 `scripts/test_lumos.py:17650`(實機那支完全沒守門),對照 `scripts/test_lumos.py:146` 的 `_need_src` 與 `scripts/test_lumos.py:4827` 的用法。
⚠ 同檔 `scripts/test_lumos.py:1131` 的 `t_only_spec_ready_notice_uses_spec_header` 讀 `governance/autonomous-loop.sh` 也沒用 `_need_src`,所以既有做法本身不是全面一致。我判 minor,不是 major。

**P2**
severity: minor
blocking: 否
引句:「**Android 啟動與滑動效能(vault-free)**」
佐證:`docs/methodology/圖譜即合約.md:161` 有 `compose-metrics` 一列、沒有 macrobench。`docs/lumos-toolchain-knowledge/MOC/index.md:112` 有 `[[Systems/compose-metrics-adapter]]`、沒有 `macrobenchmark-adapter`。
⚠ MOC 總索引只列了 103 個 Systems 節點裡的約 76 個,不全列,所以那一處不確定算漏;方法論總表那一列我較有把握。兩處都沒有測試或推送守衛會擋,所以是 minor。

不對齊共 2 條,其中 major 0 條
