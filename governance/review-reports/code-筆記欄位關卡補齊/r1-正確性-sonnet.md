severity: blocker

## F1 standalone vault(圖譜即 repo 根)下 note_lint.gate 一律被讀成 warn,設定形同虛設

severity: blocker
blocking: yes

`_note_lint_config` 在 `lumos lint`(cmd_lint)與健檢 L 段兩處都是用 `_repo_root_from_env(env)` 去找 `.lumos/config.json`:

引句:「    _nl_mode, _nl_cfgw = _note_lint_config(_repo_root_from_env(env))」
引句:「    mode, cfg_warns = _note_lint_config(_repo_root_from_env(env))」

`_repo_root_from_env` 對「圖譜本身就是 repo 根」(standalone vault,例如核心 repo:MOC/+Systems/ 直接在 repo 根,`.git` 就在 vault 資料夾裡)這種佈局,算出來的 repo root 是 `env.vault.parent`——比真正的 repo 根多跳一層、跑到 repo 外面去了。這正是 `scripts/lumos:2765`~`scripts/lumos:2766` 那行既有註解點名過的坑(「_repo_root_from_env→standalone 回 parent 與既有定義互斥」),當初 `_lint_load_and_validate`(`scripts/lumos:2770`)、`_nodehome_config`(`scripts/lumos:995`)都因此改用 `_vault_repo_root`(`scripts/lumos:7425`,會往上找 `.git`,對 standalone vault 抓的是 vault 自己)。這次新開的 `_note_lint_config` 沒有沿用那個修法,兩個呼叫點都用回 `_repo_root_from_env`,同一種坑重新長出來。

後果:standalone vault 專案的 `.lumos/config.json`(放在 vault 根、也就是 repo 根)永遠找不到,`note_lint.gate` 不管設 `on`/`off` 都讀不到,一律 fail-open 成預設值 `warn`——這不是「未設定當 warn」的設計行為,是「設定檔根本沒讀到」的誤判,而且訊息還會照樣印「專案開關 note_lint.gate 是 warn」誤導使用者以為自己沒設對。

翻紅重現(standalone vault,`.git` 與 `.lumos/config.json` 都在 vault 根,明寫 `gate: "on"`):
```
mkdir -p /tmp/standalone_repro/{Systems,Verification,Projects,MOC,.lumos}
cd /tmp/standalone_repro && git init -q
echo '{"note_lint": {"gate": "on"}}' > .lumos/config.json
cat > MOC/idx.md <<'EOF'
---
type: moc
---
# idx
EOF
cat > Systems/沒狀態.md <<'EOF'
---
type: system
created: 2026-09-26
updated: 2026-09-26
aliases: []
tags:
  - type/system
summary: |-
  KEY:x
---
# 沒狀態
EOF
python3 <repo>/scripts/lumos --vault /tmp/standalone_repro lint 沒狀態
```
實際輸出(已跑過):`⚠ 沒填 status(…)(專案開關 note_lint.gate 是 warn,先提醒不擋)` / `0 error / 1 warning` / `rc=0`——明明設定檔寫的是 `on`,理應是 error 擋下(rc1)。`doctor --ci` 同一個 vault 也是同樣結果:L 段把「壞型別」(舊規則)跟「沒填 status」(新規則)都降成 warn_soft,doctor 仍 rc0,不擋推送。

用 `_vault_repo_root(env)` 去讀同一個 vault 能拿到正確結果:
```
_repo_root_from_env: /tmp   (跳出 repo,錯)
_vault_repo_root:    /tmp/standalone_repro   (對)
_note_lint_config(_repo_root_from_env(...)) → ('warn', [])   # 錯,應為 on
_note_lint_config(_vault_repo_root(...))    → ('on', [])     # 對
```

作者測試沒抓到這個洞,是因為 `_nl_vault`/`mkvault()`(`scripts/test_lumos.py` 的 `_nl_vault`)造的測試圖譜從不在 vault 資料夾裡建 `.git`,所以 `_repo_root_from_env` 與 `_vault_repo_root` 在測試裡永遠算出同一個目錄,兩個函式的差異被測試環境遮住了。本 repo 自己(docs/lumos-toolchain-knowledge 佈局)也不受影響,因為它不是 standalone vault、兩個函式在這裡也剛好算出同一個根——所以這批「本 repo 558 篇零違規」的驗收沒有暴露這個問題。

影響範圍:任何用 standalone vault 佈局的消費專案(`scripts/lumos:17637` 一帶明文提到「或 d 本身就是 vault root(standalone,如核心 repo)」,是既有支援的佈局),設 `note_lint.gate: on` 一律不會真的擋,`lumos lint` 與 `lumos doctor --ci`(pre-push 閘走的就是它)都會誤判成 warn,静默失去這整批新規則要達成的「推送前擋下」效果。

## 其他已驗過、沒問題的路徑

跑過作者自帶的 17 支相關測試(`t_lint_status_required`、`t_lint_date_fields_format`、`t_lint_decision_valid_boolean`、`t_lint_about_code_must_exist`、`t_lint_plan_requires_lands_in`、`t_note_lint_gate_default_warns`、`t_doctor_note_lint_gate_on_blocks`、`t_note_lint_gate_off`、`t_note_lint_gate_bad_config`、`t_doctor_note_lint_ignores_touched_list`、`t_note_lint_gate_does_not_relax_existing_rules`、`t_set_responsibility_min_length`、`t_about_code_writer_rejects_vault_path`、`t_repo_graph_passes_note_lint`),全數通過,不是假綠(在乾淨 clone 上實跑,不是讀報告)。

五條新規則(status 必填、日期格式含真日期、decisions valid 只認 true/false、about_code 存在且不在圖譜資料夾、計劃 lands_in)在「repo_root 算對」的前提下(本 repo 本身佈局、以及非 standalone 的 docs/<name>-knowledge 佈局消費專案)邏輯本身沒找到反例。

`lumos lint` 的「開關只管新規則、原有規則不受影響」這條也驗過對:

引句:「    if mode != "off":」

這行前面 `errs, warns = _lint_collect(env, rel)` 已經把舊規則錯誤裝進 `errs`,不受 mode 分支影響,只有 `new = _lint_new_rules(env, rel)` 這批才照 mode 走(前提同樣是 `_note_lint_config` 的 repo_root 要算對;F1 講的是 repo_root 算錯導致連 mode 本身都讀錯,不是這段邏輯本身有洞)。

`set responsibility` 與 `append/new --code` 對 about_code 寫入端的擋法也驗過對(用作者測試 t_set_responsibility_min_length、t_about_code_writer_rejects_vault_path 實跑通過,且看過原始碼 `_about_code_path` 用的是 `_vault_repo_root`,不是 `_repo_root_from_env`,不受 F1 影響):

引句:「        return None, f"「{v}」在圖譜資料夾裡,是筆記不是程式檔——要連結別篇就寫進 related"」

健檢 L 段「不讀碰到清單」也照 `t_doctor_note_lint_ignores_touched_list` 驗過:帶 `--touched-from` 的清單不影響 L 段擴充範圍,結果與不帶清單一致。
