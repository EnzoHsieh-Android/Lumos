severity: blocker

審查對象是 HEAD=5cca7a1372d5a4be08f5d28bc88bdc494aa5d75a。實驗都在 `/tmp/lumos-seat-work/code-測試總檔預設切片/正確性-sonnet/`。我跑的都是帶 `--serial -k` 或沙盒副本,沒有改壞 `_fanout_wanted`。我開過的測試子程序和暫存資料夾都已收掉,只有上述實驗目錄留給編排者刪。

## 1. 新加的 SIGINT 中斷測試在背景 shell 裡必紅,還會留下孤兒
severity: blocker
blocking: 是
引句:「p = _sp.Popen([sys.executable, str(runner)], stdout=_sp.PIPE, stderr=_sp.PIPE, text=True, env=env)」
file: `scripts/test_lumos.py:30854`(`_fan_interrupt_case`)

- **失敗場景**:推送前掛鉤和 CI 都用 `... &` 在非互動 bash 裡起測試片。這種背景程序的 SIGINT 被設成忽略,而且 exec 之後仍然保持忽略。
- 測試用 Popen 起沙盒母程序,沒有把 SIGINT 裝回預設。
  - Python 啟動時看到 SIGINT 已被忽略,就不裝 `default_int_handler`。
  - 於是 `p.send_signal(SIGINT)` 沒有效果。
  - `communicate(timeout=30)` 逾時後測試改用 `p.kill()`(SIGKILL),各片沒人收,變成 ppid=1 的孤兒。
  - 斷言看到 returncode=-9 和四個還活著的 pid,判紅。
- 圖譜 `Systems/bound-tests-gate` 的 PITFALL(2026-10-13)寫過同一根因,修法是「送中斷的子程序開頭先把 SIGINT 裝回預設」。這個測試沒套用。
- **重現**(只跑這一支,有 `--serial -k`):
  ```
  env -u LUMOS_FANOUT_CHILD -u LUMOS_TEST_SHARDS bash -c 'python3.14 scripts/test_lumos.py --serial -k t_runner_default_fanout_interrupt > out.txt 2>&1 & wait $!'
  ```
  實測結果:
  - `✗ S8 母程序收到 SIGINT 後各片都收掉了、回 130 ([16083, 16086, 16085, 16084], -9)`
  - rc=1
  - 耗時 52.8 秒
  - 四個 `--shard i/4` 孤兒留著
- 影響:每次推送前的全套和 CI 都會假紅,因為這兩處都是背景起片。

## 2. 各片是否整個行程群組被收掉,沒有任何測試鑑別得出來
severity: major
blocking: 是
引句:「                    os.killpg(p.pid, sig)」
file: `scripts/test_lumos.py:48833`(`_fanout_kill`);測試在 `scripts/test_lumos.py:30854` 附近

- S8 要求「整個行程群組」被收掉,但中斷測試只檢查各片領頭程序(假測試自己 sleep)的 pid。沒有任何一片開出會留下來的孫程序。
- **變異實驗**:在副本把 `os.killpg(p.pid, sig)` 改成只送給領頭的 `os.kill(p.pid, sig)`,再跑 `--serial -k t_runner_default_fanout_interrupt`,結果 `6 passed, 0 failed`。守衛被改壞,測試照綠,屬於 `Systems/測試假綠形態` 那一型。
- 程式碼本身也有缺口:`_fanout_kill` 只要領頭程序在 TERM 後死了,`live` 就是空的,直接 return,不會對同組還活著的孫程序補 KILL。遇到忽略 TERM 的孫程序,這條會漏收。(⚠ 這點沒重現,交編排者判斷。)

## 3. 起片途中出現非 Ctrl-C 的例外,已開的片全變孤兒,而且片數沒有上限
severity: major
blocking: 是
引句:「        log = open(work / f"shard{i}.log", "wb")」
file: `scripts/test_lumos.py:48925`(`_fanout_spawn`);例外處理在 `scripts/test_lumos.py:48909`

- `_fanout_main` 只接 `KeyboardInterrupt`。`Popen` 或 `open` 丟 `OSError`(EMFILE、EAGAIN、記憶體不足)時,例外一路噴到外面,不呼叫 `_fanout_kill`。`finally` 只關記錄檔,不收程序。
- **重現**(沙盒副本,子程序都帶 `LUMOS_FANOUT_CHILD`):`ulimit -n 12; LUMOS_TEST_SHARDS=40 ZZFAN_MODE=sleep python3.14 box/scripts/test_lumos.py`
  - 母程序印出 `OSError: [Errno 24] Too many open files`,離開碼 1。
  - 已開的 6 片 `--shard i/40` 的 ppid=1,繼續跑。
  - 暫存資料夾 `lumos-fanout-*` 也沒清。
- `_fanout_shards` 沒有任何上限。`LUMOS_TEST_SHARDS=1000` 時,macOS 預設 256 個檔案描述子在 EMFILE 之前,已經夠把機器吃到當機。這跟 2026-11-05 的炸彈同類(只是量級要靠片數推)。
- 同一個缺口也包含 SIGHUP:關終端機時母程序直接死,各片在自己的 session 裡,沒人收。計劃只列了 SIGINT/TERM/KILL。

## 4. 片數環境變數的判法跟推送前掛鉤不一致,`²` 還會讓執行器崩潰
severity: minor
blocking: 否
引句:「    v = os.environ.get("LUMOS_TEST_SHARDS", "4").strip()」
file: `scripts/test_lumos.py:48808`(`_fanout_shards`)

計劃寫「跟推送前閘同一個變數、同一套判法(不是正整數就當 1)」,實測不是:
- `LUMOS_TEST_SHARDS=""`:掛鉤的 `${…:-4}` 取 4,執行器取 1(串行)。
- `" 4 "` 和全形 `"４"`:掛鉤的正則不過,取 1;執行器 strip 或 `int()` 之後取 4,會切片。
- `"²"` 或 `"①"`:`isdigit()` 為真但 `int()` 丟 `ValueError`,不帶條件的整個執行器 traceback 崩潰。在 Python 直接驗過。

## 5. `-x` 在切片模式下不會停掉其他片
severity: minor
blocking: 否
引句:「        + (["-x"] if args.exitfirst else []) + (["--ff"] if args.ff else [])」
file: `scripts/test_lumos.py:48899`

- 掛鉤擋下時教人敲的快速重跑是 `scripts/test_lumos.py --ff -x`(`scripts/hooks/pre-push:981`)。
- 以前這條「紅就停」可以幾秒內回來;現在不帶條件會切片,`-x` 只停紅的那一片。`_fanout_wait` 等全部片結束才回,其他綠片要跑完約 4 分鐘。
- 這符合 S6 的字面,但這條推薦的快速迴圈實際變慢。

## 6. 合併摘要沒反映當掉的片和跳過加總判紅
severity: minor
blocking: 否
引句:「Path(args.json_summary).write_text(_j.dumps({**tot, "shard": None}, ensure_ascii=False), encoding="utf-8")」
file: `scripts/test_lumos.py:48944`(`_fanout_report`)

- 某片沒寫出摘要時,合併摘要的 `failed` 是 0、`passed` 只有其餘片的數字,`bad` 沒寫進檔,程序離開碼卻是 1。
- 只看 JSON 的消費者會把當掉的全套讀成零紅。
- 只有跳過加總判紅(`bad == [0]`)時,還會印出空的「沒過的片,完整輸出在:」(`scripts/test_lumos.py:48950`),而且留下工作目錄卻沒有任何路徑可指。

## 圖譜鏡頭
- **`Systems/測試假綠形態`(含 ★INVARIANT★「還原翻紅釘須有前置斷言」)**:新測試大多有 ★前置★,沒違反那條。但第 2 條是同族的「測試鑑別不了守衛」,而且第 1 條說明 S8 的 SIGINT 前置(沙盒母程序真的會被中斷)在背景 shell 裡不成立。
- **`Systems/bound-tests-gate`**:
  - 綁定測試走 `-k {method}`,不受預設切片影響,★INVARIANT★ 沒被破壞。
  - 它的 PITFALL(背景起的程序忽略 SIGINT)正好是第 1 條的根因,新測試沒照做。
  - 掛鉤在 `_shards<=1` 時不帶 `--shard`,由執行器自己決定要不要切;第 4 條的判法不一致就在這裡露出。
- **`Systems/測試執行器`**:新節點,沒有既有合約可破壞。
- 其餘 `Systems/lumos-cli-read` 等只因為共用 `scripts/test_lumos.py` 列在牽連清單,這份 diff 不改它們的行為。

總結:全份最高 blocker
