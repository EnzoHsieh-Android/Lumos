severity: minor

# code-ablation-probe r3 彙總報告(審 r2 修正版)

席:正確性+併發、邊界+統計(claude sonnet 各一)。外家 Codex 本輪不可用(前輪 stdin 卡住),單家族視角、降級留痕(Enzo 2026-08-22 裁 high 缺外家不硬擋)。

## 結果:r2 的 4 條折入全部核實正確,無 major、無新增行為 bug

兩席都實跑重現腳本+測試(131 全綠、含 backfill 三分支/M2 排除/防線四指令)驗證,非純讀碼:

- **collect_skills_health 接進 main**:`poisoned = collect_skills_health(out_dir)` 在 `if not a.merge_only:` 區塊外無條件執行,--merge-only 與 jobs 空兩路都掃得到;與 `stop.set()` 即時攔截互補不重複。核過無誤。
- **backfill 三分支**:`else: r["ever_lumos"], r["first_lumos_idx"] = None, None` 對截斷判不出標未知;下游 `is not None` 篩過,無 TypeError、無誤算。核過無誤。
- **M2 分母 m2_known**:`round(m2 / len(m2_known), 4) if m2_known else None` 擋除零,全 None 組回 —,不炸;M1/M3/M4 未受牽連。核過無誤。
- **_sync_global_claude 回 bool + run_one 還原 miss_a**:回傳鏈對,`miss_a` 純顯示不影響計分。核過無誤。

## 折入(2 條 minor,均文件/契約一致性,無行為變更)

1. **[minor] backfill_limit docstring 停在 r1 舊邏輯**——頂部摘要與實作(r2 三分支)矛盾,對照讀誤導。
   引句:「截斷且原本標 True 的保留 True」。修:docstring 改寫成三分支描述。(邊界席)
2. **[minor] cmd_install 沒接 _sync_global_claude 的 bool 契約**——r2 已讓該函式回 bool、_install_hooks_py 據此印訊息,但 cmd_install 那個呼叫點沒跟上、無條件印成功;非活 bug(cmd_install 入口已擋 probe),但契約不一致、日後非 probe 的失敗回退會印假成功。
   引句:「synced = _sync_global_claude(root)」(這是 _install_hooks_py 已接上的契約,cmd_install 該比照);函式回傳語意 引句:「回 True=有做、False=探針下被擋沒做」。修:cmd_install 接上 if/else。(正確性席)

## 收斂判定

r3 無 major、無行為缺陷;兩條 minor 都是文件/防禦一致性,已當輪折入(改 docstring + 補 if/else,零行為變更、131 測試仍綠)。外家席不可用故單家族視角、結論降級留痕。建議收斂。
