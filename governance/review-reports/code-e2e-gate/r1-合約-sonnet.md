severity: major

說明:以下重現都在 `/tmp/lumos-seat-work/code-e2e-gate/合約-sonnet/` 的 clone(提交 0aecbf90)上做,沒動原 repo。收尾時 clone 和探針已刪,我自己留下的 `gctl-run-*` 現場也已刪。測試改動(mutation)都是改在 clone 的 `scripts/lumos`,測完還原。

## Findings

**1. 逃生出口 `LUMOS_SKIP_ANDROID_E2E=1` 在「被推送提交的 `.lumos/macrobench.json` 讀不懂」時不生效;沒用 E2E 的專案也會被這樣擋**
severity: major
blocking: 是
引句:「_e2e_gate_block(f"被推送提交的 macrobench.json {perr}")」
file: `scripts/lumos:_e2e_gate_body`(diff 內)先呼叫 `_e2e_gate_resolve`、`_e2e_gate_uses`,才檢查 `_in_ci` 與 `os.environ.get("LUMOS_SKIP_ANDROID_E2E") == "1"`。前兩步都會直接擋。
- 場景:專案不用 E2E,但 `.lumos/macrobench.json` 帶 BOM 或是壞 JSON。
- 現象:`code-loop check` 擋下,訊息卻照印「這一次整道先關掉:LUMOS_SKIP_ANDROID_E2E=1 git push」。
- 照做:設環境變數,照樣擋。
- 文件說這個變數能「整道不跑」:README 中英、skill、計劃 S17、`pp_cl_reason` 逃生路文字都這樣寫。實際只剩 `--no-verify`。
- 同一個順序也違反 README「沒用端到端驗收的專案,這道檢查一行都不印」。
- 重現(clone 內臨時測試,用 `_e2eg_proj`):
  - 把 `.lumos/macrobench.json` 提交成 `{not json`。
  - `lumos android-e2e check` 不帶環境變數:`rc 1 blocked ... 讀不懂(不是合格的 UTF-8 JSON 物件)`。
  - 帶 `LUMOS_SKIP_ANDROID_E2E=1`:輸出和 rc 完全一樣。
  - 無 `e2e` 段、只有 `results_dirs`、帶 BOM 的專案:`PLAIN 1 blocked`,加 SKIP 後仍 `blocked`。

**2. S9 條款說被推送提交把畫面、記憶體 check 拿掉也要擋,綁定測試只驗了拿掉 flow**
severity: major
blocking: 是
引句:「- [S9] 當被推送的提交自己改弱 `e2e` 段(關掉 stability、拿掉主線版要求的 flow、畫面或 check)時,判定應照主線版要求的塊核對紀錄並擋下、印出少了哪一塊」
file: `scripts/test_lumos.py:t_android_e2e_gate_reads_mainline_config` 只有「拿掉 other.yaml」一組。
- 改壞:把 `_e2e_runs_missing` 的「畫面」那一行刪掉,再把 `if ml_e2e.get("stability"):` 改成 `if False:`。
- 結果(改壞後逐支跑):`t_android_e2e_gate_reads_mainline_config`、`_by_feature`、`_needs_full`、`_newest_wins`、`_bad_record`、`_wiring`、`_survives_rebase` 全綠(3、10、8、5、11、5、2 passed, 0 failed)。
- 影響:被推送提交可以自己關掉記憶體和截圖,拿一份只跑了 flow 的整套 pass 過關。這是 S9 要防的事。

**3. S31「同一秒算較新」:按功能那條路沒有測試守**
severity: major
blocking: 是
引句:「`runs` 是 fail 而且結束時間不早於它(同一秒算較新)時,應擋下並印 `--case` 指令」
file: `scripts/lumos:_e2e_gate_by_feature` 的 `elif rt is not None and rt >= _e2e_ts(v["ended"])`;`t_android_e2e_gate_by_feature` 只用整套 12:00 對按功能 11:00,沒有等時刻的案例。
- 改壞:把 `>=` 改成 `>`,`-k android_e2e_gate_by_feature` 仍 `10 passed, 0 failed`。
- 改壞後,整套 fail 與按功能 pass 同為 `T1` 的紀錄,`check` 回 `rc 0 pass-by-feature`(原版回 `blocked`)。
- 對照:S30 的整套那條路有同秒案例,按功能這條路沒有。

**4. S14 寫了「`lumos doctor --ci` 不因此變紅」,測試沒驗**
severity: major
blocking: 是
引句:「`lumos doctor` 應列成提醒(`--ci` 不因此變紅)」
file: `scripts/test_lumos.py:t_android_e2e_ai_waiver_notice` 只跑 `doctor`,沒帶 `--ci`,也沒看 rc。
- 改壞:把 doctor AE 段的 `warn_soft([...` 改成會增加 issues 的 `warn([...`,`-k android_e2e_ai_waiver_notice` 仍 `7 passed, 0 failed`。
- 另外 S14 的「答別的不標看過」只測了沒人能答,沒測答 n;「標看過後三處都不再列」沒重驗推送那一行。這兩項是小缺口。

**5. 放行指令印出的理由占位字串本身就過得了「至少 10 字」檢查**
severity: minor
blocking: 否
引句:「print(f"    {_e2e_waive_hint(rep['fp'], rep.get('commit') or '')}", file=sys.stderr)」
file: `scripts/lumos:_e2e_waive_hint` 印 `--note "<為什麼放行,至少 10 個字>"`;`_e2e_waive_cmd` 的檢查是去掉空白後 `len(...) < 10`。
- 占位字串去空白後是 14 字(已量過),原樣照抄就被當成有效理由放行。
- README、skill 都叫人或 AI「照它印的那行」放行。無終端的 AI 可以不寫理由就放行,而這是推送閘唯一的出口。
- 對照:lint-waive 的 `_lint_waive_cmd` 是「補上理由照抄」,沒有這個洞。

**6. `lumos android-e2e check` 在 main 上直接開發時會誤報「找不到主線」,文件沒提 `--range-start`**
severity: minor
blocking: 否
引句:「lumos android-e2e check                                            # 推之前先看推送前檢查會不會擋、為什麼」
file: `scripts/lumos:_e2e_check_cmd`;README 中英和 skill〈準備推送〉都叫人先跑 `check`。
- 重現(bare origin、本機 main 領先一個提交,不帶參數):`找不到主線:有設 remote 但本機沒有任何追蹤 ref 認得出主線;先 git fetch`。我已 fetch 過,訊息誤導。
- 帶 `--range-start <origin/main 位置>`:正確回 `blocked ... 這一版沒有查證紀錄`。
- README 自己提到「直接在 main 上開發」,但沒說這種情況 `check` 要帶 `--range-start`。這也是固定席「Issues/code-loop守衛main-direct盲區」那一帶。

**7. 計劃寫的接線點和程式不一致**
severity: minor
blocking: 否
引句:「放行路徑的印出接進 `_cl_say_ok_extras`;擋下時待看那一行跟擋下原因一起印(接進 `_cl_say_block` 那段明細)」
file: 實作是 `_cl_say_e2e_notes()` 接在 `_cl_say_tail`(放行和擋下共用)。`_cl_say_ok_extras` 只印「Android 端到端驗收:{reason}」,`_cl_say_block` 沒有印待看行。接手的人會去錯地方找。

**8. 計劃〈查證紀錄長怎樣〉的 `waivers` 欄位清單少了程式會寫的 `commit`**
severity: minor
blocking: 否
引句:「`waivers`:每筆是 `by`(`human` 或 `ai`)、`who`、`at`(帶時差的 ISO 時間)、`note`、`acked`(布林)、`acked_by`、`acked_at`」
file: `_e2e_waive_cmd` 另寫 `"commit": commit or head`,清單沒列。

**9. 開場提示的適用條件,計劃改成和程式不符**
severity: minor
blocking: 否
引句:「開場提示另印一行「有 N 筆 AI 放行還沒人看過」與看的指令(不算防護層:不進 `lumos enforcement` 的列與分母,那裡查的是有沒有裝上;沒有 `e2e` 段的專案不印)」
file: `scripts/hooks/claude/lumos-entry-hook.py:main` 在沒有 `docs/*-knowledge` 時直接 `return 0`;`_e2e_ai_line` 也不看 `e2e` 段,只看有沒有紀錄檔。舊版計劃寫的「沒有 knowledge 時開場提示不印」是對的,這次被刪掉。README 中英的「the session-start notice keep listing it」對沒有圖譜的專案不成立。

**10. 驗證紀錄的前提被同一份 diff 作廢**
severity: minor
blocking: 否
引句:「revalidate_when: 改了 lumos-android-evidence skill 的 description 或〈端到端驗收〉一節、推送前檢查改成按功能判之後、換了預設模型」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-26_AI自己選分塊跑法探針.md` 的 `status: pass`。
- 同一份 diff 改了 skill 的 description 和〈端到端驗收〉一節,推送前檢查也改成按功能判,三個重驗條件全觸發。
- 它卻以 `status: pass` 掛進 `android-e2e-acceptance.md` 的 `verified_by`。受測的是舊 skill 和舊行為,不是這次的版本。

**11. S12 綁定測試沒守條款裡的句子一致和數字種類名**
severity: minor
blocking: 否
引句:「對照表句子跟計劃正本一致、兩支守衛測試認得含數字的種類名;放行時「提醒:」開頭的 AI 放行待看行與按功能放行行,經過真的 pre-push 也印得出來 [test:t_android_e2e_gate_wiring]」
file: `t_android_e2e_gate_wiring` 沒有比對句子,也沒驗守衛認數字。句子一致由未綁定的 `t_prepush_cl_reason_*` 兩支守。
- 檢查:pre-push 原因表、`_PPC_KIND_SENTENCES`、計劃正本三處第六句逐字一致(「Android 端到端驗收沒過、沒紀錄(或判不清)」)。逃生路文字的「上面那行 waive」在沒有指紋的擋下(逾時、找不到主線、先合主線)並不存在。

## 固定席圖譜判斷

- `lumos-cli-lifecycle`(re-inject)、`lumos-cli-read`(search 排除 superseded)、`guard-kill`(rc 優先序、`--json` 純度):這份 diff 沒碰這些路徑,不影響。
- `Issues/code-loop守衛main-direct盲區`:`pre-push` 只加對照表一行和逃生路文字,不影響合約,但見 finding 6(main 直推時 `check` 要帶 `--range-start`)。
- `存量漂移守衛`、`每支檔有家`、`筆記內容閘`:新碼落在 `android-e2e-acceptance`、`bound-tests-gate`、`codex-harness` 各自的家,新增的 PITFALL/WHY 的出處、根因、`[test:]` 都齊,不影響。

最高等級 major;擋實作的 4 條(1、2、3、4),不擋的 7 條(5 到 11)。
