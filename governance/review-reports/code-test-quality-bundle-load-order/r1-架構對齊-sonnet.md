severity: minor

這份 diff 在結構上跟專案既有做法對得上。分層沒有跨層呼叫,也沒有引入另一套「核對模組來源」的機制。我找到三條寫法上的不一致,都是 minor,都不擋。

## 問 1:分層與依賴方向

三個新東西(`_TEST_QUALITY_LOAD_ORDER`、`_test_quality_bundle_unverified_refs`、`_test_quality_bundle_sources` 裡的一般檔檢查)都留在原本的配套載入區塊,依賴方向沒變。

- 新 helper 只被 `_test_quality_load_bundle` 呼叫,不碰 vault 或圖譜層。
- 比照 `_vendored_digest`(`scripts/lumos:22361`)的用法:指紋照舊走同一支函式,沒有另算。
- `_TEST_QUALITY_BUNDLE_DIGESTS` 照舊跟 `_VENDORED_TOOLKIT`(`scripts/lumos:22331`)對齊,對齊檢查還在。
- 移除 `ModuleNotFoundError` 死分支,讓 `main` 只走「已登記或結構化錯誤」兩條路,跟 `test-quality` 子命令一貫「部署不完整就回結構化 JSON」的路徑一致。
- `import stat as _stat` 寫在函式內,跟 `scripts/lumos:1384` 與 `scripts/lumos:13769` 的既有寫法一樣。

**LOA-1**
severity: minor
blocking: false
引句:「if not _stat.S_ISREG((folder / name).stat().st_mode):   # FIFO/裝置檔讀了會卡住每個指令」
file: `scripts/lumos:49473`
專案已有「擋 FIFO」的慣用做法:`_regular_own_fd`(`scripts/lumos:1376`)先用 O_NONBLOCK 開檔,再用 `fstat` 判一般檔。這次改成「`stat()` 判斷,之後才 `open("rb")`」,是同一件事的第二種寫法。它先看後開,中間檔案可被換成 FIFO。`stat()` 也會跟隨捷徑,沒有 O_NOFOLLOW。結構上沒有新機制,所以只算 minor。

## 問 2:命名與錯誤處理

- `except Exception as exc:   # 配套任何錯誤都只讓 test-quality 回部署不完整,不拖垮其他指令`(`scripts/lumos:49500`)符合專案慣例。
  - `scripts/lumos` 裡約 245 處 `except Exception`,多數帶一句理由註解。
  - 同類的「載入別人的檔、炸了轉成一句原因」是 `_handoff_load_hook` 的 `except Exception as e:   # 匯入是別人的檔,什麼都可能炸`(`scripts/lumos:48916` 起),走法一致。
- 對照 python-idioms R6:`except Exception` 接不到 BaseException,不吞取消,符合條款。
  - 這個接法會被 `ruff:BLE001`(接太寬)標記;專案已有帶註解的前例,所以不算偏離。
  - ⚠ 註解寫的是「任何錯誤」。專案另有 `★fail-open 鐵則:本 try 內禁止 sys.exit/SystemExit(except Exception 攔不到)★` 的說法(例如 `scripts/lumos:14428`)。配套檔頂層若 `sys.exit`,仍會逃出這個 `except`。這是註解措辭問題,不列為不對齊。
- `ValueError` 加中文訊息、命名 `_test_quality_*`,都跟同區塊既有函式一致。

**LOA-2** ⚠
severity: minor
blocking: false
引句:「_TEST_QUALITY_LOAD_ORDER = ("test_quality.py", "test_quality_semgrep.py", "test_quality_scan.py")」
file: `scripts/lumos:49464`
載入順序另開一張平行表,跟 `_TEST_QUALITY_BUNDLE_DIGESTS` 要手動同步。既有那張表旁邊有 `if required != set(_TEST_QUALITY_BUNDLE_DIGESTS): raise ValueError("配套指紋清單未對齊")`(`scripts/lumos:49469` 附近)。新表只靠 `LOAD_ORDER.index` 在缺名時隱性拋 `ValueError`。如果 `LOAD_ORDER` 多出名字,沒有任何檢查會發現。專案對「兩張要同步的表」一向配對齊守衛,這裡少了一道。我不確定專案是否有特別允許這類表不加守衛,所以標 ⚠。

## 問 3:有沒有引入第二種做法

- `_test_quality_bundle_unverified_refs` 靠 `__module__` 和模組物件身分比對來核對引用來源。我在 `scripts/lumos` 搜尋 `__module__`、`sys.modules[`、`exec(compile`、`spec_from_file_location`,沒有找到另一套相同目的的機制。`_handoff_load_hook` 只做 `exec_module` 加 callable 檢查,不核對來源。所以這是補第一套,不是第二套。
- 唯一的第二種做法就是 LOA-1 的「檔案類型判斷」。
- 測試側風格一致:用 `copied_bundle`、`subprocess.run([... target/"lumos" ...])`、`assertEqual` 判 returncode 並解析 stdout JSON,檔頂的 `import re` 與 `import stat` 跟檔內其他 import 同層。

**LOA-3**
severity: minor
blocking: false
引句:「self.assertTrue(cache.exists(), "stale runner cache must exist before restoration")」
file: `scripts/test_test_quality_cli.py:762`
`test_semgrep_adapter_uses_verified_runner_not_stale_bytecode` 把既有 `test_source_bytes_not_stale_bytecode_authorize_capture`(第 762 行起)整段「造舊 bytecode → 還原原始碼 → 用 `os.utime` 還原時間戳」又抄了一份,沒有抽成 helper。寫法一致,但同一套手法在檔內現在有兩份。

不對齊共 3 條,其中 major 0 條
總結最嚴重 severity: minor；blocking: 0
