severity: major

## 1 測試從 markdown 抽出 shell 腳本來執行,專案沒有先例
severity: major
blocking: 是
引句:「m = _re.search(r"```sh\n(.*?)```", ref.read_text(encoding="utf-8"), _re.S)」

我重判後仍認為這是「引入第二種做法」,維持 major,所以 blocking 改成「是」。派工詞明列「測試從 markdown 抽腳本來跑而專案沒有先例」屬於這一類。

`t_android_evidence_rerun_refuses_empty` 從 `skills/lumos-android-evidence/reference.md` 抽出 ```sh 區塊,寫成 `rerun.sh`,再用 `sh` 執行。這是第二種做法。

- **既有的圍欄抽取只讀不跑。** `scripts/test_lumos.py:11708`、`:57966` 用 `findall(r"```[a-z]*\n(.*?)```")` 取出文字,只做斷言,沒有把它當程式執行。
- **既有的跑外部程式測試跑的是真檔案。** `_mb_run`(`scripts/test_lumos.py:17552`)用 `sp.run([sys.executable, GRAPHCTL, ...])` 跑 repo 內的真腳本。
- **這支測試把文件裡的範本當程式碼跑。** 範本文字一改,測試行為就跟著變,沒有獨立的被測物。我在 `scripts/test_lumos.py` 裡沒找到這種先例。
- 範本本身是 `sh` 加 `python3 - <<'PY'` 的混合體。它是給專案用的範本,不是 skill 目錄裡的可執行檔。`skills/` 底下我沒找到可執行檔或 `.sh`/`.py`,所以「skill 目錄放可執行檔」這項沒有成立。

## 2 新測試沒有「消費端沒有 skills/」的守衛
severity: minor
blocking: 否
引句:「ref = Path(GRAPHCTL).resolve().parent.parent / "skills" / "lumos-android-evidence" / "reference.md"」

鄰居讀 skill 文件的測試,在 `skills/` 不存在時會先 `raise _SrcOnly("消費端沒有 skills/(非來源 repo),這段沒驗到")`,例如 `t_data_state_lens_doc_sync`(`scripts/test_lumos.py:58015` 起)。全檔有 70 處 `_SrcOnly`。

新測試直接 `ref.read_text`。消費端裝的 `scripts/lumos` 如果沒有 `skills/`,這裡會丟 `FileNotFoundError`,不會被標成「沒驗到」。結構是對的,只是少了鄰居的守衛寫法。

## 三問

**1. 分層與依賴方向:對齊,沒有跨層直呼。**
- 新函式 `_macrobench_num`、`_macrobench_threshold_item_err`、`_macrobench_thresholds`、`_macrobench_check_thresholds`、`_macrobench_print_thresholds` 都放在 `scripts/lumos` 的 `MACROBENCH_*` 區塊內,緊貼 `_macrobench_config_fields` 與 `_macrobench_collect`。
- 分工和既有的讀設定、判斷、印出相同,由 `cmd_macrobench` 串起來。
- `_macrobench_num` 呼叫 `_secev_num`(`scripts/lumos:8554`),往下一層、方向正確,沒有繞過別層。
- 測試輔助 `_mb_thr`、`_mb_thr_root`、`_mb_scroll` 沿用 `_mb_run`、`_mb_result_json` 的 `_mb_` 命名,放在 `t_macrobench_*` 區。

**2. 命名與錯誤處理:對齊。**
- 檔案壞掉回 `(None, 錯誤訊息)`,`cmd_macrobench` 用 `print(f"擋下:...", file=sys.stderr)` 加 `return 2`,和既有設定檔的處理一樣。
- 「只提醒,不擋推送」的文字,以及有退步或沒達門檻仍回 0,都和既有行為一致。
- `--json` 多出的三個欄位直接併進同一份 `res`。
- 函式內 `import math`、`import datetime` 的局部匯入,和鄰居的寫法相同(`scripts/lumos:5100`、`:19742` 有同樣模式)。
- 測試暫存目錄前綴 `gctl-*` 合慣例,子行程用 `import subprocess as sp`。

**3. 第二種做法:只有第 1 條。**
- 數字檢查沒有另起一套。`_macrobench_num` 是在 `_secev_num` 外面加 `math.isfinite`,而且 macrobench 區原本所有 `_secev_num` 呼叫點都改成它了。
- 專案裡本來就有行內的 `math.isfinite`(`scripts/lumos:52191`、`:58317`),所以「有限數」也不算新做法。
- 設定檔仍是 `.lumos/*.json`,讀法與 `macrobench.json`、基準檔一致。
- 其他 `_secev_num` 呼叫點(`scripts/lumos:9257` 起,k6 那一帶)仍收 NaN。這在 macrobench 範圍外,我不列為不對齊。
- 第 1 條是唯一的新做法。

不對齊共 2 條,其中 major 1 條
