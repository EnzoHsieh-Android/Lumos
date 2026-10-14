severity: minor

我在 `/tmp/lumos-seat-work/code-推送與CI提速-r3/邊界輸入-sonnet/` 的複本(修後 aea70018)與修前複本(22f6e132)裡實際造輸入跑過。找到兩條 minor,都不阻擋推送。沒有找到會讓分片漏跑或重複跑、或改壞耗時表的問題。

## findings

severity: minor
blocking: 否

**一、`scripts/lumos` 載不進來時,`--shard` 連吐兩段 traceback,rc=1,沒有說明。**

引句:「print(f"擋下:耗時表 {_durations_table_path()} 格式不對({_e});修好或刪掉它(刪掉就照名字輪流分)",」

- 輸入:複本裡只放 `scripts/test_lumos.py` 和一份合法耗時表,不放 `scripts/lumos`,跑 `--list --shard 1/4`。
- 實際結果:
  - `_load_durations_table` 載主程式時丟 `FileNotFoundError`,被 `except (OSError, ValueError)` 接住。
  - except 區塊的 f-string 又呼叫 `_durations_table_path()`,它內部再 `_load_lumos_inproc()`,第二次丟同一個例外,沒人接。
  - 結果是 "During handling of the above exception, another exception occurred" 加兩段 traceback,rc=1。
- 另一個輸入:`scripts/lumos` 有語法錯誤。丟的是 `SyntaxError`,不在 `(OSError, ValueError)` 裡,同樣是 traceback,而且也沒有「改成輪流分」的退路。
- 應該怎樣:這種情況給一行話說「主程式載入失敗」並 rc2。路徑要用不重新載入的方式算。
- 歸因:有證據的修復回歸。
- 兩版查證:
  - 修前 22f6e132 的 `test_lumos.py` 放在沒有 `lumos` 的目錄,`--list --shard 1/4` 是 rc0、512 支。
  - 修後同樣的目錄是 traceback、rc=1。
  - 原因是讀表規則搬進主程式後,純分片多了對 `scripts/lumos` 的依賴。
  - 實務衝擊低:`test_lumos.py` 本來幾乎每個測試都要載 `lumos`,CI 和來源 repo 一定有它。這個問題只在載入失敗那一刻的訊息和 rc 上看得出來。

severity: minor
blocking: 否

**二、刷新指令對特殊 run 檔的處理不完整,而且結尾的「刪掉 N 個」數字不實。**

引句:「print(f"✓ 耗時表更新:{_TEST_DURATIONS_REL}(原有 {before} 支 → 現在 {len(table)} 支;這次合進 {got} 筆,讀完刪掉 {len(runs) - kept} 個 run 檔)")」

- 輸入:`.lumos/` 裡放一個叫 `test-durations-run-dir.json` 的資料夾、一個斷掉的符號連結 `test-durations-run-dangle.json`,另外還有好壞各幾個 run 檔。
- 實際結果:
  - 輸出說「讀完刪掉 11 個 run 檔」。
  - 事後 `ls .lumos` 還留著資料夾和斷掉的連結。
  - 資料夾的 `unlink` 被 `except OSError: pass` 吞掉,卻照樣算進 `len(runs) - kept`。
  - 斷掉的連結在 `stamped` 階段 `stat` 失敗,根本不在 `runs` 裡,永遠留著。
  - 如果 `.lumos/` 只有斷掉的連結,訊息是「沒有測試執行器留下的實測秒數,先跑一次測試」,方向有點誤導。
- 同族的假綠:所有 run 檔都讀不懂時,指令印「✓ 耗時表更新…這次合進 0 筆」並 rc0。表的位元組沒變(sha 前後都是 19a95d9d),所以無害,只是訊息是綠的。
- 應該怎樣:刪除數實際計刪成功的;刪不掉或略過的列出來,或至少不算進去。
- 歸因:有證據的原有漏查。R3 只修了「排序時 `FileNotFoundError` 崩潰」,這個清理與計數的角落上輪沒人看。
- 兩版查證:修前遇斷掉的連結 rc=1 加 `FileNotFoundError` traceback。修後 rc0,但連結留著、計數照上述。

## 已驗、沒問題的邊界

**耗時表**(執行器 `--shard i/n --list`)

| 輸入 | 結果 |
|---|---|
| 資料夾、斷掉的符號連結、指向資料夾的符號連結 | rc2,「不是一般檔」 |
| 空檔 | rc2,「不是合法的 JSON」 |
| 不可讀(chmod 000) | rc2,「讀不進來」 |
| 超大整數(約 400 位) | rc2,拒收 |
| `inf` | rc2,拒收 |
| `tests` 為空、是 list、頂層是 list | rc2,拒收 |
| 巢狀一百萬層括號 | rc2,「不是合法的 JSON」,沒有崩潰也不慢(合法的九十萬層巢狀也是這個結果,訊息有點籠統) |
| BOM | 照常讀進,表雜湊與無 BOM 時一致 |
| 浮點中位數溢位成 `inf`(兩筆 1.7e308) | 四片仍是 513、512、512、512 支,聯集等於全部 |

**`--shard` 參數**

- `1/1` 全部測試都在這一片,配 `-k` 也正常。
- `0/4`、`1/0`、`a/b`、`1/`、`1/4/5`、五千位數:全部 rc2。
- `2000/100000000` 分到 1 支,rc0。
- 片數比測試多、不帶 `--suite` 時,空片是 rc1(符合 P3)。
- `--suite docs`、`--suite keys` 配分片時,空片是 rc0 並印「這片算過」。
- 純數字白話提示:`" 1 / 4 "` 這種帶空白的寫法也被接受,是 `int()` 的寬鬆,無害。

**聯集與支數**

- n 取 1、2、7、2049、2050、3000、10 的 9 次方,各片聯集都等於全部、不重複,且 `len(buckets) == min(n, 測試數)`。
- 空輸入回 `[]`。

**刷新指令**

- 舊表是資料夾、斷掉的符號連結、tests 為空、亂碼、不可讀:全部 rc2 且不覆蓋,訊息都指向「刪掉再刷」。
- 舊表不存在:只用這次的實測重建,rc0。
- run 檔是資料夾、指向資料夾的符號連結、空檔、BOM、超大整數、負數、布林、NaN、字串、list、一百一十萬層巢狀、不可讀:都略過或不收壞值。
  - BOM 的好值照收(`t_bom` = 3.0)。
  - 約 0.9 秒跑完,沒有崩潰。
- 舊命名 `test-durations-run-1of4.json` 與新命名 `test-durations-run-shard1of4.json` 混在一起:最新的檔案時間勝出(`t_old` = 1.1)。

## 三問

**一、原問題的修復效果(同一案例的證據)**

| 案例 | 修前 | 修後 |
|---|---|---|
| R1:`--shard 1/100000000 --list` | 28.06 秒、7.5GB | 2.57 秒、0.5GB |
| R2:耗時表是資料夾,`--shard 2/3` | 當成沒有表、照名字輪流分,rc0 | rc2「不是一般檔」 |
| R3:run 檔是斷掉的符號連結 | `FileNotFoundError`,rc=1 | 略過、其他照合 |

- R4、R5、R6 的翻紅是測試層的主張,不在我的邊界與輸入鏡頭範圍內,**未驗**。
- 修後的 R1 約 0.5GB,看來是載入 `lumos` 的基線;我沒有另外量證實。

**二、修補處的正常、錯誤與相鄰路徑**

- P1:合法表下四片聯集等於全部,同一表雜湊 19a95d9d,成立。
- P2:沒有表時,修前與修後都是「照名字輪流分」,每片 683 支,成立。
- P3:空片兩版都是 rc1,成立。
- P4:BOM 舊表加好壞 run 檔,兩版輸出一字不差(舊值保留、好的合進),成立。
- P5:一片跑的期間表被換掉會 rc2。這條要實際跑完一片才能驗,**未驗**。
- 相鄰路徑出現新增依賴,即上面第一條。

**三、新發現的修前、修後對照**

- 第一條:修前 rc0,修後 rc1 加 traceback。
- 第二條:修前 `FileNotFoundError` rc1,修後 rc0 但留檔、計數不實。

## 節點判讀

- `測試假綠形態.md`:不影響。這次沒有新增「還原翻紅釘」,也沒有動它所綁的測試;我造的輸入都是真跑,不是只看測試通過。
- `lumos-cli-read.md`、`guard-kill.md`、`lumos-cli-lifecycle.md`、`design-loop.md`:不影響。它們的 INVARIANT 分別管 search 的排除規則、guard kill 的 rc 與 JSON、re-inject 的位元組保留、處置閘第五步。我讀到的改動沒有碰到,而且我造的輸入都在耗時分片與刷新路徑上。
- `pitfalls-code-loop.md`、`reversibility-governance-ledger.md`、`loop-convergence-recording.md`:不影響。它們是 RISK 節點,我讀到的改動沒有影響。
- 超出上限、只列名的節點:未逐篇判。

未驗範圍:CI 上真實跑(`ci.yml` 的 concurrency、子殼層 `exit $rc`)、全套測試實跑、`--ff` 與 `--seed` 配分片、併發中換表(P5)。

最嚴重等級 minor;blocking 共 0 條。
