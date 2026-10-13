severity: minor

## 1. 通過代碼審後把設定改成 1 會讓留痕失效,〈回退〉卻寫成只走 light 閘
severity: minor
blocking: 否
引句:「設定檔不在簿記清單,改它要照常走推送閘(只改設定檔時風險分級是 light)。」
file: `scripts/lumos:49080`(`_codeloop_record_valid_ex`)、`scripts/lumos:49486`(`_codeloop_guard_verdict`)

失敗場景與歸因:
1. 上線後出事,按〈回退〉只把 `bound_tests.parallel` 改成 1 再推。
2. 我在臨時 clone 的 `54b01b1a` 上這樣做,多一個只改 `.lumos/config.json` 的提交。接著用 `54b01b1a`(假設它是通過的留痕 sha)當記錄、新提交當目標,呼叫 `_codeloop_record_valid_ex`。回傳 `(False, '記錄 sha 54b01b1a 之後動了代碼(非純簿記增量)', False)`。
3. `.lumos/config.json` 不在 `_BOOKKEEPING_FILES`,所以已過的留痕會失效。
4. 推送閘的 tier 是照整段 merge-base..HEAD 算的,不是只看這個提交。`pitfalls --diff a701909c..HEAD --no-lint` 在這段範圍上回 `tier: high`。所以「只改設定檔是 light」只對單看那個提交成立,對推送閘不成立。
5. 結果是想快速停用,卻要重跑一次代碼審,或用 `code-loop skip` 加 `--note`。計劃沒寫這一步。
6. 這不會讓你收拾不了,只是計劃裡的說法不準。
7. ⚠ 我沒在真實分支上跑完整的 `code-loop check`,它會真跑綁定測試,太慢,被我中止。失效判定是直接呼叫函式驗到的。
8. 歸因:有證據的原有漏查。這是新計劃文字的錯,不是修補差異引入的。

建議在〈回退〉補一句「通過代碼審後改設定會使留痕失效,要重審或 skip」。

## 回滾鏡頭判定
我在臨時 clone 實操了計劃〈回退〉的各步,其餘都走得通。

- **整段還原**:`git revert -n a701909c..HEAD` 乾淨成功。它拿掉全部 6 個提交,包含 `docs/.canary-log.jsonl` 和 `docs/.governance-log.jsonl` 的帳行,所以計劃說的「先另存帳行再接回」確有必要,也如實寫了。
- **設定改成 1 或整個拿掉**:兩種做法下 `-k bound_tests_parallel` 都是 46 passed、0 failed。S3 沒有因此轉紅,計劃說對了。
- **舊帳與新帳混用**:帳上 secs 的兩種來源靠 `secs_kind` 分得開,計劃有寫。
- **`_kill_run` 多了 `started=None`**:
  - 其餘三處呼叫(`scripts/lumos:17432`、`17478`、`48136`)都沒傳這個參數,行為不變。
  - `test_lumos.py` 裡沒有替身或 monkeypatch 去換 `_kill_run`,不會有簽名不合。
  - 同一份腳本內沒有新舊混用的問題。
  - `-k guard_kill` 的 289 條我沒重跑,只讀程式確認沒動。
- **推送閘自己壞掉的逃生路**:`LUMOS_SKIP_BOUND_TESTS=1` 和 `--skip-bound-tests --note` 都在 `_bound_tests_check` 最前面(`scripts/lumos:48440`),早於 `_bound_tests_parallel` 和工作執行緒。並行路徑壞了也擋不住這條逃生路。
- **循序模式**:出錯或 Ctrl-C 的行為跟修補前相同。`_BtProcs` 只在並行分支才會 `reap`。
- **留下的程序**:我的測試沒有留下孤兒。

## 圖譜鏡頭(固定席)
- **guard-kill 的兩條 INVARIANT**:`_kill_run` 預設參數不變,rc 優先序和 `--json` 單行輸出不受影響。新增的提醒只印 stderr,而且只在 `_bound_tests_parallel` 裡。
- **bound-tests-gate 的 INVARIANT**:紅、懸空、偽證據、不可證明跑過仍然擋(blocked、rc1),判定沒動。沒 `run_cmd` 或沒綁定時仍然不擋、寫帳。帳多了 `secs_kind`,不影響判定。這份 diff 沒有改動這條 INVARIANT 的描述。
- **測試假綠形態**:新測試是否都有「現場成立」的前置斷言,我沒逐支查,留給架構席。
- **lumos-cli-read、lumos-cli-lifecycle、design-loop、loop-convergence-recording、pitfalls-code-loop**:diff 沒碰它們的行為,不受影響。

## 三問與已驗範圍
- **①修復效果**:我只驗了回滾面,沒獨立重現孤兒程序的修復。`t_bound_tests_parallel_error_stops_fast` 在 clone 裡綠,0.3s。
- **②正常與相鄰路徑**:設定為 1、拿掉、4 這三種值下,並行的測試子集都綠。
- **③修前修後**:回滾面的案例沒有修前版本可比,標未判定。

總結:最高等級 minor
