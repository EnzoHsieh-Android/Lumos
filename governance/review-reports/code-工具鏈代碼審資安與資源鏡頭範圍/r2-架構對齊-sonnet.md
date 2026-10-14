severity: clean

我讀了 r2-repair.patch 的程式與測試部分,以及筆記和範本的改動。沒有發現第二種做法,也沒有跨層直呼。

**§7.6 三問**

1. 分層與依賴方向:已讀,無 finding。
   - `scripts/lumos` 只改了 `_LENS_SCOPE_TOOLCHAIN_LINE` 這個常數的文字,位置、用法和 `cmd_loop_next` 的呼叫方式都沒變。
   - 測試仍走 `_lens_next`、`_mk_lens_dirs`、`mkvault`、`run` 這組既有夾具。
   - 對照: `scripts/test_lumos.py:96424` 的 `_lens_next`、`scripts/test_lumos.py:96433` 的 `_mk_lens_dirs`。
2. 命名與錯誤處理:已讀,無 finding。
   - 新測試 `t_loop_next_lens_scope_loose_code_ids`、`t_loop_next_lens_scope_marker_odd_kinds`、`t_toolchain_lens_scope_note_pointers` 命名接在 `t_loop_next_lens_scope_*` 和 `t_toolchain_lens_scope_*` 後面。
   - 寫法照舊:`check("①…")` 加 `_need_src`。
   - 變異斷言(`⑥變異:拿掉 … 那句`)跟 `④`、`⑤` 同一種寫法,都是 `find` 加 `replace(_RM_LITERAL_RULE, "", 1)`。`⑥` 用 `"\n"+head` 找位置,`⑤` 沒加換行,只是細節差異,不列。
   - 對照: `scripts/test_lumos.py:96383-96394`、`scripts/test_lumos.py:96312-96339`。
3. 第二種做法:已讀,無 finding。
   - `_tpl_dispatch_fences` 沒有另寫一套掃描器,只在原有函式上加了 `sub` 追蹤和兩個 `elif`。呼叫端只吃函式回傳的 `(標籤, 圍欄各行)`,內部換成三元組不影響它們。
   - 逐句比對(`for sent in (…): sent in three`)接續了 `_IDEMP_ORIG`、`_SEC_SIX_CLASSES_ORIG` 這種「改動前原句逐字」的獨立基準,沿用既有做法。
   - 新增的 `_SEC_NB_DOS_ORIG` 同理。
   - 對照: `scripts/test_lumos.py:96321-96350`、`scripts/test_lumos.py:96477`。
4. 設計審才問的落點:本輪是代碼審,不適用。附帶確認:
   - `Systems/每輪修補差異派工.md` 的 `about_code` 新列 `skills/lumos-code-loop/reference.md`。全 repo 的 Systems 裡只有這一篇列它,沒有重複的家。
   - 新增的刪檔紀律那一行,在 §3.1 和 §9 派工詞第二行,字面與 §7.6 範本、`_RM_LITERAL_RULE` 一致,放在括號第二行的位置也和既有 LUMOS-SEAT 派工詞相同。

**範本填空和筆記**:已讀,無 finding。
- 填空改成「整行換成貼上的那一段」,在原有的二填空機制內改措辭。
- 筆記 summary 行沿用 `WHY:`、`RULE:`、`KEY:` 加方括號鍵的既有格式。
- 沒有新增 `KEY:` 行,只是改了既有 `KEY:` 行句尾的指向。

**表態記錄**:附加段的 py-external 引用的是 `scripts/scenario_probe.py:1077`,不在本輪修補差異裡,這一席沒法對照,也不影響架構對齊的判定。

最高等級 clean,blocking 0 條。
