severity: major

## F1 decisions 的 decided/ended 空字串仍繞過日期規則,跟 PITFALL 宣稱的「一律報錯」不符

severity: major
blocking: yes

這次 patch 對「日期寫了卻是空的」只修了 `_lint_new_rules` 裡管 `created`/`updated`/`date`(`_NOTE_DATE_FIELDS`)的那段迴圈,新增了 `k in n.fields and (v is None or str(v).strip() == "")` 的專門分支去攔空字串。但同一支函式底下管 `decisions` 陣列的 `decided`/`ended` 迴圈完全沒有改,還是原本 `v is not None and str(v).strip() != "" and not _note_date_ok(str(v))` 的寫法——`decided: ""`(引號包住的空字串)會讓 `str(v).strip() != ""` 為假,整條判斷短路,不會報任何錯。

引句:「寫了欄位卻是空的(含引號包住的空字串):會同時繞過日期規則與既有的建立日切點(代碼審 r1 外家兩席)」

這行註解與同段 PITFALL 摘要(`③★日期寫成空字串會繞過日期規則與既有建立日切點★,寫了卻空一律報錯`)都在講「日期規則」整體,且 RULE 行明講新規則涵蓋「日期年-月-日且是真日期(含決策 decided/ended)」,讀起來像是這次連 decisions 的 decided/ended 空字串也一併堵住了,但實際只堵了頂層三個日期欄位。

引句:「if v is not None and str(v).strip() != "" and not _note_date_ok(str(v)):」

翻紅重現(在複本 repo 跑,唯讀,未動到 /Users/enzo/harness/lumos-toolchain):
```
mkdir -p /tmp/nl_test_vault/docs/kg-knowledge/{Systems,MOC}
git init -q /tmp/nl_test_vault
mkdir -p /tmp/nl_test_vault/.lumos
echo '{"note_lint": {"gate": "on"}}' > /tmp/nl_test_vault/.lumos/config.json
cat > /tmp/nl_test_vault/docs/kg-knowledge/MOC/idx.md <<'EOF'
---
type: moc
---
# idx
EOF
cat > /tmp/nl_test_vault/docs/kg-knowledge/Systems/測試.md <<'EOF'
---
type: system
status: doing
created: 2026-09-25
updated: 2026-09-25
aliases: []
tags:
  - type/system
summary: |-
  KEY: test
decisions:
  - content: "test decision"
    decided: ""
    valid: true
---
# 測試
EOF
python3 /Users/enzo/harness/lumos-toolchain/scripts/lumos --vault /tmp/nl_test_vault/docs/kg-knowledge lint 測試
```
實際輸出:`✓ lint 測試 — 0 問題`——`decided` 明明寫了引號包住的空字串,理當被判「寫了卻是空的」,卻完全沒被抓到,跟頂層 `created`/`updated` 寫成 `""` 會被擋(見這批新測 `t_lint_empty_date_is_error`)不一致。這批新增的四支測試(`t_note_lint_gate_repo_root_layouts`/`t_doctor_note_lint_survives_malformed_note`/`t_note_lint_config_not_object_warns`/`t_lint_empty_date_is_error`)也都只覆蓋到頂層 `created`/`updated`,沒有一條測到 `decisions` 的 `decided`/`ended` 空字串,所以這個缺口沒被翻紅釘接住。

影響:這個開關在本 repo 是 on(擋),但 `decided`/`ended` 空字串仍能通過 lint、doctor L 段、cmd_lint 三個路徑,悄悄套錯「翻案時序比對」(注解自己講的用途),跟已折入的另外三個坑(找根、type 清單、整份非物件)不同,這個坑這輪並沒有真的補上。

## 已驗過、沒問題的路徑

開關讀取的 repo 根改用 `_vault_repo_root`(往上找 `.git`),我原本懷疑跟 r1 折入前的 `_repo_root_from_env` 混用,實測 `scripts/lumos` 第 1210 行與第 4835 行兩處呼叫點(`run_doctor` L 段與 `cmd_lint`)都已經是 `_vault_repo_root(env)`,MD5 對過跟真正工作目錄的 `scripts/lumos` 一致,沒有殘留舊呼叫。
引句:「_nlc = _note_lint_config(_vault_repo_root(env))」

健檢 L 段對整個圖譜跑 lint 時,`type` 寫成清單的筆記會被 `_lint_collect` 新增的非字串分支攔成一條錯誤且 `t` 被設回 `None`,不會讓後面 `t in ("system", "issue")`、`_STATUS_ENUM` 等處對非字串做成員判斷丟例外;`_lint_new_rules` 另外獨立读一次 `type`,list 不在 `_NOTE_STATUS_REQUIRED_TYPES`(全字串 tuple)裡用 `in` 比對時也只是不命中、不會炸,doctor 外層還包了 try/except 兜底,三層都驗過不會像折入前那樣讓整個健檢丟 Traceback。
引句:「except Exception as _ex:   # 一篇讀不懂的筆記不能讓整個健檢當掉——列成那篇的錯(代碼審 r1 邊界席)」

`.lumos/config.json` 整份不是物件(`null`/陣列/純量)這次改成回傳字典並帶警告訊息,不再靜默吃掉;實測 `data.get("note_lint")` 這行原本在 `data` 是 list/None 時可能丟 AttributeError,patch 已經把 `isinstance(data, dict)` 檢查挪到 `.get` 之前先擋,順序正確,不會有二次例外。
引句:「if not isinstance(data, dict):」
