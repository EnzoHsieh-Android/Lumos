severity: minor

這份改動沒有 blocker 或 major。修補驗收的三個正向主張都有證據,有 3 條 minor 候選(其中 2 條有重現,1 條只做了程式碼閱讀)。

## 修補驗收(三問)

1. **原問題的修復效果**
   - 問題:份數打成 1/100000000 時,分片照份數配置而吃光記憶體。
   - 輸入與預期:在固定版本 aea70018 的 `archive` 副本,帶耗時表,執行 `--shard 1/100000000 --list`。預期立刻回來,只分到一支。
   - 修後結果:印出「分法:耗時表 19a95d9d,共 2049 支,這份分到 1 支」,只列一支測試。`--shard 2/100000000 --list` 也回得來,rc=0。
   - 修前結果:未驗,我只讀了修補差異的程式碼。
   - 原因:程式碼 `live = min(n, len(names))` 把配置量限在測試數以內。
   - 另外,執行器自己的讀表規則已收進主程式的 `_read_durations_table`,這條有程式碼閱讀為證。
2. **修補處的正常、錯誤與相鄰路徑**
   - 讀表、分片、結尾再讀一次比對雜湊、`test-durations refresh` 的錯誤路徑,我逐行讀過,沒找到會出錯的行為。
   - 這些路徑包括:超大整數、巢狀過深、BOM、資料夾當表、tests 形狀不對、讀完才被改寫的 run 檔、列出後才消失的 run 檔。
   - 我沒有逐一翻紅,這部分只是閱讀判斷。
3. **新發現在修前、修後的結果**
   - 下面三條都是修補前後沒變的原有漏查。
   - 兩版都沒有針對這三條的守衛或測試,所以我沒另外跑修前版。修補差異沒有動到這些行(只讀差異判斷)。

## 找到的問題

severity: minor
blocking: 否

**1. 執行器寫 run 檔的固定暫存檔名會跟著符號連結寫到別處(⚠ 威脅模型下很弱)**
- 輸入與走到哪裡:`.lumos/test-durations-run.json.lumos-tmp` 被放成指向別檔的符號連結。執行器收尾的 `_tmpd.write_text(...)` 會寫進連結目標,再用 `replace` 換名。
- 重現:在 `archive` 副本放上那個符號連結,執行 `python3.14 scripts/test_lumos.py -k no_zero_assertion_return_paths`。結果 `victim.txt` 的內容被改成 `{"tests": {"t_no_zero_assertion_return_paths": 8.298}, "version": 1}`。
- 應該是:refresh 端已在 r1 資安席後改成不跟符號連結寫(`t_test_durations_refresh` 有測),寫 run 檔這一側是同一族卻漏掉。要嘛用 `_write_lf`(唯一暫存名),要嘛先 `unlink` 暫存檔。
- 註記:同一段的 `test-cache.json.lumos-tmp` 是原本就有的同形狀。
- 歸因:有證據的原有漏查。
- 查證命令:`git -C <repo> show aea70018:scripts/test_lumos.py` 的 `_tmpd = _dur.with_suffix(...)` 一段,加上上面的重現。

引句:「_tmpd = _dur.with_suffix(_dur.suffix + ".lumos-tmp")」

**2. 無分片的 run 檔每次直接蓋掉,小範圍的 `-k` 子集跑會洗掉先前全套的實測(有重現)**
- 輸入:先跑一次全套(不帶 `--shard`,寫出 `test-durations-run.json`,約 2000 支),再跑 `-k stop_block` 之類的子集。
- 結果:子集的收尾以 `os.replace` 整檔覆蓋,同名檔只剩子集的幾支。之後 `lumos test-durations refresh` 只能合進那幾支,全套的實測沒有進耗時表。
- 應該是:無分片的檔名帶上範圍(例如有 `-k` 或 `--suite` 時另用檔名),或寫入前先合併既有內容。
- 代價:耗時表長期靠人手補,CI 各份不平均的問題照舊。
- 歸因:有證據的原有漏查,這段是新增的,修補沒動。
- 查證:同一份 `archive` 副本,看 `_DURATIONS` 寫檔段。

引句:「"test-durations-run.json")」

**3. 紅的、環境壞掉的或逾時的一輪也會原樣進耗時表(⚠ 程式碼閱讀,未重現)**
- 情境:本機環境壞掉,多支測試瞬間丟例外或秒紅。這時 `_DURATIONS` 記下接近 0 的秒數,refresh 不分辨,把最慢的幾支改成接近 0。
- 逾時那支記的是上限(例如 180 秒),不是實測。
- 後果:這份表一提交,CI 的 16 份會因權重變成 0.05 秒下限而不平均,最慢那台又拖回 12 分以上。
- 計劃明寫「過、紅、逾時、例外都記」,所以是設計取捨,不是實作錯。
- 應該是:`refresh` 或執行器至少略過該輪失敗數大於 0 的 run 檔,或把紅的測試排除。
- 歸因:未判定。

引句:「_DURATIONS[t.__name__] = round(_time_slow.time() - _dur_start, 3)」

## 固定席節點逐條判

- **測試假綠形態 ★INVARIANT★(還原翻紅釘要配前置斷言證明現場成立):** 不影響合約本身。新測試都有 `★前置★ 現場成立` 斷言:檔名順序與時間順序相反、`ci.yml` 找得到分片行、箱內測試真的寫出耗時表等。這次改動沒有削弱前置斷言。
- **lumos-cli-read 的 search 排除規則(★INVARIANT★):** 不影響,改動沒碰 search。
- **guard-kill 的 rc 優先序與 `--json` 純淨(★INVARIANT★):** 不影響,改動沒碰 guard kill。
- **lumos-cli-lifecycle 的 re-inject 只覆蓋 sentinel 之間內容(★INVARIANT★):** 不影響,沒有碰注入邏輯。
- **design-loop 處置閘第五步(★INVARIANT★):** 不影響。
- **pitfalls-code-loop、reversibility-governance-ledger、loop-convergence-recording(★RISK★):** 不影響執行路徑。
  - `_BOOKKEEPING_FILES` 多收了耗時表,代價是只改這張表的推送不需要新的代碼審留痕。
  - 這是計劃明載的取捨,但上面第 3 條提到表的內容未經任何審查就能影響 CI 分片平衡。
- **bound-tests-gate、arch-alignment-lens 等「超出上限,只列名」的節點:** 都只列名,我沒有逐條判。其中 bound-tests-gate 是這次改動的家,新增的 WHY/PITFALL 行格式和 `[test:]` 指到的測試名都存在。
- **未判:** 其餘只列名的節點沒有判。

## 慣例對照

- **CLAUDE.md 逐條對照:** 我看了(使用者層、repo 根)一遍,沒有找到能逐字引出規則又指得出違反那一行的情況。
- **未驗範圍:**
  - 沒跑全套測試或 CI。
  - 沒在 r2 前的版本重現修補前的行為。
  - ci.yml 的 `concurrency` 實際在 GitHub 上的取消行為只讀了設定。

最嚴重等級:minor;blocking 共 0 條。
