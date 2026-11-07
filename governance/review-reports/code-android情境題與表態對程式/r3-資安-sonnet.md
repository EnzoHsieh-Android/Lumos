severity: minor

已看三類。①提示注入:無發現。②讀寫與執行越界:F1(minor)。③非刻意一步繞過的守衛:無發現。

## F1 `_home_cache_evict` 刪檔前不驗目錄可不可信
severity: minor
blocking: 否

引句:「        _home_cache_evict(_kt_sit_cache_path(key).parent, _KT_SIT_CACHE_TTL)   # 寫之前清掉過期的(代碼審 r2 通才 F2、資源 F1)」

- **刪檔範圍本身是安全的。**
  - 目錄是固定的 `~/.cache/lumos/kt-situation/`,不含被掃 repo 能控制的字串。
  - 檔名只列目錄一層,不拼路徑。
  - `key` 是 sha256 十六進位,穿越字元進不來。
  - 迴圈裡有 `is_file() and not is_symlink()`,所以目錄裡的捷徑不會被跟著刪。
- **缺口在目錄本身。**
  - 新函式 `_home_cache_evict` 在 `_home_cache_write` 的 `_mkdir_trusted_under_home` 與 `_trusted_private_dir` 之前就被呼叫,evict 自己不做這道檢查。
  - 對照舊的 `_drift_m1_cache_dir`,它先過 `_trusted_private_dir` 才回目錄,不可信就回 None,所以「不可信不寫也不刪」。
  - 重構前,不可信的目錄對 evict 是 None。重構後,`kt-situation` 這條路徑的 evict 沒了這道前置檢查。
- **攻擊路徑四件:**
  - 誰:能在使用者家目錄放東西的另一個程序或另一次操作,與使用者本人同權限。
  - 從哪:把 `~/.cache/lumos/kt-situation` 換成指向別處目錄的符號連結。
  - 送什麼:使用者下一次跑 `pitfalls --diff` 或推送前閘。
  - 拿到什麼:evict 會 `iterdir` 跟進連結目標,刪掉裡面超過 24 小時的一般檔,沒檢查擁有者、也沒限 `.json`。
- **為什麼只標 minor。**
  - 要先植入符號連結,是刻意多步操作。
  - 單人電腦上,能植入的人本來就能直接刪那些檔。
  - 它退掉了 2026-09-06 全 repo 審視 #6「寫入端也要驗目錄」的同一道防線,屬縱深防禦的退步。
- **建議修法**(不是必修):`_home_cache_evict` 開頭加 `_trusted_private_dir(d, ".cache", "lumos", <子目錄>)`,不過就直接 return。

## 已看且無發現
- **提示注入:**
  - 進問題句、提醒的檔名,都先過 `_kill_esc` 才印。
  - 印出的放行指令用 `shlex.quote` 組(`_lint_waive_cmd`),檔名帶空白、引號或 `$()` 也不會變成指令注入。
  - 證據提醒印的是型錄的標準寫法與證據樣式,來自工具鏈型錄,不含被掃 repo 的 Kotlin 原文。
  - 段身分是內容雜湊。
- **借用 check.py 的載入位置:**
  - `_kt_toolchain_root()` 找的是這支 lumos 旁邊那份,或 `_lumos_src()`,不是被掃 repo。被審分支改不了讀表程式。
  - `LUMOS_KT_CATALOG` 只在 `TMPDIR` 名稱以 `gctl-run-` 開頭時才採用。要先偽造 `TMPDIR` 才能換型錄,屬刻意多步,最多 minor,這裡不另立條。
- **證據樣式降成提醒後,有沒有一步讓缺段缺列也只剩提醒:**
  - 沒有。缺段、缺列、答案形狀不對、evidence 不在段範圍,在 `_kt_sit_row_verdict` 與 `_kt_sit_check` 裡仍是 `block`。
  - 只有 `evidence` 種類進 `reminders`。
  - 段放行(`waived`)只略過 `evidence` 提醒,缺段缺列照擋,放行檔讀不了判無法驗證。
- **段放行指紋撞段:** 指紋是 `kt-situation:` 加段身分,段身分綁段材料內容,所以改碼會換身分。我沒看到一步就能撞到別段的路徑。
- **環境不可用被平常情況觸發把整題關掉:**
  - `_KT_DT_MISSING` 只在型錄或 check.py 檔不存在時成立。
  - 檔在但讀表失敗走 `block`。
  - 唯一的平常情況觸發點是消費專案裡 `LUMOS_HOME` 或 `~/harness/lumos-toolchain` 找不到。
  - 這種情況是明寫的設計,而且會印提醒並記 fail-open 帳,不是靜默。

總結:最嚴重是 F1(快取清理不驗目錄可不可信,minor 縱深防禦退步),會擋 0 條。
