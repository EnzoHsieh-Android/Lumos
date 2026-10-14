severity: major

我只讀了固定版本 22f6e132 的 diff 與相關既有檔,沒有跑測試。

## 三問

**1. 分層與依賴方向**

「執行器讀 governance/ 下的資料檔、lumos 子指令改寫進版控檔」本身有前例,做法也對齊。
- 耗時表放 `governance/`,跟 `governance/anchor-baseline.json` 一樣是進版控的資料檔,也列進 `_BOOKKEEPING_FILES`。file: `scripts/lumos:29370` 與 `scripts/lumos:26412`。
- 路徑常數寫成 `_TEST_DURATIONS_REL`,命名跟 `_ANCHOR_BASELINE_REL` 一致。
- 子指令掛法跟 `note-audit` 一樣:巢狀 subparser、`HELP_WHEN` 同時有父指令與子指令兩條,用 `--repo` 與 `_note_audit_root`,錯誤訊息以「擋下:」開頭並回 rc2 或 rc1。file: `scripts/lumos:48602`。
- 刷新用 `_write_lf` 原子寫入。file: `scripts/lumos:21235`。
- 執行器寫 run 檔,是照抄同檔 `.lumos/test-cache*.json` 的位置、條件、`.lumos-tmp` 暫存名加 `os.replace`。file: `scripts/test_lumos.py:39631`。

不對齊的是「秒數規則與路徑在兩支檔各寫一份、靠對照測試守一致」。
- 專案裡有「兩份加對照測試」的前例,但理由是交付包獨立。例如 `scripts/test_lumos.py:10903`,精簡版是獨立交付包,所以必須兩份。
- 這個執行器的慣例剛好相反。file: `scripts/test_lumos.py:31` 寫明「這個檔的慣例是 `_load_lumos_inproc()` 讀活的常數,不抄第二份」。file: `scripts/test_lumos.py:64221` 有測試專門守「執行器不抄白名單」。
- 執行器已經有載入 lumos 模組的機制。file: `scripts/test_lumos.py:230`。文件子集那條路徑本來就會載入。
- 計劃筆記沒有寫「不能載入 lumos」之類的理由。我 grep 計劃筆記找過,沒有。
- 所以第一條 finding 判 major。

**2. 命名與錯誤處理**

結構一致,只有一處命名差異,列為第二條 finding。
- 錯誤處理:執行器對壞表回 rc2,並寫「擋下:…修好或刪掉它」。刷新對舊表壞掉回 rc2、寫不進回 rc1,訊息都以「擋下:」開頭。這些跟 `anchor check` 的「擋下:基準線檔讀不到」寫法同型。file: `scripts/lumos:28390`。
- 暫存名:執行器用固定的 `.lumos-tmp`,比近年用 pid 加隨機的 `_write_lf` 舊。但這是照抄鄰居快取的寫法,各片寫的檔名不同,不會互搶,所以我不列為 finding。

**3. 第二種做法**

沒有另一套快取、原子寫入或資料檔位置。
- run 檔跟 test-cache 同在 `.lumos/`,`.gitignore` 也照 test-cache 加了一行。
- 刷新用既有的 `_write_lf`。
- 耗時表放既有的 `governance/`。
- 唯一的第二套是第一條 finding 的規則與讀表邏輯重複。

---

severity: major
blocking: 是
一、秒數合法性規則、表路徑、讀表驗證各寫了兩份,違反這個檔「讀活的常數、不抄第二份」的慣例。
引句:「跟 scripts/test_lumos.py 的 _duration_ok 同一條規則(刷新寫得出來的表,執行器一定讀得進)」
- 位置:`_duration_ok` 在 `scripts/lumos:48590` 與 `scripts/test_lumos.py:39090` 各一份,逐行相同。
- 路徑:`scripts/lumos:29370` 的 `_TEST_DURATIONS_REL` 與 `scripts/test_lumos.py:39085` 的 `_durations_table_path` 各寫一次字面路徑。
- 讀表驗證:`scripts/test_lumos.py:39102` 的 `_load_durations_table` 要求 tests 非空,`scripts/lumos:48602` 的刷新內聯另寫一套,不要求非空。同一張表有兩套讀法與兩種嚴格度。
- 失敗場景:有人改一邊的規則,例如放寬成接受字串或調整上限,而沒改另一邊。只有 `t_test_durations_refresh` 的探針清單守著,探針沒涵蓋到的輸入就漂移。
- 應該是:執行器像文件子集那樣用 `_load_lumos_inproc()._duration_ok` 和 `_TEST_DURATIONS_REL`,只留一份。依賴方向是執行器讀 lumos,與 `_DOCS_ONLY_PATHS` 同向,沒有新增跨層。
- 重現:`grep -n 'def _duration_ok' scripts/lumos scripts/test_lumos.py` 在固定版本印出兩處。`sed -n 64221p scripts/test_lumos.py` 是「執行器不抄白名單」的守衛測試,它只守白名單,守不到這份新複本。
- 歸因:未判定。這是新增程式碼本身的做法,跟修補無關。

severity: minor
blocking: 否
二、run 檔命名跟同位置的相鄰快取不同。
引句:「_dur = _cache_dir / (f"test-durations-run-{_args.shard.replace('/', 'of')}.json"」
- 相鄰的快取檔是 `test-cache-shard{i}of{n}.json`,見 `scripts/test_lumos.py:39632`,分片標記是 `shard1of4`。新檔是 `test-durations-run-1of4.json`,少了 `shard` 字樣,不分片時是 `test-durations-run.json`。
- 影響:`.lumos/` 底下兩種分片檔命名並存,後人要記兩套。不影響功能,glob 與 `.gitignore` 都對。
- 應該是 `test-durations-shard1of4.json` 之類同型的名字,或在註解裡說明為什麼不同。
- 歸因:未判定。

## 固定席節點

- `測試假綠形態.md` 的合約要求還原翻紅釘配前置斷言。新測試多處有「★前置★ 現場成立」,結構對齊,不影響本席判斷。
- `pitfalls-code-loop.md`、`guard-kill.md`、`lumos-cli-read.md`、`lumos-cli-lifecycle.md`、`design-loop.md`、`reversibility-governance-ledger.md`、`loop-convergence-recording.md` 這些節點:diff 沒碰它們的合約行為,不影響。
- `_BOOKKEEPING_FILES` 的改動不改它的單一源用法,不影響。

## 未驗範圍

沒有實跑 `lumos test-durations refresh` 與分片。本席只判一致性,不判正確性。

不對齊共 2 條,其中 major 1 條。
