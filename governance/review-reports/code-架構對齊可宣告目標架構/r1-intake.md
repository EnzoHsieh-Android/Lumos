# r1 intake(代碼審)

## 收貨
- 兩席:單reviewer-sonnet(8 條)、架構對齊-sonnet(7 條)。
- report-normalize:架構對齊席清單式嚴重度用 --write 純格式搬移;單reviewer 末行總結請該席自己改寫成「總結最嚴重 severity:」後重存(未記帳前覆蓋)。
- quote-check(對 r1-snapshot.patch):兩份全數錨定。refcheck:引的 file:line 全存在。

## 編排者機械重現(先寫紅測試,修前紅、修後綠)

| finding | 重現 | 修前 | 修後 |
|---|---|---|---|
| COR-1 | t_arch_target_lens_trusts_mainline_base_only ②:範圍 <分支提交>..<分支提交> 附了分支寫的寬規則 | HIT 紅 | 綠 |
| COR-2 | t_arch_target_control_chars_never_reach_prompt ①②:含換行檔名在目標段另起一行;node 含換行被收 | HIT 紅 | 綠 |
| COR-3 | _lint_new_verdict 69ac44b2..fd2bd3ec → blocked 3 條(DTZ011、C901×2) | HIT | 69ac44b2..2cb3e330 → clean |
| COR-4 | t_arch_target_same_files_as_lens:分級回 ['app/Domain/my file.py\t','app/Domain/my notes.md\t'] | HIT 紅 | 綠 |
| COR-5 | 同 COR-1 測試 ①:現行碼本來就讀起點版(綠),變異改讀終點版 → 翻紅 | 缺口 HIT | 守住 |
| COR-6 | S7 反例斷言:變異「每篇都判沒規則」→ 翻紅(要 doctor --verbose,軟段預設只顯示 3 條) | 缺口 HIT | 守住 |
| COR-7 | t_arch_target_failure_not_silent ①②:git 失敗回 ([],[])、例外回 '' | HIT 紅 | 綠 |
| COR-8 | t_arch_target_config_reader_cases ①:沒宣告、設定壞掉多出 warnings | HIT 紅 | 綠 |
| ARC-1 | t_arch_target_rules_shared_parser:大寫 SUPERSEDED 照附、單行 summary 認不得 | HIT 紅 | 綠 |
| ARC-2 | t_arch_target_config_reader_cases ②:改走 _json_at_ref(strict) 後非 UTF-8 照警告;路徑檢查與 review_roles 共用 _config_glob_error | HIT | 綠 |
| ARC-3 | 讀碼:_arch_target_vault_rel 改用 _vault_slug_of 辨認 | 讀碼 HIT | 已改 |
| ARC-4 | 同 COR-4:分級與鏡頭共用 _arch_target_changed_files | HIT | 綠 |
| ARC-5 | 讀碼:新碼 8 處 unicodedata.normalize 改用 nfc() | 讀碼 HIT | 已改 |
| ARC-6 | 讀碼:掛鉤 _role_text 改名 _extra_text | 讀碼 HIT | 已改 |
| ARC-7 | 讀碼:doctor 宣告清單改用 ok() | 讀碼 HIT | 已改 |

所有變異(九處)都讓對應測試翻紅,已還原。

## 同族掃描
- COR-1 同形狀:派工鏡頭角色段也讀範圍起點版 review_roles、沒檢查起點在主線。角色鏡頭計劃的驗收條款明文決定「base 不在主線時角色卡照附」,這次不擅改,開 Issues/角色鏡頭在起點不在主線時讀分支宣告。
- COR-1、COR-2 是設計審該看出的洞,已記兩筆設計迴圈逃逸。

## 處置
15 條全數折入,無放行、無駁回。
