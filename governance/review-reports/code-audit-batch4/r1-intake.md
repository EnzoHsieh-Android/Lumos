# code-audit-batch4 r1 收貨留痕

## 三道機械檢查
| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 架構對齊 | 3 句中 1 句錨不到 | 7/7 ok | vacuous 豁免 |
| 通才 | 5 句中 2 句錨不到 | 5/5 ok | vacuous 豁免 |
| 外家 codex | 全數錨定 | 4/4 ok | vacuous 豁免 |

## 錨不到的引句:機械重現(HIT 才撈回)
兩句錨不到的共同原因:它們引的是**既有碼**(說明「專案本來有這個做法/這個欄位工具會讀」),
不是這次 diff 的內容。凍結快照只含 diff,所以對不回去——不是編造。逐句用真檔重現:

1. 架構對齊 #3 「LINK_KEYS = ("verified_by", "plan_refs", "related", "core_refs")」
   指令:`grep -n 'LINK_KEYS = ' scripts/lumos`
   輸出:`8662:LINK_KEYS = ("verified_by", "plan_refs", "related", "core_refs")  # S2「純連結欄位」子集…`
   判定:**HIT**(逐字相符;core_refs 確實是工具的一等連結欄位)

2. 通才 #3 「for ref in as_list(n.fields.get("core_refs")):」
   指令:`grep -n 'fields.get("core_refs")' scripts/lumos`
   輸出:`1022:        for ref in as_list(n.fields.get("core_refs")):`(另 16494、16755 同型)
   判定:**HIT**(doctor Check C 與 impact 跨 repo 展開都在讀)

## 編排者自己的機械覆核(不靠席位轉述)
兩席都說我「全套零命中=既有測試沒有零斷言的」這句錯了。我寫了一支 AST 掃描逐支 t_ 函式
比對「任何 return 之前有沒有跑過 check()」,結果:

    零斷言 return 共 8 處,分佈在 8 支測試
    :2268 t_export_quote_escape      :2450 t_precommit_vendored_exempt
    :4324 t_marker_doc_sync          :5573 t_precommit_shebang_script_counts_as_code
    :6061 t_confirm_tty_unit         :6128 t_bootstrap_autoinit
    :6172 t_bootstrap_pull_failure_aborts  :12109 t_init_existing_resyncs

**跟三席點名的完全一致,不多不少。席位是對的,我原本的人工盤點是錯的。**
修完重掃 = 0 處。這支掃描已落成守衛測試 `t_no_zero_assertion_return_paths`(含反面),
往後不再靠人工盤點。

`core_refs`/`regen` 漏列、`_extra_fm_keys` 深巢 vault 失效,兩條都用真檔 grep + 實搭
monorepo 佈局跑 lint 重現過,皆 HIT。

## 兩家適配核對(Enzo 2026-09-06 追加要求)
逐件核落點,不推論:
- 開頭欄位提醒 + 設定檔擴充 → `scripts/lumos`(兩家共用同一支 CLI)
- 零斷言判紅 + 跳過通道 → `scripts/test_lumos.py` 執行器(由 git pre-push 叫起,與家族無關)
- skills 裡的規矩 → 安裝時同一份來源連進 `~/.claude/skills` 與 `~/.agents/skills`,已有守衛 `t_codex_skills_shared_dir`
- ★破口:單源守衛只掃 skills,漏了 Codex 讀的 `AGENTS.md` / `AGENTS.override.md` 與 Claude 讀的 `CLAUDE.md`★
  → 已納入掃描 + 三條反面斷言(入口檔真的在清單裡、抄一行進去會被抓到)

機械核對:`git diff` 這批新增行裡所有 claude/codex/harness 字樣,全部是註解或「被抄的那段是關於 Codex 的」,
**沒有任何一條是家族條件分支**。指令:
    git diff Lumos/main..HEAD -- scripts/ | grep '^+' | grep -in 'claude\|codex\|harness'
