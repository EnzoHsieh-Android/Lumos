severity: clean

驗證摘要(非 finding,供編排者參考):在 `/tmp/nh-review`(scripts/ 完整複製,GRAPHCTL 指向該副本)對 scripts/lumos 逐條改壞下列規則的判定邏輯,各自單獨跑對應測試:

1. `if homesB.get(f) and not homesN.get(f): blocks.append(("home-removed", ...))`[S4] 改成恆假 → `t_nodehome_check_blocks_home_removal` 3/4 斷言翻紅。
2. `if not homesN.get(f): blocks.append(("new-homeless", f))`[S3] 改成恆假 → `t_nodehome_check_blocks_new_homeless_file`、`t_nodehome_birth_commit_requires_homes` 翻紅。
3. `foreign_before = (_nodehome_refs(...) - ownB...) if b else set()`[S9] 改成 `foreign_before = foreign_now`(恆無新違規)→ `t_nodehome_check_blocks_new_foreign_ref` 2/3 翻紅。
4. `if not (mine & routed[rel]): blocks.append(("route", ...))`[S13] 改成恆假 → `t_nodehome_check_blocks_write_back_to_non_home` 2/3 翻紅。
5. `if f in wb_files: blocks.append(("write-back-homeless", f))`[S13b] 改成恆假 → `t_nodehome_write_back_requires_every_changed_file_homed` 1/2 翻紅。
6. `_nodehome_resp_ok` 改成恆 True[S16/S17/S18] → 三支對應測試各自翻紅(共 6 條斷言)。
7. `kind = "blocked" if blocked and cfg["mode"] == "on" else ...` 拿掉 `and cfg["mode"] == "on"`(warn 模式也擋)[S37] → `t_nodehome_gate_switch` 翻紅。
8. `_nodehome_side` 的 share/changed 快取跳過邏輯改成恆假(強迫每篇都重讀)[S38] → `t_nodehome_diff_shares_unchanged_notes` 翻紅(讀取次數斷言抓到)。
9. `_nodehome_ledger` 的 bypassed/legacy 分組互換[S39] → `t_doctor_nodehome_splits_bypassed_from_legacy` 翻紅。
10. `_lands_in_bad` 拿掉 `.md` 後綴檢查[S20] → `t_lands_in_field_format` 翻紅。
11. 處置閘落點步驟的 `if bad: ... return "fail"` 改成恆假[S21] → `t_disposal_gate_requires_landing` 翻紅。

以上涵蓋計劃 [S1]–[S21]、[S37]–[S39] 中判定最重的規則(家的認定、別人的檔名、寫回落點、負責範圍門檻、gate 開關、效能快取、健檢分群、落點格式與處置閘整合);全部 11 個突變無一存活。另核對計劃全部 39 條 [SN] 條款的 `[test:]`/`[manual:]` 標註:除 [S23][S32][S36] 明文標 `[manual:]`(非機械可驗,計劃自己承認天花板)外,其餘均有 `[test:]` 綁定,且逐一比對 51 個被引用的測試函式名在 `scripts/test_lumos.py` 中全部存在(無懸空引用)。另跑 `t_nodehome_rules_in_hint_skill_and_discipline`(需要源 repo 的 skills/範本檔案)於實際 repo 下全數通過,證實文件同步宣稱不是空話。斷言型態上,CLI 層級的每條 `_nh_check` 斷言都同時卡 `rc ==` 與訊息子字串(非單靠文字);每個規則測試函式都先有「不該擋的情境仍放行」的前置控制案例,再驗證「該擋的新增情境確實擋下」,fixture 有真的造出規則要判定的情境。未能找到能在此鏡頭下翻紅的輸入,故判定為對。

總結:最高 severity clean,blocking 共 0 條
