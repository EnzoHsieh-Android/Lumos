severity: minor

我逐 hunk 讀完整份補丁,並把修後版本(474346765)的 scripts/lumos 抽到暫存目錄,實跑了兩處函式(跳脫與擋下訊息)。除下面兩條 minor 外沒有 major。

## 發現

### 1. 擋下訊息在「護欄層加證據層同時擋」時,仍建議用例外放行
severity: minor
blocking: 否

引句:「        let.append("由使用者在核可鏈簽例外(最長 30 天,只蓋證據種類)")」

這條屬新引入的訊息邏輯,修前沒有這段,修前版本我沒跑。

- **失敗場景:** `blocking` 同時有 `[護欄] threat_categories_missing` 和 `[behavior] no_evidence`。
- **重現:** 在 `_cl_sec_block_lines` 傳入這份 rep(`gate_code` 為 None 與 `evaluation_error` 各跑一次),輸出的「接下來」都寫「真的要先放行,由使用者在核可鏈簽例外…或gate_setting 降成只提醒」。
- **為什麼不對:** 上面那行「在意的原因」剛說「例外蓋不掉這一層」。`let` 只看 `ev_kinds`,沒扣掉 `ctl_layer` 與不能被例外蓋的整道代碼,所以例外並不能讓這個推送過關。
- **次要:** 輸出裡「或」與「gate_setting」之間少一個空格。
- **歸因:** 有證據的修復新增。這段是本輪新寫的,未判定是否造成回歸。

### 2. 收據原始碼指紋比對假設收證的 cwd 就是 repo 根
severity: minor
blocking: 否

引句:「    pre = cwd.rstrip("/") + "/"」

- **做法:** 這是 `_secev_tq_rel` 的做法。`test_quality.py:316` 記的是 `path.resolve()` 的絕對路徑,`test_quality.py:331` 記的 cwd 是 `Path.cwd()`。
- **失敗場景(推論):** 如果在 monorepo 子目錄收證,例如 cwd 是 `/repo/sub`,快照路徑 `/repo/sub/src/a.py` 會被換算成 `src/a.py`。
- **後果:**
  - `_secev_tq_source_problems` 在提交樹找不到 `src/a.py`,誤判 `stale:receipt_source_changed`。
  - `_secev_tq_relevance` 拿 `src/a.py` 去比 bindings 的 `sub/src/a.py`,誤判 `invalid:fault_unrelated`。
- **未能重現:** 我沒有造出子目錄收證的資料,嚴重度已自降。
- **歸因:** 未判定,缺修前證據。這兩段都是本輪新增,修前版本沒有這個檢查。

## 資料狀態五問(有核對到的部分)

- **新舊格式互讀:**
  - `_secev_exception_shape` 讓閘門與 `security approvals` payload 共用同一支。v1 形狀(沒有 `covers_kinds`、也沒有 `compensating`)在兩邊都得到 `exception_unapproved`。
  - 非 dict 的 `exception` 得到 `exception_fields_missing`。
  - `_secapr_c_exception` 改成先驗形狀再 `sorted(covers_kinds)`,原本壞值會丟 `TypeError`,這個崩潰路徑已封掉。
- **寫一半:**
  - `_jsonl_append_line_verified` 改成 `"ab"` 位元組寫入,寫前檔尾沒換行會補、讀回只讀新寫的那段,三者仍一致。
  - `_secev_append_target` 在建資料夾前後各查一次符號連結。
  - 核可鏈的追加入口另有一次前置檢查,擋住符號連結或跑出 repo 的路徑。
  - 這個前置檢查的 `bad[1].relative_to(root)` 不會拋錯,因為 `_repo_path_unsafe` 回的是 `root / rel` 的 Path。
  - 背書指令在「已有一筆就不重寫」時也會先建資料夾,但 `docs/` 本來就在,無害。
- **衍生資料:** `_secinv_show` 逐行再過一次是冪等的。我用 ESC、換行、tab、零寬字、`\x1b` 字面反斜線、框線字元實測,二次輸出與一次輸出完全相同。`_secev_render` 與 `_secinv_render` 的行元素裡沒有刻意內嵌的換行,改成 `_secinv_lines_text` 不會把多行元素壓成一行。
- **時間:** `_secev_iso` 現在在讀進來就判掉換到 UTC 會溢位的極端值(`OverflowError`),並且先檢查 `tzinfo is None`,邏輯與修前等價且更早判。
- **不可逆(只追加帳本):** `_secev_mainline_override` 把「git 失敗、逾時、檔過大」與「真的沒有這支檔」分開,前三者回 `mainline_unknown`。`_nodehome_cat_sizes` 對缺檔回 `None`,所以「沒設」的路徑成立。`_secev_main_side_trace` 在認不出主線時改看所有候選 ref,否則 force push 退版刪光圍欄會被當成 `no_registration` 放行;無痕跡時的結果與修前相同。

## 三問回答

1. **原問題的修復效果有何行為證據:**
   - 跳脫、非法 `exception` 形狀、`mainline_unknown`、符號連結追加,這幾組我只靠讀碼與上面兩個小實驗(跳脫冪等、擋下訊息)驗證邏輯。
   - 我沒跑 `t_*` 測試,測試通過與否未判定。
   - 兩條新增的 tq 檢查(原始碼指紋、故障相關性)沒有做端到端實跑,只讀碼。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立:**
   - `_SecevTree` 的 `deadline` 是選填,`_secapr_cmd_verify` 等不帶 `deadline` 的舊呼叫仍可用。
   - `_nodehome_list` 新增的 `modes` 只填非一般檔,`tree.modes.get(p) == "120000"` 與舊的逐檔 `ls-tree` 判法等價。
   - `_SecevDataError` 在生產碼只有定義和 `except`,沒有任何 `raise`,只有測試用 monkeypatch 丟過。
   - 各讀法目前靠形狀檢查回代碼(例如 `_secev_sarif_shape`),所以沒有現成的失敗輸入。
   - 但這道 except 目前不會觸發,docstring「讀進來那一層丟」與實況不符。之後新增讀法若直接丟 `TypeError`,會變成整道 `evaluation_error`,而不是單項 `report_malformed`。
3. **新發現的同一案例在修前、修後各是什麼結果:**
   - 兩條 finding 都是本輪新增的程式碼,我沒有跑修前版本。
   - 兩條都標未判定,不下「回歸」結論。

最嚴重 severity:minor,blocking 共 0 條。
