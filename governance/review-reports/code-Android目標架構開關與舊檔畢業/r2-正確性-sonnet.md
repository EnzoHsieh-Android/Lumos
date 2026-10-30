severity: major

**審查範圍與方法**:固定版本是 `44b0044da`,我獨立讀了完整 diff 與修補 diff。在 `/tmp/lumos-seat-work/.../正確性-sonnet/` 的 `--shared` clone 裡做了改壞實驗,做完已刪。主 worktree 上的 `-k arch_target_graduate`(24 個,含 same_branch、check_note)、`-k legacy_doctor`(7 個)、`-k spec_lens_reads`(2 個)、`-k arch_target_doctor`(5 個)修後全綠。另一個在 clone 上跑的 `-k arch` 全套跑到一半,我同時在改 clone,出現 85 個失敗,結果作廢、不採信。

## Findings

### 1
severity: major
blocking: 是

doctor 在「HEAD 版沒有目標架構宣告、但有舊檔清單」時還印不印清單摘要,沒有任何測試守著。S9 的條款寫「目前提交有舊檔清單時應多印一行摘要」,沒有限定要有宣告。這條路徑是修補輪新加的早退,而「沒被判給目標節點」計數正是為這種狀態準備的。

引句:「    if not rules and not warns:
+        return [], [], leg_list, leg_probs」

- 改壞實驗:把這行回傳改成 `return [], [], [], []`。修後版 `-k legacy_doctor` 跑 7 個全過、`-k arch_target_doctor` 跑 5 個全過。
  - 原因:`t_arch_target_legacy_doctor_lines` 的 repo 一律帶有宣告(`cfg = _arch_cfg(...)`),「沒有清單不印」那組也有宣告。
  - 實際後果:被改壞後,宣告被刪掉但清單還在的專案,doctor 不再提醒。
- 複現命令:在 clone 用 python 把 `return [], [], leg_list, leg_probs` 換成 `return [], [], [], []`,再跑 `python3.14 scripts/test_lumos.py -k legacy_doctor`。結果是 7 passed。
- 修前 vs 修後:修前 `6c3` 的獨立函式 `_arch_legacy_doctor_line` 不依賴宣告,修補輪把它併進有早退的函式。修前我沒另跑,只看了修補 diff 的程式,所以測試是否「修前會紅」無從比較。
- 歸因:有證據的修復回歸。程式路徑是修補輪新增的,測試缺口也在修補輪新增的接線上。但程式行為本身是對的,只是沒被釘住。

### 2
severity: minor
blocking: 否

`_arch_legacy_check_lines` 傳 `need_head=True` 這一點沒有測試守著。起點有宣告、但起點版沒有清單檔,而終點版新增了清單時,「清單比起點多了 N 行」這行提醒才會印出來。

引句:「legacy, h_legacy, keep = _arch_legacy_graduation(root, trusted, head, rules, need_head=True)」

- 改壞實驗:改成不傳 `need_head`(預設 False)。`-k arch_target_graduate_check_note` 跑 7 個全過。
  - 原因:測試 A、A2、E、B 的起點版清單都非空,K 沒有宣告,沒有案例走「起點無清單、終點新增清單」。
- 直接呼叫函式證實:起點無清單、終點新增一行時,`need_head=False` 回 `(set(), None, set())`,`need_head=True` 回 `(set(), {'…OrderOld.py'}, set())`。預設值會讓提醒靜默消失。
- 嚴重度降級理由:這種情況下審查本來就照起點版(沒有清單),所以只是少了「架構測試會跳過這些檔」的提示,不會漏審。這是覆蓋面缺口,不是行為錯誤。
- 歸因:有證據的原有漏查。`need_head` 在修補輪重構前就存在,但修補輪把單一入口收斂後它成了載重參數,測試沒跟上。

## 沒有 finding 的部分

- 回傳形狀:`_arch_target_doctor_lines` 在整個 repo 的 scripts、docs、skills 下只有 `scripts/lumos:2283` 一個呼叫者,已解成四個值,錯誤分支也給四個值。測試端沒有直接呼叫它的地方。
- `need_head` 各呼叫處:推送前分級、代碼審派工鏡頭、設計審派工鏡頭走預設 False。
  - 清單空時略過讀 head,等價於「畢業集合為空」。
  - `_arch_legacy_apply` 的 `if not legacy: return` 與此一致。
  - 只有說明行用 True,因為它需要印「多了幾行」。
- 例外與 None:
  - `_json_at_ref` 只回 dict 或 None,`{}` 會落到 `files` 檢查而判 unreadable,不會 AttributeError。
  - `head=None`、`head==ref`、`ref=None`(沒主線或首推)都早退,未畢業。
- 邊界與衍生資料:
  - 畢業判定只有 `_arch_legacy_graduation` 一份;說明行的「其中幾支」另算 `judged` 是顯示用,不影響判定。
  - NFC/NFD 兩邊都轉了。
  - 增量範圍讀分叉點版,所以起點若是分支自己的提交也不會誤讀。
  - 頂端清單讀不懂或宣告有改時,`keep` 為空,失敗方向是多審。
- 新舊互讀:舊版 lumos 不認識 `.lumos/arch-legacy.json`,會直接忽略;新版讀不到檔就當沒清單。
- 寫一半、時間、不可逆:不適用(全部是唯讀路徑)。
- 文件:06 那一列、`arch-alignment-lens`、`templates.md` 的說法與程式行為一致,沒有照做會做錯的矛盾。
- 未驗範圍:S1–S4、S7、S8、S10 屬下一部分。doctor 現在每次都多叫一次 `git ls-files -z`,即使沒有宣告也沒有清單,我沒有做大 repo 的量測,所以沒標 finding。

## 固定席逐條判定

- `Issues/code-loop守衛main-direct盲區`:不影響。diff 沒動 main-direct 的判定,只多了讀清單。
- `Systems/lumos-cli-read` ★INVARIANT★(search 預設排除 superseded、不排 stale):不影響。diff 沒碰 search。
- `Systems/pitfalls-code-loop`:不影響合約,只在分級處多接一層清單過濾。
- `Systems/arch-alignment-lens`:行為如文件所述。
- `Systems/design-loop` ★INVARIANT★(審材必須是 .md 計劃、有 `[SN]` 的條款定義 `[綁定測試:有]`):不影響。這份審材是 .patch 已在前面流程處理,diff 沒動處置閘。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要有前置斷言):發現 1、2 正是這個形態,測試的現場走不到被測分支,把修法還原照綠。
- `Systems/guard-kill` ★INVARIANT★:不影響,沒碰 rc 優先序與 `--json` 純度。
- `Systems/reversibility-governance-ledger`:不影響,這次不碰帳本。
- 超出上限只列名的各篇:沒有逐篇讀,圖譜面沒有它們被破壞的證據,不影響。

## 三問

1. **原問題的修復效果,行為證據**:
   - 輸入:`t_arch_target_graduate_same_branch` 的 I、J1、J2 與 `check_note` 的 K、A2。
   - 預期:清單讀分叉點版,NFD 清單認得 NFC 檔,起點版沒有宣告時不印清單說明,「其中幾支」只算有改動的。
   - 修後:`-k arch_target_graduate` 24 passed。
   - 修前:作者沒另存,我也沒跑,**未判定**。
2. **修補處的正常、錯誤與相鄰路徑**:
   - 輸入:主 worktree 上的 `-k legacy_doctor`、`-k arch_target_doctor`、`-k spec_lens_reads`。
   - 預期:doctor 計數、git 失敗說「讀不到」、列檔失敗說「算不出」、其他宣告提醒不變、設計審不列舊檔。
   - 修後:7、5、2 個全過。
   - 修前:未判定。
   - 這幾條路徑仍成立,但發現 1 說明「無宣告但有清單」這條路徑目前沒有測試守著。
3. **新發現同一案例,修前修後**:
   - 發現 1:修前是獨立函式、不依賴宣告;修後併入有早退的函式,行為仍會印但缺測試。
   - 發現 2:`need_head` 修前的狀況未驗,未判定。

最嚴重等級為 major
