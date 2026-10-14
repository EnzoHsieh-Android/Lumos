severity: minor

主程式的 `--keep-going` 收尾、`push-summary` 的參數檢查、掛鉤的陷阱與 bash 3.2 搭 `set -u`,我都讀過也實跑過,沒找到 major 以上的問題。找到三條 minor。

**我實跑過的**
- 簡版彙總函式用 `/bin/bash` 3.2.57 跑:tab、換行、反斜線、空 ref 的 `-` 都正確。
- `push-summary` 用真的 lumos 跑:`--count -1` 回 2,`--count 0`、暫存檔不存在、`--repo` 指到不存在的路徑都回 0 並印出彙總。
- 用真的 lumos 跑 `code-loop check --help`:有 `--keep-going`、rc 0;`code-loop pass --help` 沒有,探測不會誤判。
- 為了驗證變異,我把 `scripts/` 等目錄複製到 scratchpad 改過,跑了 `-k prepush_` 的 212 支測試。結果 211 過 1 敗,唯一的敗是複製時沒帶 `.github/workflows/ci.yml`,與變異無關。實驗目錄與測試現場都已刪除。

severity: minor
blocking: 否 — 只讓彙總少一行,擋下與否不受影響
引句:「g, r, w = (x.strip() for x in parts)」
問題:`cmd_push_summary` 用 `raw.splitlines()` 切暫存檔。Python 的 `splitlines` 也會在 U+2028、U+0085 這類字元斷行,而 git 允許 ref 名帶這些字元。
具體失敗情境:ref 名含 U+2028 的那一筆被切成兩段,各只有 2 欄以下,整筆被 `len(parts) != 3` 丟掉。
實測:我造了含 U+2028 ref 的兩列暫存檔,印出「2 筆擋下(1 道閘)」,只剩 doctor 一列,home 那道閘消失,另加「有 1 筆的原因沒寫進暫存檔」。
連帶影響:治理帳的 `gates_n` 與 `gates` 也少一道。掛鉤端的簡版彙總按 `\n` 讀,不受影響,所以兩種彙總會不一致。
建議:改用 `raw.split("\n")` 切。
佐證:`prepush-collect/scripts/lumos` 的 `cmd_push_summary`;`_esc_clean` 刻意不清 U+2028,所以消毒也補不到。

severity: minor
blocking: 否 — 擋下照常,只是終端多一行雜訊
引句:「printf '%s\t%s\t%s\n' "$_g" "$_r" "$_w" >> "$_PP_TMP/blocks" 2>/dev/null || true」
問題:`2>/dev/null` 寫在 `>>` 之後。bash 先處理 `>>`,開檔失敗的訊息會在 stderr 被導走之前就印出來,所以 `|| true` 擋不住這行雜訊。
具體失敗情境:暫存目錄被刪時,終端會多印 `line N: …/blocks: No such file or directory`。我用 `/bin/bash` 3.2 實測:不加 `2>/dev/null` 時有這行;外層加 `2>/dev/null` 才消失。
測試缺口:`t_prepush_block_survives_lost_record` 的 ④ 只檢查 rc 與「沒寫進暫存檔」那句,沒檢查雜訊。
建議:改成 `{ printf ... >> "$_PP_TMP/blocks"; } 2>/dev/null || true`。
佐證:`scripts/hooks/pre-push` 的 `pp_record_block`。

severity: minor
blocking: 否 — 屬測試力度,不是行為錯
引句:「IFS=',' read -r -a _cl_ks <<< "${_cl_bl#LUMOS-BLOCKS:}"」
問題:掛鉤測試從沒餵過兩個以上的種類。`FAKE_CL_LINE` 只出現 `review`、`NONE`、空行、`weird_kind` 四種單值。多種類只在行程內的 `t_code_loop_check_keep_going` 驗到 python 端印出什麼,從沒走過掛鉤的 `read -a` 與逐筆記帳。
變異實證:我在記帳迴圈裡 `pp_record_block` 之後加 `break`,只記第一個種類。`-k prepush_` 的 212 支測試全綠。
沒被守到的行為:`bound_tests,review` 這種多種類各記一筆,以及 `tail -n 1` 取最後一行、`${_k// /}` 去空白、`a,,b` 的空元素。
連帶影響:計劃宣稱的主要效果「代碼審多原因各列一筆」,掛鉤端沒有任何測試守著。
建議:加一個 `FAKE_CL_LINE="LUMOS-BLOCKS: bound_tests, review"` 的案例,斷言彙總 2 筆、1 道閘;再加一個兩行 `LUMOS-BLOCKS:` 的案例,斷言只取最後一行。

**已讀,無 finding**
- 掛鉤邊界:`_PP_NREFS` 計數(刪除行、tag、空 stdin 都不誤算);`pp_stop_if_signaled` 與九道閘的 rc 語義;`read -r _ _lsha _ _` 在 bash 3.2 下可用。
- 主程式:`_fin` 收尾對所有放行站點的處理;pitfalls 失敗(三種)時新增告警閘照跑(`_lint_step`,tier 用 `unknown`,測試 ③④ 有守);`reason_kind` 對照表四個種類與 `pp_cl_reason` 一致;不帶 `--keep-going` 時行為不變(有逐字黃金輸出比對)。
- `LUMOS-BLOCKS:` 其餘壞形狀(缺行、空行、未知種類)都會至少記一筆,有測試守。
- 假 lumos 的搭法能走到每一道閘(逐道單獨擋、後面的閘照叫、混版、簽名中斷、TERM 時的背景工作)。

最高等級 minor,blocking 共 0 條。
