severity: major

# code-ablation-probe r1 彙總報告(5 席 + 辯方核實)

五席:正確性 / 併發資源 / 邊界輸入 / 合約架構(claude sonnet)+ 外家 finder(Codex)。逐條回原檔核實後判讀。

## 折入(已修 + 綁測試)

1. **[major] lumos_stats 正則誤判**(scenario_probe.py:117)——`rg 'lumos search'`、`echo "lumos doctor"` 這種引號內/印出規則文字被算成敲了 lumos,灌 M2/M3。引句 `LUMOS_CALL_RE = re.compile(r"(?:^|[\s;&|(`'\"/])lumos\s+[a-z]")`。修:前置字元類移除引號 `'"`。測 `test_lumos_stats_rejects_quoted_and_echo`。(codex#2、邊界席)
2. **[major] 判準正則複製兩份而非 import**(ablation_lumos_first.py:37,41)——違反同目錄 retrieval_eval_multiword「單一實作來源、兩份必漂」明文教訓;`backfill_limit` 本身就在補第一版漂移的爛攤。修:`from scenario_probe import LIMIT_RE, LUMOS_CALL_RE`。(合約席)
3. **[major] M4 混淆答案對與走對路**(ablation_lumos_first.py:149)——`m4` 用 passed(敲對+答對合取),欄名寫「答案題正確」誤導。修:拆 M4a(gated)/M4b(content-only);探針加記 `answer_content_ok`。測 `test_m4_content_vs_gated`。(codex#1)
4. **[major] backfill 從截斷 calls 下修 ever_lumos**(ablation_lumos_first.py:57)——第一版只存前 12 呼叫,真 lumos 在第 13 個之後時重算壓成 False、低估 M2。修:截斷且原判 True 則保留。測 `test_backfill_keeps_ever_when_truncated`。(codex#4、正確性席)
5. **[major] _arm_stats 沒按 expected_ids 過濾**(ablation_lumos_first.py:157)——題庫改過後舊題殘檔靜默混進 M1-M4 與頭條差值。修:開頭用 idset 篩。測 `test_arm_stats_filters_expected_ids`。(正確性席)
6. **[major] 防線漏 cmd_init/_vendor_toolchain 路徑**(scripts/lumos)——只擋四個指令入口,但 init→vendor→_install_hooks_py→_sync_global_claude 會覆寫真 ~/.claude/hooks+settings,繞過。修:_refuse_if_probe 下移到變動原語 `_install_skills`、`_sync_global_claude`。(正確性席 F2)
7. **[major] Bash 指令截 200 字**(scenario_probe.py:46)——lumos 落在後面會漏抓,低估 M1/M2/M3。修:Bash 指令存全文(顯示用的其他工具仍截)。(邊界席)
8. **[major] 健康檢查只印 stderr、跑批不讀**(scenario_probe.py finally / ablation_lumos_first.py)——平行時一場沙盒事故靜默污染整批。修:skills_health 寫進 out JSON、探針事故回 rc3、跑批 collect_skills_health + threading.Event 停整批。測 `test_collect_skills_health`。(併發席 F1)
9. **[major] 題庫重複 id**(ablation_lumos_first.py:27)——虛墊缺場數+雙倍排程/雙倍權重。修:load_ids 去重。測 `test_load_ids_dedup`。(邊界席)
10. **[minor] load_results 對非 dict JSON/元素會炸**——一顆壞檔拖垮整批 merge。修:isinstance 過濾。測 `test_load_results_skips_bad_json`。(邊界席)
11. **[minor] strip_lumos_first_rule 標記重複無檢查**——find 取第一個、可能砍錯段且無聲。修:count!=1 安全回退。測 `test_strip_rejects_duplicate_markers`。(邊界席)
12. **[minor] rule_conflict_scan 只接 OSError**——非法 UTF-8(UnicodeDecodeError)炸掉整支掃描。修:併接。(邊界席)
13. **[minor] 缺 expect 的題先燒一次配額才炸**——修:`_validate_scenario` 派工前擋。測 `test_validate_scenario`。(邊界席)
14. **[minor] 拒絕訊息前綴 `✗` 不合全檔 `擋下:` 慣例**——修:改 `擋下:`。(合約席)
15. **[minor] lumos_stats 對 summ 無 str() 防禦**——與 backfill 不一致。修:加 str()。(邊界席)

## 附理由接受(不修)

- **[minor] max_per_window TOCTOU 競態**(codex#3、併發席 F2):兩 worker 可同時放行、超額到 workers×n。接受——這是禮貌性軟上限,真正的帳號硬上限由 --wait-on-limit 接住,超額有界(預設 workers=2),不會做出錯的判分。已在 code 註記。
- **[minor] waited 預算整支子程序共用**(併發席 F3):同 job 內多場共用 wait_on_limit 預算。接受——是設計選擇(每子程序一份總預算),行為正確只是非逐場獨立。
- **[minor] 兩個 runner 實例無鎖**(併發席 F4):同時對同 out_dir 跑會重複派工。接受——操作紀律問題,單 runner 是常態;逐題檔名帶時間戳不會撞檔。

## 既有問題(非本 diff 引入,不進本輪處置;記追蹤)

- cmd_teardown 忽略 cmd_uninstall 的 rc、恆回 0(合約席):既有寫法,本 diff 只是讓它多一個觸發場景。
- subprocess 逾時只殺直接子程序、非行程群組(併發席):既有 context,--runs/多 worker 常態化後撞機率升,建議另票用 start_new_session+os.killpg。

## 核實帳

每條 finding 都回原檔核過 file:line 與引句;codex 的 4 條與 claude 四席去重後無矛盾。無 blocker。M1 頭條結論(94.0% vs 58.3%,差 35.7pp)在所有修正後不變。
