severity: clean

本輪零 finding。沒有留下 `--shard` 子程序。

**已驗主張與證據**

我在 ed66cd8 的 `--shared` 臨時 clone 裡實測,clone 已刪。

- **新測試抓得到改壞(問題一)**:我把 `_fanout_spawn` 裡 `kw["preexec_fn"] = lambda: _sig.pthread_sigmask(_sig.SIG_SETMASK, old)` 換成 `pass`。
  - 原樣:`t_runner_fanout_spawn_mask` 3 條斷言全過。
  - 改壞後:紅(2 過、1 敗),敗的是「子程序起來時沒有任何訊號被擋」那條。
  - 這是 `pass` 版與原樣版的對照,所以不是測試本來就會紅。
  - 引句:「preexec_fn」出處見下方引句行。
- **整組 fanout 測試在 `--serial -k fanout` 全綠**:83 過、0 敗。範圍包含 `t_runner_default_fanout_spawn_error`、`t_runner_fanout_signal_handling` 和 `t_runner_fanout_child_never_fans_out`。
- **相鄰路徑(問題二)**:`mock.patch.object(sys.modules[__name__], "_fanout_kill", ...)` 的 `__name__` 是對的。
  - 測試總檔是當 `__main__` 跑(`--serial` 與 `--shard` 都一樣),`_fanout_main` 查的 `_fanout_kill` 就在這個模組的全域裡。
  - 全檔只有 `test_lumos.py:19175` 附近有別的 `__name__` 命名空間(`collector`),跟這裡無關。
  - 另外,`--shard 1/1 -k fanout` 跑完沒有 ✗ 或 FAILED。
  - 該輪我的 grep 沒印出 `passed` 彙總行,我沒追原因,所以「`--shard` 下 83 條全過」未驗。
- **非 POSIX 跳過的說法(問題二)**:`t_runner_fanout_spawn_mask` 用 `hasattr(_sig, "pthread_sigmask")` 判斷,跟程式 `mask = hasattr(_sig, "pthread_sigmask")` 同一條件,所以說法吻合。
  - Windows 上不擋訊號、也沒有可傳的遮罩,跳過合理。
  - 我只在 macOS 驗過,Windows 實跑未驗。
- **mock 還原(preserve)**:新寫法用 `with` 包住 `patch.object` 和 `patch.dict`,離開時一定還原。`_fanout_kill` 和 `subprocess.Popen` 都由上下文管理器還原,比原先 `globals()["_fanout_kill"] = ...` 少一個漏還原的洞。
- **相關檢查(問題三)**:
  - 修前 c816c9f 的測試是直接改寫 `globals()` 和 `_sp.Popen`,遮罩傳給子程序這件事沒有任何測試守著。
  - 修後有了。這是補缺口,不是回歸。

引句:「kw["preexec_fn"] = lambda: _sig.pthread_sigmask(_sig.SIG_SETMASK, old)」是修補前後都存在的 `_fanout_spawn` 內容,審材 patch 本身引到的是新測試的 docstring:「拿掉子程序開頭還原遮罩那行,各片收不到中斷」。

**圖譜鏡頭**

Systems/測試執行器 新增兩條 WHY,綁 `t_runner_fanout_spawn_mask` 與 `t_runner_default_fanout_red`,測試名都存在。計劃 S8 的 `[test:]` 也補了 `t_runner_fanout_spawn_mask`。三處的描述(遮罩跨 fork 與 exec 傳給子程序、子程序開頭還原)與程式一致。

**未驗範圍**

- Windows 實跑。
- 推送前閘與 CI 的完整流程(我只跑了 `-k fanout` 子集)。
- `LUMOS-IMPACT` 範圍(a7d8445..ed66cd8)算不出來,也沒讀 `impact.txt`。
- `--shard 1/1 -k fanout` 的 `passed` 彙總行。

**三問**

1. 修復有行為證據嗎?有。改壞還原遮罩那行,新測試會紅。
2. 相鄰路徑仍成立嗎?在 macOS 的 `--serial` 下成立;`--shard` 下沒看到失敗,但沒拿到彙總行確認。非 POSIX 跳過的說法對。
3. 新發現?無,修前與修後都是沒有。

總結:全份最高 clean
