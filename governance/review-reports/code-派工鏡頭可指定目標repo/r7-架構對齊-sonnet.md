severity: major

**finding 1:隱形字元清單是第二份「什麼算看不見」**
severity: major
blocking: 是 — 專案已有 Unicode Default_Ignorable 全表與判定函式,這輪 lumos 端又手抄一份子集,是同一件事的第二種做法。
引句:「_LENS_NAME_INVISIBLE_RANGES = ((0xFE00, 0xFE0F), (0xE0100, 0xE01EF), (0x034F, 0x034F), (0x17B4, 0x17B5), (0x180B, 0x180F),」
對照:`scripts/lumos:6962-6972` 的 `_PQ_DICP_RANGES`、`_pq_is_default_ignorable`(6962 到 7015 行)與 `_PQ_BLANK_LOOKALIKES`(U+2800、U+FFFC、U+1D159)。
判定理由:
- `_LENS_NAME_INVISIBLE_RANGES` 的九段裡,八段(FE00-FE0F、034F、17B4-17B5、180B-180F、115F-1160、3164、FFA0)已完整落在 `_PQ_DICP_RANGES` 內。
- E0100-E01EF 包含在 `_PQ_DICP_RANGES` 的 E0000-E0FFF 內。
- 第九段 U+2800 就是 `_PQ_BLANK_LOOKALIKES` 的成員。
- 這份新表同時給 `_lens_name_blank` 和 `_LENS_NAME_ESC_CHARS` 用,兩個判定都能直接改用 `_pq_is_default_ignorable(c) or c in _PQ_BLANK_LOOKALIKES`。
- 兩份表還會漂移:DICP 表含 U+00AD、U+061C、U+FEFF、U+2060-206F、U+FFF0-FFF8、U+1BCA0-1BCA3、U+1D173-1D17A,新表沒收。其中屬 Cf 的,`_PATH_SPECIAL_CATS` 剛好兜住。DICP 裡不是 Cf 的碼位,新表兜不住。
- `_PQ_*` 在 `scripts/lumos` 的 6962 行,先於 50574 行定義,lumos 端可以直接用,沒有 import 的限制。
- 掛鉤 `SPEC_NAME_INVISIBLE`(`scripts/hooks/claude/dispatch-lens-hook.py:97-100`)是獨立腳本、不能 import,照抄一份並用測試比對輸出,與既有的 `_spec_name_show` 抄法一致,這一份不列 finding。
- 但抄的來源應該是 DICP 全表,不是又一份手選子集。
佐證:``scripts/lumos: `scripts/lumos:50574-50578` ``、``scripts/lumos: `scripts/lumos:7013` ``

**②**:`_arch_target_lens_split`(`scripts/lumos:44305`)只是呼叫 `_arch_target_split` 並帶上預算和上限參數,比對邏輯只有一套。已讀,無 finding。

**③**:新增的 `_ARCH_TARGET_LENS_*`、`_ARCH_TARGET_RULE_SHOW` 放在同一個 `_ARCH_TARGET_*` 常數區(`scripts/lumos:44131-44143`),命名也一致。總字數上限直接重用 `_LENS_SPEC_TEXT_MAX`,沒有另開 12000。以下兩點不達 major,不列 finding:
- `_arch_target_text` 內有一個裸的 `2000`(`(_LENS_SPEC_TEXT_MAX - 2000) // ...`)。
- `_LENS_SPEC_NODE_FIXED` 這類同性質的估計值是具名常數,這裡沒有,形狀不一致。

**④**:`_arch_target_text` 同時負責出口、加框和上限,與設計審附加段的 `_lens_spec_cap_lines` 加 `_frame_injected` 是同一種分層。兩條呼叫路徑(`scripts/lumos:50301` 和 `scripts/lumos:51285`)都只傳資料,沒有跨層直呼。已讀,無 finding。

**⑤**:`_lr6_mark_spans`(`scripts/test_lumos.py:47917`)配對的是單角引號,`_lr5_frames`(47905)找的是注入框,兩者各管一件事。全檔沒有別的單角引號配對輔助。已讀,無 finding。

最高等級 major,blocking 1 條。
