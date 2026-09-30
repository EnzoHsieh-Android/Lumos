severity: major

## F1 第 8 週結算時，最後 14 天的提醒尚未完成追蹤

severity: major
blocking: 是
引句:「上線第 8 週量四條,**全部**成立、而且每一條都達到最小樣本」
file: `governance/review-reports/否定現況句配回頭條件/r3-snapshot.md:170`

1. 窗口涵蓋上線後 8 週，但 `followup` 要逐筆觀察 14 天。第 55 天出現的提醒，要到第 69 天才能判成①至⑤；第 56 天結算時只能看到一天。
2. 因此第 8 週無法完整計算照做率，也無法取得最後兩週新增的條件式 REVISIT 母體。spec 沒定義右設限、排除最後 14 天或延至第 10 週，四條門檻照字面算不完。
3. 未能重現：唯讀沙盒拒絕建立規則要求的臨時 clone；此項由時間軸直接推得。

## F2 被 amend 掉的原文沒有可供準度複判的版本

severity: major
blocking: 是
引句:「抽法:隨機抽 30 筆,讀 `excerpt`(片段不夠判時,到提醒時的那一版或主線找原行)」
file: `scripts/lumos:1210`

1. 提交前寫帳時，`_gate_event` 記錄的是當下 `HEAD`，也就是尚未包含 staged 新行的上一版；帳內只保存 60 字片段與文字雜湊。
2. 若作者看到提醒後 amend、壓提交或根本未推送，原行從未存在於主線，記錄的 `head_sha` 也沒有它。片段不足時，所謂「提醒時的那一版」無從取得。
3. 這正是新帳要補救的主要樣本，但 spec 沒定義無法判讀、重抽或保存原文的方法；隨機 30 筆只要抽中一筆此形狀，準度門檻便沒有完整分母。
4. 未能重現：臨時 clone 無法建立；程式碼已確認 `head_sha` 的來源。

## F3 噪音分子會把失敗的 commit attempt 算成提交

severity: major
blocking: 是
引句:「分子:帳上窗口內的 `hinted` 事件數;分母:主線上窗口內改到圖譜的非合併提交數,≥ 30」
file: `scripts/hooks/pre-commit:230`

1. note-shape 在 Git pre-commit 執行。S4 又要求同時有 blocking 違規與否定提醒時，先寫 `blocked`、再寫 `hinted`，最後回 1；該次根本不會產生提交。
2. 使用者每修一次再重試，都可能新增一筆 `hinted`，且 `head_sha` 仍相同。做法只對單行提醒以 `(path, line_sha)` 去重，噪音分子卻直接數事件，沒有 commit-attempt 去重規則。
3. 因此分子是「包含失敗重試的掛鉤執行次數」，分母才是主線提交數；35% 門檻與歷史重放的提交比例不同口徑，可能因其他 blocking 問題被任意推高。
4. 未能重現：臨時 clone 無法建立；hook 與 S4 的控制流程已逐段核對。

## 其餘段落

其餘各節已讀，無 finding。`Systems/筆記內容閘` 沒有登記額外合約可消解上述三項。

最高等級:major;blocking 共 3 條