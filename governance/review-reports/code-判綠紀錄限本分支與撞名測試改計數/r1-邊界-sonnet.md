severity: major

我替極端輸入逐 hunk 走過。這份 diff 在邊界上大致站得住:三引號樣式、可用性不足時的保留方向、同名重開分支都過了。但有兩處測試抓不住它宣稱要擋的錯(下面 1、2),還有一處分支名比對對改名與同名 tag 太敏感(3)。我在 `/tmp` 的副本上對原始碼注入改壞,跑相關測試,看哪些會翻紅。

1. `t_name_collision_scales` 的「每種串接最多 1 次」抓不到「串接每次重算」,只抓得到「串接完全不存」。
severity: major
blocking: 是
引句:「應抓到的錯:每個名字重建索引、或串接不快取每次重做 → 次數紅。」
- 起因在測試夾具的計數方式。`Counting._join` 只在 `(kind, fold) not in self._joined` 時才記一次。
- 把真正的 `_TitleIndex._join` 改成 `if True:`(每次都重算,但仍寫入 `self._joined[key]`),第二次起夾具看到 key 已存在就不記數,`len(joined) == len(set(joined))` 恆成立。
- 最小重現:複製 `scripts/` 後把 `_join` 內的 `if key not in self._joined:` 改成 `if True:`,執行 `python3.14 scripts/test_lumos.py -k t_name_collision_scales`。四條斷言全綠、耗時 9.2s,正常是 0.29s,且遠低於 60 秒安全網。
- 結果:驗收條款 S3 的後半「每種串接最多一次」,以及測試說明寫的「串接不快取每次重做 → 次數紅」都不成立。
- 佐證:`scripts/lumos:68879` 的 `_join` 與 `scripts/test_lumos.py` 新版 `Counting._join`。

2. 淺複製裡「rc 1 → 保留」那條路沒有任何測試。
severity: major
blocking: 是
引句:「verdict[sha] = None if is_shallow() else False」
- 這是計劃做法 c 與驗收條款 S8 寫明的「淺複製的歷史被截掉,rc 1 不可信」。
- 改壞再跑:把這行改成 `verdict[sha] = False`,跑 `-k t_redbase_branch_rows` 與 `-k t_spec_gate_redbase_green`,兩組合計 19 條全綠。
- `t_redbase_branch_rows_fallback_keeps` 的淺複製案例用不存在的 `"cd"*20`,只會走 rc 128 → `cat-file` 那一支。
- 這條路真的走得到:先 `git clone --depth 1`,再 `git fetch --depth 1 origin <較舊提交>`,此時 `merge-base --is-ancestor <舊> HEAD` 回 rc=1、`--is-shallow-repository` 為 true。
- 我拿這個 clone 呼叫真函式。原版保留該筆並印出「1 筆…照舊算進來」,改壞版丟掉(回 0 筆)。
- 結果:有人把這行簡化掉,過濾會在淺複製裡丟掉真正的祖先紀錄,而所有新測試都不會紅。
- 佐證:`scripts/lumos:14440` 附近的 `_redbase_on_branch`。

3. 分支名比對對「同名 tag」與「分支改名」敏感,舊判綠紀錄被丟,之後判紅會多存一份實作後的紅燈版。
severity: minor
blocking: 否
引句:「br = _lens_git(rr, "symbolic-ref", "--short", "-q", "HEAD")」
- `symbolic-ref --short` 在同名 tag 存在時回 `heads/feat`(git 2.39.2 實測)。
- 重現:分支 `feat` 上判綠,寫入 `ref="feat"`;之後 `git tag feat`,`_redbase_branch_name` 變成 `heads/feat`,`_redbase_on_branch` 對該筆回 0 筆。`git branch -m feat feat2` 同樣被丟(回 0 筆)。
- 後果等同計劃「天花板一」那一方向:判綠不算,多存一份實作後的紅燈版。
- 天花板一只寫了壓提交與 rebase,沒寫 tag 同名與改名。

三引號樣式、不做檔案寫入的路徑與 CI 夾具這幾項沒找到會出錯的地方:
- `_TG_CONST_PAT` 三引號段:空三引號、含單個雙引號、跨行、含 `${}` 都判對。1MB 長字串、1MB 單引號交錯、1MB 未收尾字串都在 0.05 秒內,沒有回溯爆量。
- 結尾四個以上引號(`"""a""""`)不被當常值,但出錯在更前面的 `_tg_call_parts` 切參數(第二參數被切出多餘的 `)`)。這是改動前就有的行為,不歸這份 diff,所以不標。
- `_redbase_attach` 先問 `_gov_ledger_ignored` 再寫:`st` 只在 `caps` 非空時才問,其餘路徑行為不變。
- 夾具在 CI 上的風險:
  - 預設分支名用 `symbolic-ref` 取得,不寫死 `main`。
  - 額外提交都帶 `--no-verify` 與 `-c user.*`。
  - 淺複製目錄在 `mkvault().parent.parent` 底下的新暫存目錄裡,不會殘留到下次執行。
  - `git clone --depth 1 --no-local` 在 Linux 沒有 file transport 限制。
  - 本機慢案例 `t_spec_gate_redbase_green_other_branch` 16.4s,上限 180s,餘裕 11 倍。
- 我另外改壞了五處並重跑測試:拿掉祖先丟棄、拿掉分支名過濾、`cat-file` 後備改成一律保留、拿掉 `_TG_CONST_PAT` 的三引號段(寫入端的 ref 欄位沒改)。這四處都有測試翻紅,涵蓋足夠。
- 改壞 rc 1 路徑(上面第 2 點)是唯一翻不紅的過濾分支。

固定席筆記逐條判定:
- `Systems/lumos-cli-read.md`(search 排除 superseded 不排除 stale):不影響。diff 只動規格閘、比對工具與一支測試,沒碰 search 的濾網。
- `Systems/測試假綠形態.md`(還原翻紅釘要有前置斷言證明現場成立):未破壞。新測試多半有 ★前置★ 或前面斷言證明現場;`t_spec_gate_redbase_green_other_branch` 的 S6 同名重開案例沒有明寫前置,但我拿掉祖先過濾後它翻紅,現場確實走到。只有上面第 1 點是「現場走到、但那條斷言抓不到改壞」。
- `Systems/loop-convergence-recording.md`、`pitfalls-code-loop.md`、`reversibility-governance-ledger.md`(★RISK★,牽連 `scripts/lumos`):不影響。diff 沒改審查帳寫入、迴圈收斂與可逆性的程式,只在治理帳兩種事件多記 `ref`。我 grep 過 `ref` 的讀取端,沒有消費者會把規格閘事件誤讀成留痕。
- `Systems/design-loop.md`(處置閘第五步,設計審材必須是 `.md` 計劃、有 [SN] 時條款要 [綁定測試:有]):不影響。本迴圈是 code- 開頭,審材是 patch。計劃自己的 S1 到 S9 條款都有 [test:] 綁定。
- `Systems/guard-kill.md`(rc 優先序、`--json` 純淨):不影響。`_name_collision_reason` 的行為沒改,只有測試改成數次數。
- `Systems/bound-tests-gate.md`(合約綁的測試逐支真跑):不影響程式行為。但新綁定測試 `t_name_collision_scales` 有第 1 點的缺口。

最嚴重等級是 major,blocking 共 2 條(第 1、第 2 點)。
