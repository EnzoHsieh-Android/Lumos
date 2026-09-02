severity: major

# code-ablation-probe r2 彙總報告(審 r1 修正版)

席:正確性+迴歸、併發+邊界(claude sonnet 各一,審 r2-snapshot=r1 全部修正)。外家 Codex 本輪兩次卡在 stdin 沒產出 → 外家席不可用,依 Enzo 2026-08-22 裁「high 缺外家不硬擋、降級留痕」:本輪為單家族視角。

## 折入(已修 + 綁測試)

1. **[major] collect_skills_health 是死碼,main() 沒呼叫**(ablation_lumos_first.py)——r1 寫了健康檢查函式也加了測試,但 main 實際停批走 run_job 自讀那條;`--merge-only` 跳過工作迴圈、或本批 needed 全 0(jobs 空)時,上一輪留下已標事故的舊檔會被靜默合併出報告。引句 `def collect_skills_health(out_dir):` 全域只被測試呼叫。修:main() 產 summary 前無條件 `collect_skills_health(out_dir)`,非空印警告+ summary 標 `skills_health_poisoned`。(併發席 F1)
2. **[major] backfill 截斷分支保留可見假陽性**(ablation_lumos_first.py)——r1 修法「截斷就保留原 True」連舊正則假陽性(`rg 'lumos search'` 在可見前 12 筆)也留著,等於 r1 finding#1 換截斷角度漏回來。引句 `if truncated and r.get("ever_lumos"): r["first_lumos_idx"] = idx if ever else None`(不寫回 ever)。修:三分支——不截斷用重算/截斷且可見有真呼叫=True/截斷且可見無真呼叫=未知 None;_arm_stats M2 分母排除 None。測 `test_backfill_truncated_ambiguous_is_unknown`、`test_backfill_truncated_visible_false_positive_downgraded`、`test_backfill_truncated_visible_real_call_kept`、`test_arm_stats_m2_excludes_unknown`。(正確性席)
3. **[minor] _install_hooks_py 探針下印假成功**——_sync_global_claude 在 LUMOS_PROBE 下 return 沒做事,但緊接無條件印「✓ 全域 hooks 同步」。修:_sync_global_claude 回 bool,_install_hooks_py 據此印「已擋、未動 ~/.claude」。(正確性席)
4. **[minor] run_one 診斷訊息弱化**——r1 把「答案缺哪些關鍵事實」的 miss_a 列表砍成通用句,除錯資訊流失。修:還原 miss_a。(正確性席)

## 附理由接受

- **[minor] 新正則對貼引號的真呼叫會漏抓**(`sh -c 'lumos search x'`、`ssh host "lumos doctor"`)——移除引號修假陽性的代價。接受:題庫的 prompt 都是要 AI 直接下 lumos,不會包一層 sh -c;假陰性實際踩到機率低。REVISIT 若題庫出現包裹式呼叫。
- **[minor] _install_skills 那道守衛對 init 路是死碼(belt-and-suspenders)**——init/vendor 路實際只經 _sync_global_claude,不經 _install_skills;cmd_install 入口本來也擋過一次。接受:多一道無害,真正堵洞的是 _sync_global_claude 那道(已生效)。r1 報告把兩處並列略誇大,此處更正。

## REVISIT(記追蹤,不本輪動)

- 單一 Bash 指令字串無上限(Bash 指令改存全文後):目前實測最大結果檔 69KB、總目錄 1MB,沒膨脹;但若題目誘導 AI 把整份 diff 內嵌進單一指令,理論可無界。REVISIT:2026-10-02 隨探針量測若出現 >1MB 單檔就加 cap。

## 核實 / 誠實帳

- r2 兩席逐條回原檔核 r1 的 15 折入:除本輪抓到的 #1(死碼)、#2(半修)外,其餘 13 條改對、無回歸;131 測試全綠;主測試套件(test_lumos.py 全量)exit 0。
- 外家席本輪不可用(Codex stdin 卡住兩次),單家族視角,收斂結論降級留痕。
- M1 頭條(94.0% vs 58.3%)在所有修正後不變。
