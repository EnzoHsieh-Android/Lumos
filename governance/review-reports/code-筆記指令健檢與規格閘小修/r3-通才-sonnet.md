severity: minor

我是通才席,第 3 輪(最後一輪),只看測試那半。整份審查沒有 blocker 或 major。

我先在原 repo(342cf099,和 HEAD 內容相同)跑了本輪新增或改動的 17 組測試,全綠。接著把 `scripts/lumos` 複製到臨時目錄,逐一做改壞實驗,確認每個修補都有測試守著。

## 發現

**1. 規格閘留痕「同一秒取先列的」,會讓治理帳裡同秒的新留痕輸給舊留痕**
severity: minor
- blocking: 否
- 位置:`scripts/lumos` 的 `_spec_gate_pick`。
- 具體例:乾淨 clone 沒有本機審查帳,治理帳裡同一迴圈有兩筆同秒留痕,依序是舊 token 和新 token。
  - 輸入:`_spec_gate_pick(None, old, new)`,兩筆的 `ts` 都是 `2026-10-15T10:00:00+08:00`。
  - 實際:回傳 OLD。
  - 預期:治理帳是只追加的檔案,同秒時後寫的才是新的,應該回傳 NEW。
  - 修前:同秒取後列的,回傳 NEW。
- 影響:推送閘拿到舊指紋,會判計劃過期而擋下推送。這是偏安全的錯誤,補跑一次規格閘就解。要同一秒內連跑兩次規格閘才會遇到,所以只算 minor。
- 測試那邊:`t_spec_gate_record_in_governance` ③ 把舊留痕的 `ts` 改成 `2026-01-01`,避開了同秒平手。同秒平手只剩 `t_spec_gate_pick_same_second_keeps_local` 一條,它只守「本機那筆放最前就贏」,沒守治理帳內部的順序。更穩的做法是,平手時本機優先,同一來源內以後列為準。
- 歸因:未判定。我只直接驗了修後的行為,修前是從程式碼讀出來的,沒有另外載入舊版跑。
- 引句:「old = dict(old, ts="2026-01-01T00:00:00+08:00")      # 舊的那筆確定比較早(秒級 ts 同秒時取本機那筆,代碼審 r2 G7)」

**2. `_spec_gate_pick` 的 token 去重沒有行為差別,測試也沒守它**
severity: minor
- blocking: 否
- 去重加上「嚴格 `>`、同分取先列」之後,結果跟沒去重一樣。只有「同 token 但 ts 不同」才會分出差別,這不是真實情境。
- 實驗:把去重那一行改成 `if not r:`,`t_spec_gate_pick*` 和 `t_spec_gate_record_in_governance` 全過。
- 測試 `t_spec_gate_pick_same_second_keeps_local` 的 docstring 說「先依 token 去重再比時間」,但它守的其實只有「同秒取先列」。這是死碼加上一句沒有對應測試的說明。
- 歸因:有證據的原有漏查(去重是這輪才加的,測試一開始就沒覆蓋到)。
- 引句:「if not r or (r.get("token") is not None and r.get("token") in seen):」

**3. `t_docs_catalog_count_wording` ③ 的判準偏弱,斷言的說法比實際證明的多**
severity: minor
- blocking: 否
- ③ 現在檢查 `reference.md` 裡「N 個指令的總目錄」的 N 有沒有在 `_docs_command_count_claims(ref)` 的結果裡。
- 問題:`reference.md` 第 117 行也有「92 個頂層命令」,所以 `{'92'}` 本來就會出現。
- 實驗:把 `reference.md` 的「總目錄」改成「目錄」,`_docs_command_count_claims(ref)` 仍回 `{'92'}`。
- 實際分工:守衛少認「總目錄」寫法,是 ① 抓到;`reference.md` 改掉措辭,是 `i == -1` 那一支抓到。③ 名字寫「真的被守衛掃到」,沒有證明那一句。
- 另外,從後往前讀數字的寫法(反轉字串再 `re.match`)很難讀,可以直接用 `re.search(r"(\d+) 個指令的總目錄", ref)` 取代。
- 歸因:未判定。
- 引句:「check("③reference.md 的總目錄那句真的被守衛掃到", num is not None and num in _docs_command_count_claims(ref), (num, i))」

**4. 「只要…就」「等到…才」配對,遇到中間有逗號時變成誤報**
severity: minor
- blocking: 否
- 輸入:`只要尚未登入,就導到登入頁`,`等到檔案還沒鎖住,才寫入`。
- 實際:`_ns_negation_hits` 分別回 `[('尚未', 2)]`、`[('還沒', 4)]`,會唸成現況句。
- 預期:這是條件句,不該唸。
- 原因:配對字要在「否定字眼之後、同一小段」裡找,逗號會把小段切斷。這種寫法比不帶逗號的更常見。
- 影響:這條只用 warn,不擋,所以是 minor。
- 測試只放了不帶逗號的 `只要尚未登入就…`,沒覆蓋這個形狀。
- 歸因:有證據的修復回歸。修前只看字首,這種寫法是靜音的;修後變唸。這屬於「換成配對規則」這個決定的已知取捨,請編排者決定要不要接受。
- 引句:「_NS_NEG_COND_PAIRED = {"只要": "就才便", "等到": "才再就"}」

## 三問

1. **原問題的修復效果有何行為證據?** 已驗,下列每個修補都有測試守著。我把對應的實作改壞(複製版,已刪),各有測試翻紅:
   - git 判不了時照擋(`_is_git_worktree` 回 None 當成非 git):翻紅。
   - 三點範圍起點取 merge-base(改回左端點):翻紅。
   - 補跑紅前警告把未追蹤的新檔算進去:翻紅。
   - 警告扣掉簿記檔(改成不扣):`t_spec_gate_manual_red_ignores_bookkeeping` 與 `t_fix_check_tree_setup` 翻紅。
   - `_excluded_line` 內的冒號前置檢查(拿掉):`t_door_exclusions_many_spaces_fast` 從 1 秒內變成 55.8 秒,翻紅。
   - 同秒取先列(改成取後列):翻紅。
   - 第二個詞是旗標的分支(拿掉):`t_ref_path_first_word_of_command` 翻紅。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 大致成立。本輪改的函式(`_dirty_non_bookkeeping`、`_range_base`、`_excluded_line`、`_drift_fix_shape_err`)的其他呼叫端,測試沒有紅。例外是發現 1 的同秒平手方向,以及發現 4 的逗號形狀。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - 發現 1:修前 NEW,修後 OLD(修前是讀程式碼推的,沒載入舊版跑)。
   - 發現 4:修前靜音,修後唸(同上)。
   - 發現 2、3:修前、修後行為相同,屬於測試強度問題。

## 其他核對

- **被刪掉的行為:** `t_prepush_spec_gate_done_gone_still_runs_rest` 刪掉的「兩支都找得到且綠 → 過」,原本就沒有對應斷言,只是 docstring。它已改由 `t_prepush_spec_gate_done_in_range` 的 ④、⑤ 守著。
- **固定席節點:** 這次改動沒碰 `search`、`guard kill` 和設計審處置閘。`lumos-cli-read`、`guard-kill`、`design-loop`、`測試假綠形態` 的 ★INVARIANT★ 不受影響。`loop-convergence-recording` 的 ★RISK★ 只受 `cmd_loop_fix_check` 的簿記檔過濾影響,測試有守。
- **表態記錄:** `py-eventloop`、`py-parallel`、`py-memory`、`py-hotpath` 都標 na,我沒看到相反證據。
- **未驗範圍:** `_dirty_non_bookkeeping` 處理改名條目(`R  new\0old`)的路徑切割沒測。`cochange --diff "   "`(只有空白)沒有測試,只有 `""` 有。我讀過程式,`.strip()` 的分支是對的。

最嚴重 severity:minor(4 條),blocking 共 0 條。
