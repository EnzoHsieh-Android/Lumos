severity: minor

## r1 守的測試名取最後一段後,常見方法名一次吃掉大量記憶體(沒有輸出上限)
severity: minor
blocking: 否 這不會做出錯的判定。它是資源壓力:時間有 20 到 30 秒的限制,記憶體隨 repo 大小線性漲,沒有上限。

引句:「term = {n: (n.rsplit(".", 1)[-1] if _dotted_ident(n) else n) for _p, n in keys}」

- 輸入:計劃綁了 `類別.方法` 形式的測試名,方法名是 `get`、`run`、`value`、`test` 這類常見字。
- 路徑:`_choice_test_blobs` 把名字縮成最後一段。接著用 `git grep -z -o -w -F -I -e <段>… <sha> -- '*.kt'` 一次查全樹,包含 main 正式碼。`-o` 對每個出現處各印一行。整份 stdout 由 `_lens_git` 用 `capture_output` 且 `text=True` 全部收進記憶體,之後才用 `_choice_is_test` 過濾。
- 預期:輸出和記憶體跟測試檔數量成比例,不被正式碼的出現次數放大。
- 實際:我造了一個 repo,1500 支 main 檔加 600 支 test 檔,每支約 300 行,字都很常見。
  - 4 個常見字,輸出 85,394,000 位元組(約 85MB)。
  - 5 個名字,耗時 1.5 秒,RSS 685MB。
  - 50 個名字(最多 20 個不同的字),RSS 1.3GB,耗時 5.5 秒。
  - 1 個名字 `get`,0.4 秒,RSS 170MB。
  - 每個名字的雜湊鍵 `sig` 約 24.6KB,是所有含該字的測試檔的物件編號串起來。
  - 測試名 `T1Test.zap` 在計劃裡其實指向 `T1Test` 這個類別,最後一段卻會匹配全樹每支含 `zap` 的測試檔。這只會多重跑,不會漏判。
  - 測試名越常見,查得越寬、輸出越大。
- 同一支函式在兩版完全相同(`awk` 抽出 `_choice_test_blobs` 到 `_choice_kill_pick` 的區段,md5 都是 `f3047706ef9cf03b4d8438cd45e2d0cb`)。
- file: `scripts/lumos:77933`(`_choice_test_blobs`,`-o` 與全樹 `*.kt` 的 grep 在 7965 行附近)
- 歸因:有證據的原有漏查。修前 04b21d1 與修後 83ac95c8 的該函式逐位元組相同,本輪修補沒碰它。
- 重現:`/private/tmp/lumos-seat-work/code-改動選擇點/資源-sonnet/m1.py`。腳本已把測試名寫死,依序跑 n=5、50、400,再用 `/usr/bin/time -l` 量 RSS。實驗用的 repo 已刪,要重跑得重新造。

## 三問的回答

**① 原問題的修復效果**
- K1(照貼的放行指令改走 shell 引號)已修好。
  - 修後:`python3.14 scripts/test_lumos.py -k choice_kill_waive_hint` 通過 3 條,涵蓋 `$(touch PWNED) x.kt`、一般檔名和含 `'` 的檔名。
  - 修前:修前行是 `lumos lint-waive choice:{_kill_esc(x['file'])}:{x['line']}`,沒有引號。該測試在修前不存在,所以修前沒有紅燈證據,只有程式文字。
  - 一般檔名的路徑沒變:`shlex.quote` 對乾淨字串原樣回傳。
  - 同類另一處 `scripts/lumos:78791` 早就用 `_sh_quote`,沒有同族遺漏。
- K2(推送前判定共用快取)已修好,且有翻紅證據。
  - 修後測試 `-k choice_guard_cache` 通過 2 條。
  - 我在臨時副本把 `_choice_guard(rr, rng, at_sha, cache=cache)` 的 `cache=cache` 拿掉,測試變紅:`_kt_sit_spec_names_calc` 被呼叫 2 次,斷言印出兩筆相同的呼叫。還原後回綠。
  - 修前版本沒有這支測試,所以沒有修前的紅燈。
- K3(點號名取最後一段)的測試 `-k choice_test_blobs_name` 8 條都通過,但功能本身是原有的(見 r1)。

**② 修補處的正常、錯誤與相鄰呼叫路徑**
- 推送前什麼路徑會不命中快取而沒有時限?我沒找到。
  - 快取鍵 `("spec", rng, at_sha)` 在 `_choice_push_scan` 和 `_choice_push_round` 裡相同。
  - `_choice_requirement` 在「沒有 kotlin-junit 平台」或「沒有改到 .kt」時先回 skip。除此之外一定先經過 `_choice_spec_calc`,把快取填上。
  - 算不出來時丟 `_KtSitUnverifiable`,不會走到 `_choice_guard`。
  - 沒帶 `cache` 的 `_choice_guard` 呼叫只在 `scripts/lumos:77531` 和 `scripts/lumos:78055`。這兩處是 choice-points 與 choice-kill 這類手動指令,不在推送路徑上。
  - 就算不命中,`_git_timeout(None)` 也是每次 git 20 秒,不是無限。我沒量這條路徑的總耗時,因為它在推送路徑上不會出現。
- `_choice_guard` 命中快取之後,讀計劃檔、`_platform_test_index` 這些本機讀檔沒有時限。我沒量過,標未判定。
- 推送前其他幾步各有獨立時限:治理帳和放行檔讀取各 `_CHOICE_GOV_BUDGET`=30 秒,test blobs 同樣 30 秒,挑壞法 15 秒。最壞總和超過 2 分鐘。
- 治理帳:真實帳 22MB、125660 行。`_gov_rows_at` 整檔 `read_bytes` 後逐行檢查。這次版本裡 choice-kill 事件為 0,`_choice_push_ledger` 耗時 0.09 秒、RSS 128MB。帳放大後只是線性成長,不是二次方。我沒有造出大帳實測,標為線性推論。

**③ 新發現在修前、修後各是什麼**
- r1 的結果兩版相同,見上面歸因。
- 沒有發現修補引入的新問題。

## 圖譜鏡頭
這次沒附固定席節點(鏡頭計算超時),所以我沒有逐條判節點。

## 未驗範圍
- 真實 Android 專案端到端的耗時。
- 本機有 ast-grep 時的掃描子程序,在逾時或 Ctrl-C 時有沒有孤兒。這不是本輪修補範圍,我沒碰。
- 清理:`git worktree remove` 已移除我的臨時 worktree,實驗 repo 和 `__pycache__` 已刪。臨時目錄只剩 m1.py 和 m2.py 兩支腳本。

最嚴重:minor;blocking 共 0 條
