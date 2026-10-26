severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/769b2e46…738bb93b.json.warming` 不存在(ls 與 cat 都回找不到),沒有鎖要處理,也沒刪任何鎖。

## F1 同一情境的清單內重複項目不會去重,會多跑並讓記憶體收集自己撞牆
severity: minor
blocking: 否
file: `scripts/lumos:41040` 附近的 `_e2e_select`(迴圈尾端那行 `sel[k] += [...]`)
失敗場景:
- 設定檔:某情境列 `"macrobench": ["B#m","B#m"]`、`"stability": ["s1","s1"]`、`"flows": ["f.yaml","./f.yaml"]`。設定檢查 `_e2e_cfg_err` 回 None,放行。
- 跑 `--case fa.c` 時,去重集合是迴圈進來時算一次,所以只去掉「跨情境」重複,同一份清單內的重複照單全收。
- 我呼叫 `_e2e_select` 的結果是 `flows ['f.yaml','./f.yaml']`、`macrobench ['B#m','B#m']`、`stability ['s1','s1']`、`visual ['home_visual','home_visual']`。
- 浪費:同一個效能方法跑兩次 Gradle,每次上限 3600 秒,Maestro flow 也跑兩次。
- 記憶體:第二次收集用同一個 `<run-id>.s1`,收集腳本 `scripts/templates/android-stability-collect.sh:391` 看到 `stability.json` 已存在就 `die`,回 2。我只讀了程式,沒跑到判讀層,所以判成沒過或沒判完這一步沒實測。
- 「同一方法列在多個情境」這條路徑是對的:跨情境有去重。
歸因:有證據的原有漏查。同一個探針在修前 9e21d491 與修後 787dd51b 兩份 `scripts/lumos` 都得到一樣的重複清單。
引句:「sel[k] += [x for x in c.get(k, []) if norm(x) not in {norm(y) for y in sel[k]}]」

## F2 --changed 的 git 逾時或失敗被靜默當成沒有改動,提交過的改動會被漏掉
severity: minor
blocking: 否
file: `scripts/lumos:40820` 附近的 `_e2e_changed_files`
失敗場景:
- `_nodehome_git` 預設 20 秒逾時,逾時或失敗回 None,這裡接 `or b""`,說明欄 `note` 仍是空字串。
- 同樣的靜默吞掉也出現在 `ls-files --others` 與 `_dirty_non_bookkeeping(root) or []`。
- 重現:臨時 repo 的 main 與 feat 兩條分支,`app/a.kt` 已提交改動,`app/b.kt` 只是髒的。
- 正常時 `_e2e_changed_features` 回 `['fa','fb']`。把 `diff --name-only` 換成回 None(等同逾時)後回 `['fb']`,`note=''`、`err=None`。
- 結果:使用者看不到任何提示,只跑 fb,漏掉已提交的 fa。
歸因:有證據的原有漏查。修前與修後兩版同一個探針,結果一樣(正常 fa+fb,逾時只剩 fb)。
引句:「raw = _nodehome_git(root, "diff", "--name-only", "-z", "--no-renames", base, head) or b""」

## F3 整套跑現在對每個 stability_scenarios 各收一次,磁碟與時間倍增,舊檔沒有清理規則
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh` 的 `stab_to_run`,以及 `scripts/templates/android-stability-collect.sh:134-150` 的 `prune_old_snapshots`
失敗場景:
- 修前 `stab_to_run` 整套跑只回 `[None]`,修後回 `[None, *stability_scenarios]`。
- 我跑了 `python3.14 scripts/test_lumos.py -k android_e2e_memory_by_case`,7 項全過,其中一項確認整套跑會叫收集腳本 3 次(`run-full`、`run-full.player`、`run-full.cart`)。
- 每個情境各佔一個 `<run-id>.<情境>` 目錄。錄製設定檔 `android-stability-record.pbtxt` 的緩衝是 64MB+8MB,所以每個情境的 `cycle.pftrace` 上限約 72MB。
- `prune_old_snapshots` 只刪超過 7 天的 `heap-*.pftrace`,`cycle.pftrace`、`logcat.txt` 不清,計劃第 115 行寫明由人清。
- 時間上限:每個情境最多 3600 秒,整套跑最壞是 (1+K)×3600 秒再加上每個效能方法各 3600 秒,沒有總上限,只有每步上限。
- 未能量:真實的快照大小與情境數沒有數字,所以只能列為累積風險,不能算出具體 GB。
歸因:有證據的修復回歸(修補引入 `[None, *scen]`)。這是修補刻意要的行為,倍增是它的代價。
引句:「return SEL["stability"] if SEL is not None else [None, *(cfg.get("stability_scenarios") or {})]」

## 已驗的正向主張(同案例修前修後)
- **總表 history 讀取不會隨行數爆量**:合成 50000 行、約 92MB 的 `history.jsonl`,`history --last 5` 在 787dd51b 耗時 1.7 秒、在 9e21d491 耗時 1.86 秒,rc 都是 0。`_canary_ledger_rows` 是逐塊串流,用 `with` 開檔。腳本空轉基準本身就約 338MB,所以不是這條路徑的增量。
- **總表追加不留 handle,也不會寫半行**:`_local_ledger_append` 用 `os.open`、單次 `os.write` 並核對長度,`finally` 關閉;追加前 `_ledger_tail_needs_newline` 補換行。
- **範本腳本的子程序都收得乾淨**:
  - `run()` 每個子程序自成程序群組,逾時或中斷都 `kill_group`,檔案在 `finally` 關閉。
  - 新增的 `select()` 與 `Steps.__init__` 的 `--precheck` 都走 `run()`,預設 120 秒,中斷時整組收掉,不留孤兒。
  - 沒做 PID 層的實測,這是讀程式的結論。
- **效能方法跨情境去重正常**:`dict.fromkeys` 與 `_e2e_select` 的集合去重,跨情境同一方法只跑一次(F1 只是同一份清單內的漏洞)。
- **每個方法收結果到各自子目錄**:`collect_results(..., mdir/i)` 把每個方法的結果收進 `mdir/<i>`,`macrobench` 判定用 `rglob` 往下層找,一致。

未驗範圍:真機上的 adb 與 perfetto 行為,以及 Gradle daemon 在逾時後是否殘留(舊行為,與修補無關)。

## 三問
1. **原問題修復效果**:我只查資源面。效能每方法一次與去重已驗(跨情境正常,F1 是同清單內漏洞)。記憶體每情境一次已由測試佐證(F3)。
2. **修補處的正常、錯誤與相鄰路徑**:history 讀取、總表追加、子程序收尾的正常與錯誤路徑都仍成立(見上)。F1 和 F2 在修前就存在。
3. **新發現的同一案例修前修後**:F1 與 F2 兩版結果相同,F3 是修補造成。

## pitfalls manifest
唯一一題是「`scripts/lumos` 寫總表那段的 open( 有沒有 with 或確定 close」。判定是誤報。
- 總表追加走 `_local_ledger_append`,用 `os.open` 加 `finally: os.close`,沒有裸 `open(`。
- 讀取側 `Path(path).open("rb")` 在 `with` 內。
- 範本腳本的 `run()` 在 `finally` 關檔,`Steps.save` 用 `with`。

## 圖譜鏡頭
hook 這次沒附固定席節點,屬「圖譜沒有釘到節點」的備援段,不逐條答。我沒看到這份 diff 破壞任何已知合約,但也沒有可對照的固定席清單。

這一輪資源面沒有會讓下一次跑不起來的洩漏,只有 F1、F2 兩個修前就在的毛病和 F3 一個修補帶來的磁碟累積。
