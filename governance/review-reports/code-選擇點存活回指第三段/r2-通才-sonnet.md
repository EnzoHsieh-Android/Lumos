severity: minor

我只讀了 diff 與相關程式,沒有在本輪跑測試。目前沒找到 blocker 或 major。

先講被刪掉的行為與跨檔追蹤的結論:
- `_kill_revert` 改走 `_kill_mtime_settle` 後,順序沒有變:先等新的一秒、再 `git checkout`、失敗回 None,之後讀回修改時間。字樣沒有動。
- 合批編譯那條「checkout 失敗、直接寫回原文」的路徑,現在跟 `_kill_revert` 共用同一段後半。
- `_choice_layer_write`、`_choice_layer_item_errs` 的呼叫者我都追過,只有 `_choice_layer_record` 一處呼叫主程式碼。
- 簽名改動的另兩處(`_choice_layer_render`、`_choice_layer_split`)呼叫端也都同步改了。
- 寫前預檢的大小算法與 `_note_audit_write_verdict` 一致,同樣是 `indent=1`、`sort_keys=True`、位元組數,兩邊不會判得不同。
- `now` 取自 `kr.plan_of` 的 `["x"]`;被用盡(exhausted)的行已從 `plan_of` 刪掉,會退回掃描時的原 `x`,跟以前行為一樣。

severity: minor
blocking: 否
`scripts/lumos:81415`(`_choice_layer_one_part`)用只放第一個存活、正文另存的材料有沒有超過上限,來斷定「共用的計劃材料本身就超過」,於是整批 20 個不再減半。存活材料(`_choice_layer_item_md`)含包住那一行的整段宣告,沒有大小上限。
- 失敗場景:第一個存活的宣告單獨就超過 200KB,其餘存活都很小。這份會被錯標成「涉及計劃的條款與預期值表本身就超過上限」,並以 20 個存活照出,實際超出上限。修補前是減半到 1 個。
- 觸發條件極窄:宣告要超過約 5000 行。
- 這個判法也沒有測試:`t_choice_layer_split_shared_plan` 的 render 是假函式,只看 `len(its)`。
引句:「if _choice_layer_over(render(chunk[:1], False)):   # 共用的計劃材料本身就超過:減半也縮不下來」

severity: minor
blocking: 否
`scripts/lumos:81242`(`_choice_layer_text`)新增「第 2、3 層取不到 cite 就印『(出處讀不到)』」。修補之前寫成的判讀檔沒有 `cite` 欄位,現在這些舊判讀的出處會顯示成「(出處讀不到)」,而不是原本的段名與引句。
- 若這功能還沒進主線,影響可忽略。
- 新測試只驗了「不印 None」,沒有斷言這個字樣,也沒有測缺 `cite` 欄位的舊檔案。
引句:「        tail = "(出處讀不到)"」

severity: minor
blocking: 否
`scripts/lumos:81166`(`_CHOICE_LAYER_NOT_BODY_RE`)用 `^(?:\S+\s+)?(?:驗收條款|預期值表|審計修正紀錄)` 只比前綴,後面接什麼都算。
- 標題「預期值表的說明」或「驗收條款怎麼讀」這類正常正文節會被整節排除,第 2 層就少了一個引句來源。
- 前綴那一段 `\S+\s+` 也比 `_FOLD_AUDIT_RECORD_RE` 寬,後者只允許 `§數字`。
- `t_choice_plan_sections_variants` 只列了應排除的變體,沒有「前綴相同但不該排除」的反例,所以抓不到過寬。
引句:「_CHOICE_LAYER_NOT_BODY_RE = re.compile(r"^(?:\S+\s+)?(?:驗收條款|預期值表|審計修正紀錄)")」

總結:最高等級是 minor
