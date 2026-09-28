severity: clean

## 已看,無 finding — 逐類記錄

1. **不可信輸入流到危險操作(命令、路徑、git 選項注入、cat-file --batch、設定檔讀取的捷徑防護)**

   - `_git_log_sha_paths`/`_note_status_seq`/`_note_base_status` 這次重構出的三支函式,組出的 `cat-file --batch` spec(`f"{s}:{q}"`)裡 `s` 一律先過 `_LENS_SHA_RE.fullmatch` 驗成完整 SHA,`q` 是 git 自己印出的路徑;真正餵進 subprocess 的地方 `_nodehome_cat_blobs` 沒有被這份 diff 改動,換行注入的防護(`if any("\n" in s_ for s_ in specs): return None`)還在,batch 走的是 stdin 逐行給 object id,不是 shell 指令列,不受選項注入影響。
     引句:「specs = [f"{s}:{q}" for s, q in pairs]」
     file: `scripts/lumos:24529`(`_note_status_seq` 組 spec)
   - 新增的批次讀失敗處理是這輪修正本身,不是引入的洞:改之前批次讀失敗會被吃成「沒有狀態翻轉」(等於讓轉正卻沒清預告句的推送靜默放行),現在失敗一律回 `None` 往上傳,`_drift_check_core` 把判不了算進 `unknown`、`cmd_drift_check` 在 `unknown` 非空時一樣視為要處理(fail-closed)。
     引句:「批次讀失敗回「算不出」(原本當成沒有狀態翻轉)」
     file: `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:63`
     file: `scripts/lumos:25671`(`for u in unknown: print(...) `,判不了一樣印「擋下」/記帳,不放行)
   - `.lumos/config.json` 讀取這次在 `_drift_gate_doctor_lines` 補上「整條路徑都要看」(`.lumos` 資料夾本身是捷徑也不跟),跟同檔案裡既有的 `_note_shape_doctor_lines`(24254)、`_nodehome_config`(22531-22533)、`_note_audit_doctor_lines`(26168)是同一套寫法,是收斂既有防護、沒有引入新缺口。
     引句:「if cp.is_file() and not cp.is_symlink() and cp.resolve() == root.resolve() / ".lumos" / "config.json":」
     file: `scripts/lumos:25768`
   - 這道閘實際生效值(是否 block)讀的是 `_nodehome_reader(root, tip)(".lumos/config.json")`(從被推送的樹讀 blob,不走檔案系統),不受符號連結影響;`_drift_gate_doctor_lines` 那段只是 doctor 的提醒文字,不是判定路徑。
     引句:「mode, warns = _drift_config(_nodehome_reader(root, tip)(".lumos/config.json"))」
     file: `scripts/lumos:25645`
   - 已知且在筆記裡明寫承認的風險(推的人能在同一個提交把 `drift_check.gate` 改成 `off` 放過自己)是設計層級接受的疏忽防線、非存心繞過防線,筆記已有 RULE 記載和撤除條件,這份 diff 沒有讓它變得更糟或新增別的繞過路。
     引句:「推的人可以在同一個提交把 drift_check.gate 改成 off 放過自己」
     file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:15`

2. **登入與權限**:已看,無。這批改動不涉任何認證/授權/角色判斷邏輯,純粹是本機圖譜狀態一致性檢查與 CLI 輸出。

3. **密鑰與個資**:已看,無。新增/改動的程式與測試沒有讀寫任何憑證、token、個資欄位;測試裡的 `t_refund`、`Systems/Pay.md` 等只是合成測試資料,不是真實密鑰或個資。

4. **加密與傳輸**:已看,無。全程只有本機 `git` 子行程呼叫(`-C <repo>`),沒有新增網路呼叫或憑證處理。

5. **執行邊界**:已看,無。`subprocess` 呼叫維持既有的「參數列表、不用 shell=True」慣例(`_nodehome_cat_blobs` 用 `_sp.run(["git", "-C", ...], input=..., capture_output=True, timeout=timeout)`),這份 diff 只加了 `timeout` 參數的傳遞,沒有改成字串拼接或 `shell=True`;測試檔新增的 `t_drift_code_review_r2_regressions` 全程操作合成 vault/repo,沒有引入新的反序列化(無 `pickle`/`eval`/`exec`)。

6. **行動端**:已看,無。這份 diff 不涉任何行動端程式碼。

**新依賴**:已看,無。這輪只多了標準庫 `import time as _t`(在既有函式內、範圍已縮小);測試檔頂端多 import 的 `pathlib, types, contextlib, io, json as _j` 皆為標準庫,`types`/`contextlib`/`io`/`_j` 在新增的 `t_drift_code_review_r2_regressions` 裡似乎沒被用到(至多是未用 import 的整潔問題,沒有攻擊路徑,不夠 minor 門檻,不報)。

## 總結

整份 diff 沒有發現可利用的安全問題,最高等級 clean,blocking 0 條。
