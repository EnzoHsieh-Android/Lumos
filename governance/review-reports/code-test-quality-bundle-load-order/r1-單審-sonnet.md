severity: major

**ID: LO-1**
severity: major
blocking: true
引句:「        stray = _test_quality_bundle_unverified_refs(loaded)」
file: `scripts/lumos:49497`
第二道守衛「載入後核對引用」完全沒有測試守著。把這一行改成 `stray = None` 後,四支新測試加上既有測試都不會紅。
- 最小重現:在 `scripts/` 的複本把該行換成 `stray = None`,然後跑 `python3.14 test_test_quality_cli.py QualityCLI.test_semgrep_adapter_uses_verified_runner_not_stale_bytecode QualityCLI.test_fifo_sidecar_does_not_hang_other_commands QualityCLI.test_incomplete_bundle_short_help_is_structured QualityCLI.test_sidecar_runtime_error_only_blocks_test_quality`。結果是 4 個全綠(我的實驗 M2)。
- repo 內只有 `scripts/lumos` 有 `unverified_refs` 與 `_TEST_QUALITY_LOAD_ORDER` 這兩個字串,沒有任何測試直接打它們。
- 順序守衛本身是有牙的。把排序拿掉但保留核對時,該測試會紅(M1)。兩道都拿掉時,測試丟 ZeroDivisionError 紅(M3)。
- 唯一會讓核對函式真正起作用的情境是「順序錯」。該測試只在順序錯而核對在時紅,沒有一支測試單獨證明核對的判斷式能逮到舊副本。
- 圖譜 PITFALL 寫「兩道各自擋得住」,第二道這一半缺實跑紅綠證據,與 `skills/lumos-project-notes/commands/test-quality-standard.md` 對關鍵守衛的要求(實跑紅綠、翻紅後還原)不符。
- 建議補一支測試:用順序錯的複本(或直接餵函式一個舊副本物件),斷言回部署不完整。

**ID: LO-2**
severity: minor
blocking: false
引句:「                if getattr(modules[owner], getattr(value, "__name__", attr), None) is not value:」
file: `scripts/lumos:49459`
這個判斷式拿 `value.__name__` 去配套模組裡找同名成員,遇到合法引用會誤報成「未驗來源」。我用函式本體抽出來實跑,A 是被依賴模組,B 是引用方:
- `from A import wrapped`,其中 `wrapped` 是 `@functools.wraps(real)` 的包裝。包裝繼承了 `__name__ == 'real'`,所以回 `B.wrapped 不是已驗的 A`。
- `from A import main`,其中 `main = _make(1)` 是工廠產出的閉包,`__name__` 是 `inner`。回 `B.main 不是已驗的 A`。
- `from A import DEFAULT as d2`,`DEFAULT` 是類別實例,沒有 `__name__`,退回用別名 `d2` 去 A 找。回 `B.d2 不是已驗的 A`。
- 以下都回 None,沒誤報:`from A import real as rc`(函式別名,`__name__` 對得上)、數值或字串常數、類別別名、同名實例。
- 目前三支配套沒有這幾種寫法,所以現在不會紅。
- 後果是日後任一支配套新增這類 import,`test-quality` 會永遠回「未完整部署」,訊息指向 `lumos update` 修不了的原因。失敗是響亮的,不會靜默。
- 建議用 `is` 比對時,先拿 `value` 自己在 owner 模組 `vars` 裡反查(`any(v is value for v in vars(modules[owner]).values())`),不要靠 `__name__`。

**ID: LO-3**
severity: minor
blocking: false
引句:「            if owner in modules and owner != name:」
file: `scripts/lumos:49458`
核對只看有 `__module__` 的物件,以下兩類從未驗副本取得的引用會漏報:
- 引用模組本身:`import A as t` 的 `t` 是模組物件,沒有 `__module__`。實跑 `import A` 與 `import A as t` 都回 None。
- 數字與字串常數:沒有 `__module__`,同樣漏掉。
- 具體路徑:若某支配套日後寫 `import test_quality as tq`,又碰上載入順序錯,標準 import 會把舊副本綁進 `tq`。之後 `sys.modules['test_quality']` 被換成新版,核對卻看不到 `tq`,舊 bytecode 照跑。
- 這要「寫法改變」加「順序錯」兩件事同時發生才會成真,所以只標 minor。
- 圖譜 PITFALL 與程式註解宣稱「逐一核對引用的配套物件都是已驗那份」,範圍寫得比實作大。
- 至少要把這個限制寫成回頭條件,或加掃 `ModuleType` 值的規則。

**已讀,無 finding 的部分**
- 鏡頭 2,例外全接:
  - `except Exception` 不吞 KeyboardInterrupt。SystemExit 只有在已通過指紋的 bytes 自己呼叫 `sys.exit` 時才會穿出,且不回復 `sys.modules`;這需要出貨的配套被刻意改過,所以不標。
  - 部分載入後的回復邏輯正確,`previous` 在載入前就記好,三個名字都會還原。M6(還原成舊的例外元組)時,`test_sidecar_runtime_error_only_blocks_test_quality` 會紅。
- 鏡頭 3,`stat()` 與符號連結:
  - 指向一般檔的符號連結:通過,`test-quality capabilities` rc 0。內容仍經 `open` 讀同一份 bytes 並驗指紋,沒有不一致。
  - 指向 FIFO 的符號連結:回「配套檔不是一般檔案」,`--version` 不卡。
  - `stat` 與 `open` 之間若被換成 FIFO,最壞是卡住,而且要有 `scripts/` 寫入權,同權限本來就能改 `lumos`,無實質影響。
- 鏡頭 4,測試品質(LO-1 以外):
  - 前置斷言都在:舊 cache 存在、`S_ISFIFO`、broken 檔指紋被替換(替換沒套上時,reason 不含 sidecar 訊息會紅)。
  - 對測試的 mutation:
    - 拿掉 `S_ISREG` 檢查:FIFO 測試 `--version` 逾時紅(M4)。
    - 還原 `-h`:短 help 測試紅(M5)。
    - 還原例外元組:RuntimeError 測試紅(M6)。
    - 順序與核對兩者併拿:stale cache 測試紅(M3)。
  - 第四支測試用 `replace(b"\r\n", b"\n")` 重算指紋,與 `_vendored_digest`(`scripts/lumos:22361`)內部規則重疊,但只是替換固定檔案,不影響判準,不標。
  - stale cache 測試在 `PYTHONDONTWRITEBYTECODE=1` 下會在前置斷言紅(「stale runner cache must exist」)。既有測試 `scripts/test_test_quality_cli.py:776` 有同樣前置斷言,屬沿用慣例,響亮失敗,不標。
- 鏡頭 5,既有行為:
  - 完整配套下整檔 `python3.14 scripts/test_test_quality_cli.py` 跑完 52 個測試全綠。
  - 佔位入口的 `test-quality -h`、`test-quality scan -h`、`--vault /tmp/x test-quality -h` 都回結構化 JSON 且 rc 2。
  - 移除的 `ModuleNotFoundError` 分支確實走不到:配套已在 `sys.modules`,缺檔會先在載入階段回結構化錯誤。
  - 排序用 `_TEST_QUALITY_LOAD_ORDER.index`;日後新增指紋項卻忘了更新順序表,會讓 `test-quality` 永遠回「未完整部署」,但完整配套測試會抓到,不標。

總結最嚴重 severity: major;blocking: 1
