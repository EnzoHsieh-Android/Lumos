severity: minor

審查範圍:r1-snapshot-tests.patch 對照計劃 S1–S14。基線:在 --shared clone 內跑 `-k note_audit_reread`,88 passed、0 failed。另跑 t_notes_touched_in_range_shared 相關子集亦綠。全套沒跑(規定)。

## 突變實驗(每次只改 scripts/lumos 或 scripts/hooks/pre-push 一處、清 __pycache__、跑完還原)
| # | 改壞什麼 | 結果 |
|---|---|---|
| M1 | _note_reread_scan 拿掉 `homed.update(homes_b.get(f, ()))`(家只看頂端) | t_note_audit_reread_prepare_candidates ③紅 |
| M2 | _note_reread_rows 行號檢查拿掉 bool 排除 | record_intake ③紅 |
| M3 | _note_reread_diff 拿掉 --literal-pathspecs | prepare_candidates ⑦紅 |
| M4 | 掛鉤改成所有非零都交給 pp_stop_if_signaled(`rrint_rc=$rr_rc`) | check_wired ③⑦紅 |
| M5 | 紀錄檔名正規式拿掉 `$` | check_never_blocks ⑫紅 |
| M6 | 對照指紋多混一個 oids 數量 | check_reminds ④⑤⑧紅 |
| M7 | 上下文序列 (3,1,0) 拿掉 1 | prepare_diff_scope ⑥紅 |
| M8 | 最外層改接 BaseException | check_never_blocks ⑪紅 |
| M9 | 平均截斷 `remaining // left` 改 `// len(parts)` | prepare_diff_scope ⑧紅 |
| M10 | 行號上限 `<= nlines` 改 `<= nlines + 1` | record_intake ③紅 |
| M11 | _BOOKKEEPING_DIRS 拿掉 reread-verdicts | bookkeeping ①②④紅 |
| M12 | 重複行號改成不去重 | record_intake ③④紅 |
| MF | note_reread.gate=block 改成真的回 block | mode_and_isolation ②紅 |
| MA | _note_audit_resolve「頂端已在主線」的原因種類 none 改 skipped | **全綠(未翻紅)** |
| MB | 候選篩選拿掉「頂端還存在」(`if pre + r in oids` 改 `if True`) | **全綠(未翻紅)** |
| MC | _NOTE_REREAD_LIST_MAX 10 改 1000 | 全綠(條款字面沒寫上限,僅提一句) |
| MD | 掃描之後那一次逾時檢查拿掉 | 全綠(掃描內的 _tick 已涵蓋,算重複防線,不報) |
| ME | skipped-env 改記 skipped | 全綠(S7/S13 條款字面沒寫 skipped-env,僅提一句) |

結論:S1–S14 的主行為(候選、diff 範圍與截斷、派工詞、record 逐項收、check 提醒/掩蓋/永不擋、簿記豁免、掛鉤 130 分流、模式與隔離)都有會翻紅的測試,沒有發現零斷言、斷言太鬆或只測 mock 的假綠。S7 那批用模組全域替換(_ns_git、_nodehome_side 等)造失敗,是造「git 失敗/例外」的必要手段,外層 rc、輸出、記帳都走真的 cmd_note_audit_reread_check,可接受。

消費專案(沒有 skills/、沒有 governance/eval/):逐支看過,讀 skills/、掛鉤、ci.yml 的 S9、S14 都先走 `_need_src`(只認檔案實況,記 skip 不紅);S4、S11 讀的 scripts/templates/note-audit-reread.md 是被 _VENDORED_TREE_FILES 發到消費專案的檔,在場。新測試都沒有讀 governance/eval/。沒看到會讓消費專案全套紅的地方。

## F1 S7 條款的「頂端已在主線記 none」沒有測試守
severity: minor
blocking: 否
引句:「sub("④刪除分支 → 記 none(這次沒有新東西)"」
佐證行:file: `scripts/lumos:26168`(_note_audit_resolve 的 quiet 分支 `reasons.append(("none", why))`)
1. 條款 S7 括號明寫「頂端已在主線、刪除分支照〈做法〉4 記 none」兩種。測試只造了刪除分支(全 0 終點,④)。
2. 突變 MA:把 `reasons.append(("none", why))` 改成 `("skipped", why)`,88 條全綠。刪除分支走的是另一行(26150),所以改壞「頂端已在主線」這一支沒人發現:實際會把正常的「這次沒有新東西」記成 skipped,污染兩週量測的 skipped 占比。
3. 補法:在 check_never_blocks 加一個頂端已在 origin/main 的場景,斷言記 none、不記 skipped。未能造出錯誤使用者行為以外的證明,故不升級。

## F2 S1 條款的「頂端還在」沒有測試守
severity: minor
blocking: 否
引句:「家沒改過、不是家(計劃)、只改筆記沒改程式的不產」
佐證行:file: `scripts/lumos:26729`(`cands = sorted(r for r in homed & touched_rel if pre + r in oids)`)
1. 條款 S1 與做法第 1 節都寫「∩ 頂端存在的筆記」(範圍內把家筆記刪掉的情形)。t_note_audit_reread_prepare_candidates 沒有「家筆記在範圍內被刪」的案例;S12 那支只驗 _notes_touched_in_range 不做頂端過濾。
2. 突變 MB:把 `if pre + r in oids` 改 `if True`,88 條全綠。刪掉的筆記若當候選,後面組項目檔讀不到筆記,最好是被外層吞成 skipped,最壞是丟例外或產出殘缺項目檔。
3. 補法:prepare_candidates 加一個「程式改了、家筆記同範圍內 git rm」的案例,斷言不產檔、印「這次沒有要對照的家筆記」。

最高等級:minor
