severity: major

## 1. 子程序開頭還原訊號遮罩這件必要行為沒有任何測試守著
severity: major
blocking: 是
引句:「kw["preexec_fn"] = lambda: _sig.pthread_sigmask(_sig.SIG_SETMASK, old)」
file: `scripts/test_lumos.py:49190`(c816c9f 版 `_fanout_spawn`)

失敗場景:
- 修補在開片時用 `pthread_sigmask` 擋住 INT、TERM、HUP。擋住的遮罩會跨 fork 和 exec 留給子程序。
- 子程序唯一還原遮罩的地方就是這行 `preexec_fn`。沒有它,各片和片裡再開的程序永遠收不到 INT、TERM、HUP。
- 我拿一個小程式驗證遮罩確實會被繼承。有 `preexec_fn` 時子程序的遮罩是 `[]`,拿掉後是 `[1, 2, 15]`。
- 我把這行換成 `pass`,放在複製出來的 scripts 目錄裡,清掉 `__pycache__` 後跑五組相關測試:
  - `-k t_runner_default_fanout_interrupt`:9 過 0 紅。耗時從 20.7s 變 35.4s,可見突變有生效,但測試仍綠。
  - `-k t_runner_fanout_signal_handling`:9 過。
  - `-k t_runner_default_fanout_spawn_error`:3 過。
  - `-k t_runner_default_fanout_green`:7 過。
- 這幾組測試抓不到,原因有兩個:
  - 中斷測試的孫程序本來就忽略 TERM,母程序最後送 KILL 也能收乾淨。
  - `signal_handling` 和 `spawn_error` 用假的 `Popen`,走不到 `preexec_fn`。
- 遮罩一旦沒還原,後果發生在各片裡。我模擬片子程序被擋 INT、TERM、HUP 起來,再跑 `-k t_prepush_interrupt_stops_every_gate`:
  - 不擋時 39 過。
  - 擋住時多條 `✗ ②…被殺掉 → …`(例如「裁判簽名 anchor verify被殺掉」「圖譜健檢 doctor --ci被殺掉」),測試失敗。
- 所以全套預設切片會冒出假紅。
- 計劃 S8 的 `[test:]` 和 `Systems/測試執行器` 的 WHY 行也都沒寫這件事。

歸因:有證據的修復回歸。
- 修前 `4efa74f` 根本沒有遮罩,不可能繼承。
- 修後 `c816c9f` 才引入遮罩,測試缺口也是同時引入的。
- 兩版查證:
  - 修前 `git show 4efa74f:scripts/test_lumos.py` 的 `_fanout_spawn` 沒有 `pthread_sigmask`。
  - 修後的小程式與突變結果如上。
- 目前程式本身正確,風險在日後有人改壞時沒有測試會紅。

## 2. `Systems/測試執行器` 的 WHY 行綁的測試沒涵蓋它宣稱的 gctl-run- 前綴
severity: minor
blocking: 否
引句:「記錄檔資料夾用 gctl-run- 開頭 [出處:[[Projects/測試總檔預設切片_計劃]] 做法 2、3]」
file: `docs/lumos-toolchain-knowledge/Systems/測試執行器.md` summary 最後一行

失敗場景:
- 這行 WHY 只綁 `[test:t_runner_fanout_signal_handling]`。
- 前綴是由 `t_runner_default_fanout_red`(S2,patch 新增的那條 check)驗的,`signal_handling` 沒碰。
- 前綴被改回 `lumos-fanout-` 時,綁定的測試不會紅。
- 同一行裡「子程序開頭還原遮罩」完全沒寫。

歸因:有證據的修復回歸。
- 該行是這輪新增的,修前沒有。
- 修前:`git show 4efa74f:docs/lumos-toolchain-knowledge/Systems/測試執行器.md` 沒有這行。
- 修後:該行存在,綁的測試如上。

## 三問的回答

**① 原問題的修復效果,有行為證據的部分:**
- 開片與記下之間收到 TERM 不漏收:`-k t_runner_fanout_signal_handling` 9 過,「剛開的那片已在清單裡」「回 143」「收完還原」都成立。
- 收片時 INT、TERM 已先忽略:`spawn_error` 的 spy 在 `_fanout_kill` 當下看到 TERM 為 `SIG_IGN`,測試通過。
- nohup 下 HUP 保持忽略:同一個測試覆蓋。
- 紅燈資料夾會被修剪:`_isolate_environment` 掃 `real_tmp` 下的 `gctl-run-*`,條件是有 `.finished` 或超過一天。
  - 紅了留下的 `gctl-run-fanout-*` 沒有 `.finished`,所以超過一天會被收掉,符合計劃。
  - 副作用:帶 `--keep-tmp` 的全綠現場也會在一天後被收。
- 缺修前證據:修前沒有 `_fanout_hush`,新案例在修前只會 NameError。「修前行為」我只能從程式文字判斷(少了遮罩、少了忽略判斷),沒有實跑,標未判定。

**② 修補處相鄰路徑:**
- 子程序起來後收得到 TERM:是,前提是 `preexec_fn` 還原了遮罩(見 finding 1)。
- 沒有 `pthread_sigmask` 的平台:`mask=False`,不設 `preexec_fn`,也不擋訊號,退回修前行為。這條我沒實跑,只讀程式碼。
- `_fanout_hush` 之後 `_fanout_untrap` 還原的值:
  - INT 用 `setdefault`,存的是 `signal(SIGINT, SIG_IGN)` 回傳的前一個值,也就是原本的處理器。測試也驗到 `keep[SIGINT]`。
  - TERM、HUP 若已被 `_fanout_trap` 記過,維持原值;若原本忽略,記成 `SIG_IGN`。
- 非主執行緒:`signal.signal` 丟的 `ValueError` 被 `except` 接住,不裝處理器;`pthread_sigmask` 只作用於呼叫那條執行緒。我沒實跑。
- 沒開標成 finding 的殘餘窗口:`_fanout_hush` 逐個設 INT、TERM、HUP,且只在 except 裡才呼叫。第二個訊號若正好落在 except 進入到各訊號設好之間,KeyboardInterrupt 會跳過 `_fanout_kill`,各片變孤兒。我拿不出實際觸發,只能靠注入模擬,不開 finding。

**③ 新發現案例的修前、修後:**
- finding 1 的遮罩缺口:修前不存在遮罩,沒有問題;修後有遮罩,但沒測試守著(上面突變證據)。
- 其餘案例修前只有程式文字比對,沒有實跑證據,標未判定。

## Preserve 組(修後各跑一次,皆 `--serial -k`)
- `t_runner_default_fanout`:51 過 0 紅,含 interrupt、spawn_error、green、red、crash、passthrough、skip_total。
- `t_runner_fanout_shards_parse`:14 過。
- `t_runner_fanout_child_never`:3 過。
- 實驗後沒有殘留 `--shard` 子程序,我建的暫存已用字面絕對路徑刪除。

## 圖譜鏡頭
- `Systems/測試執行器` 與程式大致一致。
- 沒寫到的是「子程序開頭還原遮罩」和 finding 2 的綁定測試錯位。
- 因為 LUMOS-IMPACT 範圍的 base 不在會談專案歷史上,我沒用掛鉤,直接讀了 c816c9f 版節點。

## 未驗範圍
- 沒有 `pthread_sigmask` 的平台與非主執行緒呼叫,只讀程式碼。
- 殘餘窗口只在注入模擬層面討論,沒有真實觸發。
- 全套 8 分鐘的真跑,依規定沒有跑。
- 推送前閘與 CI 的背景環境,只模擬到「繼承被擋遮罩」這一層。

總結:全份最高 major
