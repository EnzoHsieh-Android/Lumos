severity: major

審查摘要:我把 r1 合約席的 M1–M8、M13 在複本裡重做一遍,全部翻紅。接著對 21 支 psrc 測試與相關 spec_gate、doctor 測試另做約 45 道改壞,多數翻紅,有 4 道仍綠,見 F2 到 F4。`t_psrc_hook_generic_message` 是真的讀 `scripts/hooks/pre-push`:我把文案改回舊句後,它翻紅。實驗複本已用字面絕對路徑刪除。`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 下有 603 個 `gctl-run-*`,我分不出哪些是自己的,不能用萬用字元刪,所以沒動,請編排者處理。

F1
severity: major
blocking: 是
引句:「WHY:計劃第一次進 git 的日期只有 _plan_first_days 一套:整個 repo 一次 git log --reverse -M --diff-filter=AR、不限路徑」
同一檔留了一行相反的舊筆記,這輪沒改:`docs/lumos-toolchain-knowledge/Systems/規格閘.md:56` 的 PITFALL 寫「[修法:_plan_first_day 只用 diff-tree -M 逐跳追改名]」,綁 `[test:t_high_risk_evidence_since]`。程式現在是 `_plan_first_days` 整個 repo 跑一次 `git log --reverse -M --diff-filter=AR`,`_plan_first_day` 只是查這份快取(`scripts/lumos:14318`)。「不准用 --follow」的坑仍成立,但寫的修法機制已對不上程式,同檔新 WHY 與它矛盾。下一個 session 會照舊句去找不存在的逐跳追蹤。
建議:改寫那行的 [修法:],並確認綁的測試守得住新機制。

F2
severity: minor
blocking: 否
引句:「        if no not in vis:」
`_plan_sources_uncomment` 對圍欄內的行不去註解,這個分支沒有測試。
- 實驗:把那三行(`if no not in vis: out.append(ln); continue`)刪掉,`-k sources`(135 案)仍全綠。
- 失敗場景:圍欄裡寫了不成對的 `<!--`(例如示範用的程式碼區塊),會把後面真正的〈依據來源〉表吞掉,新計劃被誤擋。
- `t_psrc_section_html_comment` 的四個案例都沒有碰圍欄。

F3
severity: minor
blocking: 否
引句:「    return day >= since」
生效日當天的邊界沒有測試。
- 實驗:`_plan_sources_is_new` 內把 `return day >= since` 改成 `>`,`-k sources` 135 案全綠。
- 把 `c >= since` 改成 `c > since` 也全綠。
- 失敗場景:計劃日期剛好等於生效日時被判舊而漏擋。計劃與預期值表只寫「不早於生效日」。

F4
severity: minor
blocking: 否
引句:「首次加入日的 git log 逾時 → 回讀不到(呼叫端只看 created),並往 stderr 印一行」
`t_psrc_first_day_vault_root` 的翻紅釘寫「路徑前綴寫成 "./"」,但這輪重構後 `_plan_first_days` 已不算前綴,這個釘在原始碼裡不存在,說明與程式不符。
- 我改用 `_plan_sources_prel` 回傳加 `./` 前綴的變異去驗,該測試翻紅,測試本身有效。
- 另外,`_plan_first_days` 裡改名來源的 `nfc(parts[1])` 改成不正規化(`parts[1]`),`-k psrc` 全綠,NFC 這一格沒有測試。
- 兩者都只影響測試說明與覆蓋,沒有具體上線失敗場景。

F5
severity: minor
blocking: 否
引句:「| S1 | 出處是 `https://developer.android.com/studio/write/lint` | 放行 | 本計劃〈用詞〉出處第①種 |」
這輪新增的出處規則沒有進〈驗收條款〉S1 和〈預期值表〉,只靠 Systems 筆記裡的 `[test:]` 綁定。
- 缺的規則:example.com、example.net、example.org 不算出處、未來日期不算、`:行號` 超出範圍不算、符號連結指向 repo 外不算、HTML 註解裡的表不算。
- S1 條款只有「repo 路徑不存在 應 擋」和目錄 `scripts/` 應擋;表裡也沒有目錄那一列。
- 這些行為有 psrc 測試守,所以只是條款與表沒跟上程式。

已確認翻紅的實驗,所有指令形式皆為 `python3.14 scripts/test_lumos.py -k <名>`:
- r1 的 M1(尾行條件改成 `if True:`)、M2(依據來源補法改成 `if False:`)、M3(`bad is None` 改成 `return 0`)、M4(讀不成文字不 append)、M5(分隔列檢查改成 `if False:`)、M6(重複節檢查改成 `if False:`):都紅。M6 要改 `_plan_sources_problems` 內的第三處 `if len(heads) > 1:`。
- M8(改名不接舊日期):`-k psrc_first_day` 紅。
- M13(hook 文案改回舊句):`t_psrc_hook_generic_message` 兩條斷言紅。
- 其餘新測試的改壞,包括:
  - 目錄、符號連結目標、示範網域各一、子網域、未來日期;
  - 節點連結的目錄、`.md` 後綴;
  - 行號驗範圍、改成只看工作目錄(未追蹤檔、`.git/HEAD`、大小寫);
  - 留帳去重(stage 與指紋)、生效日覆寫通知只講一次;
  - doctor 例外不印綠勾、健檢走 `_plan_sources_is_new`、`max` 改 `min`;
  - 逾時退路的 stderr 提示、type 讀不到的提示;
  - 推送前不判新舊、`stage=push` 欄位、`bad = src_bad + bad`、讀不成文字分支:全部翻紅。
- `E_no_abs`(符號連結目標以 `/` 開頭的獨立檢查)移除後仍綠,但後面 `joined.startswith("/")` 已涵蓋,屬等價變異,不算 finding。

總結:最嚴重是 `Systems/規格閘.md` 留著與新程式機制相反的舊 PITFALL 修法句(F1),會擋 1 條(另 4 條 minor 不擋)。
