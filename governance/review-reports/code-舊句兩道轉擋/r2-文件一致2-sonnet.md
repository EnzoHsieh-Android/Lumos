severity: minor

## F1 超長行判準改成整字後,散在各處的「純子字串」舊說法沒跟上
severity: minor
blocking: 否
引句:「2026-10-09 已修:舊句兩道轉擋把 `old_sentence` 沒寫改成照總開關、預設 block 之後,這條不用專案設定也會誤擋」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:164`(同篇「時間」條)、`docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:83,143,220,326`、`docs/lumos-toolchain-knowledge/Issues/舊句檢查超長行判準偏寬與留痕殘行.md:15,28,47`
歸因:有證據的修復回歸

1. 照存量漂移守衛第 164 行做,會以為「超長行裡只要以子字串出現消失的名稱,block 就擋」。
2. 實際上 5ce8115d 把 `_drift_m1_note_long` 改成 `_drift_m1_line_names` 整字先篩。真碼在 `scripts/lumos:39914-39920`,翻紅釘是 `t_drift_m1_long_line_whole_word`(`scripts/test_lumos.py:70592`)。
3. 修補只改了那篇 Issue 的「放行理由」和「什麼算修好」兩處。上面這些地方仍寫成現在的行為:
   - 存量漂移守衛第 164 行寫「行內以子字串出現任一這次消失的名稱的照判不了算」。
   - 舊句檢查計劃的做法段(第 83 行)與誠實界線(第 220 行)仍把子字串偏寬當成已知放行項。
   - Issue 自己的 DECISION(第 15 行)、症狀第 1 條(第 28 行)、REVISIT(第 47 行)還在說「第一條看 block 專案有沒有被誤擋再決定」。
4. 修前文件與程式一致,修後程式是整字、文件是子字串。實際影響只是文件比程式保守,而且 10-14 的 REVISIT 會讓人去量一個已經修掉的項目,所以判 minor。

## F2 回頭重讀帳「來源」欄的判斷條件,計劃仍寫只看 CI
severity: minor
blocking: 否
引句:「來源〔環境變數 `CI` 有值記 ci,否則 hook〕」
file: `docs/lumos-toolchain-knowledge/Projects/守檔筆記對照改動_計劃.md:90`
歸因:有證據的修復回歸

1. 202da1a4 在 `scripts/lumos:35383` 一帶把判斷收成 `_in_ci()`,只要 `CI` 或 `GITHUB_ACTIONS` 其一有設就記 ci(`scripts/lumos` 中 `_in_ci` 定義與 `src = "ci" if _in_ci() else "hook"`)。
2. 修前 `src = "ci" if os.environ.get("CI") else "hook"`,文件與程式一致。
3. 修後只設 `GITHUB_ACTIONS` 時帳記 ci,守檔計劃仍寫只看 `CI`。轉擋計劃第 42 行與 S25 已經寫對兩個變數,這一處漏改。

## F3 轉擋計劃〈設計〉沒寫「還沒提交」收窄成只算來源核對過的
severity: minor
blocking: 否
引句:「的那一步(`_note_reread_uncommitted`)一併改成」
file: `docs/lumos-toolchain-knowledge/Projects/舊句兩道轉擋_計劃.md:46`(「已對照」的共用口徑那條)
歸因:有證據的修復回歸

1. 計劃寫 `_note_reread_uncommitted` 改成「工作目錄有、頂端樹裡沒有這個檔名」就夠。
2. 真碼在 `scripts/lumos` 的 `_note_reread_uncommitted`,另外要求紀錄讀得懂、形狀對、`provenance_ok is True`,否則不算。測試 `t_reread_block_layer1` ⑦ 釘著這一點。
3. 筆記內容審那篇的修補寫對了(第 377 行),但設計規格本身沒同步。照計劃寫的重做實作,會把「來源核對沒過、還沒提交」的紀錄當成只差提交,等於重現 202da1a4 修掉的問題。

## F4 手冊禁止整個資料夾 add,工具自己的兩處提示仍印整個資料夾
severity: minor
blocking: 否
引句:「只列這一份,整個資料夾會夾帶殘檔與別的會談的紀錄」
file: `scripts/lumos:35035`(reread-prepare)、`scripts/lumos:35370`(reread-check 的 wip 提示)
歸因:有證據的原有漏查

1. 照 06 手冊第 5 步和守檔計劃修補後的句子做,是 `git add governance/reread-verdicts/<那一份>`。
2. reread-record 的提示確實只列具體檔名(`scripts/lumos:35158`)。但 prepare 與 check 在「還沒提交」時印的是 `git add governance/reread-verdicts && git commit`。
3. 這兩處在修前就是整個資料夾(f80352f6 的 35005、35334 行),修後沒動。
4. 照提示貼會夾帶殘檔或別的會談的紀錄,與手冊相反。

## F5 CHANGELOG 只寫「有舊句要處理 CI 會紅」,沒寫判不了在 CI 也紅
severity: minor
blocking: 否
引句:「CI 接了 `drift check` 的專案,升級後有舊句要處理的推送 CI 也會紅」
file: `.github/workflows/ci.yml:239-246`
歸因:有證據的原有漏查(修補補了一半)

1. 名稱消失檢查沒寫 `old_sentence` 時照總開關,預設是 block。
2. 判不了(時間到、git 讀不出、筆記讀不出、內部出錯)在 block 時回 1(條款 S6、S17),CI 那步遇到 rc=1 就 `exit 1`。計劃自己也寫「CI 永遠冷快取」。
3. 大型消費專案在 CI 冷快取下碰到 30 秒上限,升級後可能無舉證地紅。CHANGELOG 只提「有舊句要處理」。
4. ⚠ 我沒實測 CI 逾時,只依 ci.yml 的 rc 處理與 S6 的 block 回 1 推論,所以維持 minor。

## F6 README 中文縮得比程式窄,與英文版不一致
severity: minor
blocking: 否
引句:「Python 函式或指令旗標刪了、改名了,或程式檔刪了、搬走了」
file: `scripts/lumos`(`_drift_py_names(txt, m1=True)`,條款 S8:函式、類別、指派、旗標四個集合)
歸因:有證據的修復回歸

1. 英文版寫 Python definitions,涵蓋類別與模組層常數;中文版寫 Python 函式。
2. 真碼會追的是函式、類別、模組層與類別層指派、旗標。常數或類別改名也會被擋,中文讀者讀到「函式」會以為不會。
3. 修前中文是「函式刪了」,也偏窄;這次改寫仍沒寫準。

## 修補三問

1. **原問題有沒有真的改對?**
   - 有。逐條核過的對得上真碼:
     - 重讀預設 block 與 `--gate` 才擋(`_note_reread_rc`、`_note_reread_config`);
     - 判不了在 block 回 1,涵蓋 git 失敗、30 秒、紀錄讀不懂、起點算不出(`_NoteRereadStop` 各處);
     - `old_sentence` 沒寫照 gate、壞設定與壞 JSON 照 block(`_drift_old_sentence_config`);
     - gate=off 提示句(`scripts/lumos:39251`);
     - doctor 提示行(`_drift_old_sentence_doctor_lines`);
     - 回退節「設定讀到之前就失敗的照預設 block」與〈回傳碼與判不了〉相符;
     - `--kind reread` 在 `drift ack --help` 的選項裡;
     - 掛鉤帶 `--gate`、rc 128 以上交給 `pp_stop_if_signaled`(`scripts/hooks/pre-push:537-552`)。
   - 條款 S3、S14 與 `t_drift_m1_layers_and_mode`、`t_drift_m1_gate_off_wording` 現在的斷言一致,連 en dash 都對。
   - 轉擋計劃 S5-S8、S16-S19 與 `t_reread_block_layer1`、`t_reread_block_undecidable` 一致。
2. **有沒有把原本對的句子改錯?**
   - 沒有找到。「CI 的 reread 步驟不帶 `--gate`、恆回 0」「CHANGELOG v1.2 段的歷史句」都沒被誤改。
   - README 縮準那句本身沒錯,只是中文偏窄(F6)。
3. **新發現修前、修後各是什麼狀態?**
   - F1、F2、F3、F6:修前文件與程式一致或同樣偏窄,修後因程式或措辭改動出現落差,屬修補引入。
   - F4、F5:修前就在。F4 修後沒動;F5 這次補了一半。

## 圖譜鏡頭

逐條判過固定席節點,沒有與合約或宣稱的行為矛盾的:
- 存量漂移守衛:除 F1 的第 164 行外,第 84 行新 RULE 欄位齊(`[test:t_old_sentence_default_follows_gate]` 存在)。舊 RULE 已標 superseded 並帶 `[被取代:]`。`lumos lint` 對那條舊 RULE 仍有兩個警告(缺 `[依據:]`、retire 非機器式),在 main 上就有,屬原有。
- 筆記內容審:新 RULE 與 WHY 的 `[test:]` 都指到真測試。REVISIT 的 `[closed:…]` 理由沒放 `[[連結]]`。lint 0 問題。
- bound-tests-gate:第 34 行「五道閘…原本只有 drift 那道會停」沒補上重讀這道,但第 109 行已寫明,不矛盾。
- README圖產生器第 42 行與 README 一致。
- Issues/code-loop守衛main-direct盲區、每支檔有家、pitfalls-code-loop(★RISK★)、lumos-cli-read(★INVARIANT★ 的 search 排除 superseded)、guard-kill(兩條 ★INVARIANT★):這批改動沒碰它們宣稱的行為。
- 改過的 8 篇節點用 `lumos lint` 跑過,除上面那條舊 RULE 外都是 0 問題。

## 未驗範圍

- 沒跑全套測試,只讀了條款綁定的測試本體,並用 `--help` 與讀碼核對。
- CI 冷快取下名稱消失檢查的實際耗時沒實測(F5)。
- README 的 SVG 圖與替代文字不在這次修補差異內,沒逐字核。
- 兩份計劃的審計修正紀錄、`governance/review-reports/` 下的處置沒讀,依指示不讀上輪席報告。

最高為 minor。
