severity: major

審查範圍是 `scripts/lumos` 的 `_e2e_gate_*`、`_e2e_waive_*`、`_e2e_record_*`、`_codeloop_e2e_step` 與訊息函式。我逐 hunk 讀完整份 diff 和修補差異,並用 `scripts/test_lumos.py` 的測試輔助函式在暫存 repo 重現。對照版本是修前 `0aecbf90` 的 `scripts/lumos`,我另存一份跑同一支腳本。`-k android_e2e_gate` 85 項全綠,所以下面幾條都是測試沒抓到的。

關於派工詞提到的 `.warming` 鎖:檔內是 PID 97317 與兩行雜湊,我沒有動它,照派工詞審查。

## Findings

### 1. 修補後,主線有 e2e 段時,舊分支(分岔點與被推送提交都沒有 e2e 段)只改文件也被擋,而且訊息說錯

severity: major
blocking: 是
file: `scripts/lumos:41613`、`scripts/lumos:41618`
引句:「    if fp == fp_base and same_cfg:」

- **失敗場景**:
  - 分支在 e2e 導入前切出,分岔點的 `macrobench.json` 沒有 e2e 段,被推送提交也沒有。
  - 主線後來加了 e2e 段,這次推送只改 `README.md`。
  - 兩端指紋相同,但 `same_cfg` 要求 `isinstance(pushed[1], dict)`,被推送提交沒有 e2e 段就恆為假。
  - 於是不走「不要求」,落到 `if not pushed[1]:`,印「App 程式卻跟分岔點不一樣」。這句不實,因為 App 沒動。
- **對照計劃**:S8 寫「兩端指紋相同→不要求」,這裡違反。S36 只規範「被推送提交沒有 e2e 段而主線有」時擋下訊息要說先合主線,範例是 App 有改的情況。
- **為何測試沒抓到**:`t_android_e2e_gate_missing_side` 只測 App 有改的那一種。
- **重現**:
  ```
  python3.14 /tmp/lumos-seat-work/code-e2e-gate/正確性-sonnet/repro1.py before|after
  ```
  (分岔點拿掉 e2e、主線再加回、分支只改 `README.md`;重現腳本已隨暫存目錄刪除,步驟即上述三句)
  ```
  before 0 not-required App 程式與驗收素材跟分岔點一樣
  after  1 blocked 這個提交沒有 e2e 段,App 程式卻跟分岔點不一樣:先把主線合進來再驗收;...
  ```
- **歸因:有證據的修復回歸。** 修前是 `if fp == fp_base:` 直接放行,修後多了 `same_cfg`(用來補「拿掉 e2e 段沒人驗」)。這次修補後,被推送提交沒有 e2e 段的路徑只剩擋下,不會放行。
- **修法方向**:兩端都沒有 e2e 段且指紋相同時,視同 `same_cfg` 成立。

### 2. 「拿掉 e2e 段」被擋後,第一條「接下來」指令照做解不開,「在意的原因」也講錯

severity: minor
blocking: 否
file: `scripts/lumos:66774`、`scripts/lumos:41614-41617`
引句:「git merge <主線>   # 或 rebase 到主線;合進來之後這一版才有 e2e 段、驗收與放行才算得出指紋」

- **失敗場景**:
  - 分支刪掉整段 e2e,App 沒動,分岔點有 e2e 段,於是設了 `merge_main=True`。
  - `_cl_say_e2e_block` 在「接下來」第一行叫人 `git merge <主線>`。
  - 實測 merge 完還是同一個擋下:3-way merge 保留分支的刪除,分岔點仍有 e2e 段。
  - 「在意的原因」那句固定文字也說「App 程式或驗收素材跟主線分岔點不一樣」,在這個情境不成立。
  - 真正解法只有 `LUMOS_SKIP_ANDROID_E2E=1`,訊息最後一行有印,所以降為 minor。
- **重現**(repro2,已隨暫存目錄刪除;步驟:刪掉整段 e2e、讓主線前進、feat 合併 main):
  ```
  after REMOVE e2e: 1 blocked 這個提交拿掉了 e2e 段(分岔點還有)...
  接下來:
      git merge <主線>   # 或 rebase 到主線;...
  after after merge main: 1 blocked 這個提交拿掉了 e2e 段(分岔點還有)...
  ```
- **歸因:有證據的修復回歸。** 修前同一輸入是 `not-required`(漏洞),修補加了這個擋下,但沿用 S36 那個 `merge_main` 提示。

### 3. 紀錄在提交裡讀不懂時,擋下訊息印的兩條指令都解不開

severity: minor
blocking: 否
file: `scripts/lumos:41637`、`scripts/lumos:66785`
引句:「    rerr = _e2e_record_err(rec, fp) or _e2e_gate_times_err(rec)」

- **失敗場景一**:紀錄的 `runs.result` 不認得(或 schema 比這版新)。
  - 訊息印了 `--case login.ok` 重跑和 `waive <fp>` 兩條指令。
  - `_e2e_record_update` 對讀不懂的紀錄一律不寫。實測 `waive` 回 rc 2:「讀不懂(...);先看過再決定刪掉或修好,這次不寫」。重跑一樣不會覆蓋。
  - 擋下原因那行沒講要手動修或刪。
- **失敗場景二**:紀錄有算數的放行,但某筆 `feature_runs.ended` 沒帶時差。`_e2e_gate_load` 先擋,放行寫得進去,但重跑判定還是「讀不懂」。這與 S10「結束時間讀不懂就擋」一致,只是 waive 提示無用。
- **重現**:repro4 與 repro3(iii),已隨暫存目錄刪除;步驟:committed 紀錄放壞的 `runs.result`、跑 `check` 與 `waive`;另放帶放行但 `ended` 沒時差的紀錄。修前修後輸出相同:
  ```
  waive rc 2 擋下:...讀不懂(runs.result 不是 pass、fail、unjudged 之一);先看過再決定刪掉或修好,這次不寫
  (iii) waived + naive ended: 1 blocked 查證紀錄讀不懂:按功能結果 login.ok 的結束時間(ended)讀不懂
  ```
- **歸因:有證據的原有漏查。** 兩版結果一樣。

## 沒找到問題的部分

- 判定順序(出口→放行→整套→按功能)與計劃〈推送前怎麼按功能判〉第 1 到 6 步一致。
- `newer` 與 `rt >=` 用帶時差的 `datetime` 比,同一秒算較新,和 S30 一致。
- `ended` 沒帶時差、不是字串或 `fromisoformat` 失敗,都回 None 並擋下,沒有放行路徑。
- `_confirm_tty_timeout` 負數、NaN、無限大改用預設,第 ① 階 EOF 會落到第 ② 階,Ctrl-C 也有處理。
- `waive` 寫到一半:`_write_lf` 是暫存檔加 `os.replace`,不會留半份。`--ack` 逐份寫,第二份失敗時第一份已寫入,重跑是冪等的。
- 同一指紋多筆放行用 `any()`,取哪一筆不影響結果。

## 角色鏡頭

- **be-api-compat**:不影響。
  - `android_e2e` 只在 `status != none` 且 `--json` 時加進 `code-loop` 的輸出,是新增欄位。
  - 修補把 `code` 從 `timeout`/`internal` 改成 `evaluation_timeout`/`evaluation_error`。這個功能還沒進主線,沒有舊呼叫端,pre-push 的原因表也已新增 `android_e2e`。
- **be-authz**:不影響。這是 CLI,沒有端點。
  - `waive` 在沒有互動終端時記成 AI 放行,gate 立即放行,事後靠三處通知要人看。這是計劃設計。
  - `--commit` 與 `who` 沒驗證,屬計劃設計與單人威脅模型。
  - `--ack` 要終端答 y。

## 三問

1. **原問題的修復效果**:
   - 「只改設定、拿掉 e2e 段也放行」:修前 `not-required`,修後 `blocked`。把 flow 與功能拿掉的設定弱化同樣如此。
   - 「環境變數出口排在讀設定之後」:`macrobench.json` 壞掉加 `LUMOS_SKIP_ANDROID_E2E=1`,修前仍 `blocked`,修後 `skipped-env`。
   - 這兩項都有行為證據;各項修補在腳本層仍成立。
   - 但「拿掉 e2e 段」那個修補同時帶來上面的 1 和 2。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:
   - 正常路徑與有 e2e 段的路徑都成立。
   - 相鄰路徑「被推送提交沒有 e2e 段」出了回歸(第 1 條)。修補後這條路只剩擋下,放行已不可能。
3. **新發現的同一案例在修前、修後各是什麼結果**:
   - 第 1 條:修前 `not-required`,修後 `blocked`,屬回歸。
   - 第 2 條:修前 `not-required`(漏洞),修後 `blocked`(訊息不實),屬回歸。
   - 第 3 條:修前修後都是 `blocked`,屬原有漏查。

最高等級 major,擋實作的 1 條(第 1 條)。

我的暫存目錄已刪;repro 腳本隨目錄一起刪除,上面各條已寫出重現步驟與輸出。
