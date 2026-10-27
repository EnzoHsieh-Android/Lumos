severity: major

先講結論:這道判定的順序和銜接大致照計劃走(放行、整套、按功能),時間比先後、同一秒算較新、舊紀錄缺欄位都有處理。但我找到三個會判錯的輸入:只改設定的提交會被放過、環境變數出口在最前面兩步無效、兩個必要行為被改壞測試仍全綠。

重現用的是 `scripts/test_lumos.py` 的 `_e2eg_proj`、`_e2eg_check`、`_e2eg_commit` 輔助函式,在暫存專案跑。變異測試用的是 e2e-gate 的複本,跑 `-k android_e2e_gate`。臨時目錄已刪。

## Findings

**1. 只改 `.lumos/macrobench.json`、樹其他部分不變的提交,不需要驗收就放行(含整段刪掉 `e2e`、拿掉一支 flow、關掉 `stability`)**
severity: major
blocking: 是
- 位置:file: `scripts/lumos:41572-41591`(`_e2e_gate_fps`)。
- 引句:「        _e2e_gate_done("not-required", "App 程式與驗收素材跟分岔點一樣", fp=fp)」
- 失敗場景:
  - 分岔點和被推送提交兩端用同一份設定(`sel`)算指紋。所以只動設定的提交,`e2e-config` 那一行兩端相同。
  - `.lumos/macrobench.json` 不在指紋範圍內。範圍只有 `app_dirs`、`.maestro`、門檻檔和 flows。
  - 兩端指紋就相等,直接回 not-required,下游全走不到。這包括 `_e2e_gate_need` 裡「`e2e` 段跟分岔點不一樣就要整套」和 `memory-config` 比對。
  - `stability_scenarios` 改弱(例如 cycles 調小)是同一種漏洞:`memory-config` 也用被推送提交那一份算兩端。
- 與計劃的衝突:
  - 計劃〈回退〉寫「刪段的那次推送本身用環境變數關掉」,實作卻是靜默放行。
  - S9 要求被推送提交自己改弱 `e2e` 段時要擋。現有 S9 測試的「weaken」提交同時動了 `A.kt`,剛好繞過這個缺口。
  - 同樣是刪 `e2e` 段,同時改 `A.kt` 會被擋(「先把主線合進來」),只刪段反而過。兩者不一致。
- 重現:
  ```
  root=_e2eg_proj(td); _e2e_set_cfg(root, lambda c: c.pop("e2e"), commit="delete e2e only"); _e2eg_check(root)
  → (0, {'status': 'not-required', 'reason': 'App 程式與驗收素材跟分岔點一樣', ...})
  ```
  - 同樣的輸入,在 `_e2e_set_cfg` 裡把 `flows` 拿掉一支、或 `drop` 掉 `features.other`,也回 0 not-required。
  - 對照:刪 `e2e` 段再加 `commit A.kt`,回 `(1, blocked, 這個提交沒有 e2e 段…)`。

**2. `LUMOS_SKIP_ANDROID_E2E=1` 在 `_e2e_gate_resolve` 與 `_e2e_gate_uses` 之後才檢查,這兩步擋下時訊息教的出口無效**
severity: major
blocking: 是
- 位置:file: `scripts/lumos:41632-41640`(`_e2e_gate_body`),順序是 resolve、uses、`_in_ci`、跳過旗標。
- 引句:「    pushed = _e2e_gate_uses(root, sha, pushed_branch, deadline)」
- 失敗場景:
  - 被推送提交的 `.lumos/macrobench.json` 壞掉、有 BOM,或在樹裡卻讀不出內容(物件缺),會在 `_e2e_gate_uses` 或 `_e2e_gate_resolve` 擋下。
  - 預算在這兩步前段用完,同樣是擋下。
  - 擋下訊息(`_cl_say_e2e_block`)和逾時訊息都印「這一次整道先關掉:`LUMOS_SKIP_ANDROID_E2E=1 git push`」。
  - 這個變數卻要等到那兩步通過才會看。照做仍然被擋,依 S17 的出口承諾解不開。
- 重現:
  ```
  _e2eg_commit(root, {".lumos/macrobench.json": "{broken"})
  _e2eg_check(root)                                  → (1, blocked, …讀不懂…)
  _e2eg_check(root, env={"LUMOS_SKIP_ANDROID_E2E":"1"}) → (1, blocked, …讀不懂…)   # 同樣被擋
  ```
- 測試缺口:`t_android_e2e_gate_unclear_blocks` 只在沒有更早擋下的情況測旗標。

**3. 兩個必要行為被改壞,`t_android_e2e_gate*` 仍全綠(實測變異)**
severity: major
blocking: 是
- 在 e2e-gate 的複本上改 `scripts/lumos`,跑 `python3.14 scripts/test_lumos.py -k android_e2e_gate`:
  - M1:把按功能那條路的 `rt >= _e2e_ts(v["ended"])` 改成 `rt > …`。結果 69 passed, 0 failed。
    - 這等於把「同一秒算較新」(S31)改掉,同一秒的整套 fail 反而放行。
    - 測試只測了整套那條路(S30)的同一秒,以及按功能那條路整套比較晚。
    - 引句:「        elif rt is not None and rt >= _e2e_ts(v["ended"]):」
  - M2:`_e2e_case_covered` 只留 flow、拿掉畫面和記憶體情境。結果 69 passed, 0 failed。
    - 這等於 `items` 少了截圖或記憶體項目也放行(S31、計劃第 5 步)。
    - 測試只拿 flow 缺項測 items 涵蓋。「略過記憶體」案例被 `skipped` 那一條先擋了,蓋不到這支。
    - 引句:「    want = ([("ui", _e2e_norm(f)) for f in c.get("flows") or []] + [("visual", x) for x in c.get("visual") or []]」

**4. 只列效能的情境改動,沒有任何紀錄時擋下,且訊息的情境清單是空的**
severity: minor
blocking: 否
- 位置:file: `scripts/lumos:41593-41611`(`_e2e_gate_load`)與 `_e2e_gate_need`。
- 引句:「按功能跑這幾個情境就夠:" + "、".join(info["cases"])」
- 失敗場景:
  - 只改到一個只列效能的功能(例如 `bench.scroll`,`need` 是空清單、`perf_only=["bench.scroll"]`)。
  - 計劃第 4、6 步說這種情境不用驗,應放行並印「沒驗:…」。但 `_e2e_gate_load` 先要求紀錄存在,沒有紀錄就擋。
  - 訊息變成「按功能跑這幾個情境就夠:」後面是空的。後續的指令行退回「整套跑」。
- 重現:`_e2eg_proj(td, e2e={"macrobench":True,"macrobench_cmd":"sh r.sh {{TEST}}"}, top={"results_dirs":["r"]})`,加 `perf` 功能(只有 `macrobench:["Bench#one"]`)並合進 main,再改 `C.kt`,`_e2eg_check` 回:
  ```
  1 {"status":"blocked","reason":"這一版沒有查證紀錄(…);按功能跑這幾個情境就夠:", "need":"cases","cases":[],"perf_only":["perf.p"]}
  ```
- 等級說明:行為是否算錯取決於計劃對「全部只列效能且沒紀錄」的意圖,我不確定,所以只標 minor。

**5. 開場掛鉤的 `_e2e_ai_line` 遇到一份壞紀錄,整個提醒就消失**
severity: minor
blocking: 否
- 位置:file: `scripts/hooks/claude/lumos-entry-hook.py:719-745`(diff 約 719-745 行)。
- 引句:「            rec = json.loads(p.read_text(encoding="utf-8"))」
- 失敗場景:`.lumos/e2e-records/` 底下有一份 JSON 壞掉的檔(例如合併留下衝突標記),整個函式的 `try` 吞掉例外並回 None。其他紀錄裡的 AI 放行待看提醒也跟著不印,S14 要求要印。`doctor` 走的 `_e2e_records_all` 會跳過壞檔,兩邊行為不一致。
- 重現:
  - 一份合格紀錄(`by:ai`、`acked:False`)時 `_e2e_ai_line(Path("."))` 回非 None。
  - 再放一份內容是 `<<<<<<< HEAD\n{}\n` 的 64 碼檔名後,回 None。

## 逐點確認過、沒問題的地方

- **鎖(`_E2eRecordLock`)與 `_e2e_record_update`**:`with` 在早退和例外路徑都會 `__exit__` 放鎖。`WriteBlocked` 從 `__enter__` 丟出時沒持鎖,已接住。`--ack` 中途失敗只留下已標好的幾份,重跑只處理還沒標的。
- **放行(waive)**:
  - 確認在拿鎖前(S13)。
  - 同一指紋可有多筆放行,只增不刪。
  - 重跑 judge 不會蓋掉放行。
  - `--ack` 只動 `by==ai` 且未 acked 的放行。
- **時間與新舊互讀**:
  - `_e2e_ts` 要求帶時差,同一秒走保守(判為較新)。
  - 舊紀錄缺 `feature_runs`、`waivers` 時 `.get(…) or {}` 處理得了。
  - `runs=null`、只有 `feature_runs` 的紀錄會走按功能判。
  - 欄位型別不對的例外進 `_e2e_gate_evaluate` 的 `except Exception`,結果是擋下(不放行)。
- **判定順序**:放行、整套(含較新的 fail)、按功能的順序與計劃一致。`_confirm_tty` 的 `stdin_timeout` 預設路徑沒有變動(只是把 `LUMOS_TTY_TIMEOUT` 的解析提前),空字串視為 EOF 再試第 2 階。
- **pitfalls manifest**:`pitfalls-builtin` 在新增行上只有兩條,都是誤報。
  - `scripts/lumos:41707` 的 `os.open` 用 `try/finally` 關 fd。
  - `scripts/lumos:41733` 的 `time.sleep` 在迴圈裡,上限由 `wait`(預設 60 秒)封頂。
  - 兩者落在併發類題目,屬範圍外。
- **圖譜鏡頭(固定席)**:
  - `lumos-cli-lifecycle` 的 INVARIANT(re-inject 只動 sentinel 之間)和 `lumos-cli-read`(search 預設排除 superseded)不受影響,diff 沒碰 re-inject 或 search。
  - `guard-kill` 的 rc 優先序與 JSON 純度也不受影響,改動不在 `guard kill` 路徑上。
  - `Issues/code-loop守衛main-direct盲區` 的 pre-push 只加對照表一行與逃生文字,沒動 main-direct 判斷。
  - `pitfalls-code-loop`、`存量漂移守衛`、`每支檔有家`、`筆記內容閘` 牽連的是新增接線與文件,沒找到會破壞其宣稱行為的地方。
- **角色卡**:
  - be-api-compat:`code-loop check --json` 只在 `status != none` 時多一個 `android_e2e` 鍵,紀錄格式的新欄位都可缺,舊讀法不受影響。
  - be-authz:本案是本機 CLI,沒有端點。放行的人或 AI 之分靠終端確認,屬計劃已排除的威脅模型,不影響本次判定。
- **條款對照**:S13、S14、S17(其餘)、S29–S37 與實作一致,除了 S9、S17 的前述缺口(Finding 1、2)和 Finding 3 的覆蓋面。

最高等級 major;擋實作的 3 條(1、2、3),不擋的 2 條(4、5)。
