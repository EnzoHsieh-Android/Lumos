severity: minor

### F36 清單欄位的純空白純量值被誤判成「非空」,append 後留下永久垃圾項
severity: minor
blocking: 否 — 不會崩潰、不會丟真資料,只是靜默多寫一筆垃圾項且 rc0 顯示成功
引句:「清單欄位的單一值寫法(`key: 值`)讀出那一個值(去引號,空的回 "")。」
佐證:file: `scripts/lumos:10676` `t = sval.strip()` 只把「去引號後的純空白」用在判斷式(`t=="[]"`、`t.startswith(...)`),沒有用在回傳值
佐證:file: `scripts/lumos:10684` `return sval` 回傳的是未 strip 的 `sval`,純空白引號值(如 `"  "`)在此仍是非空字串
佐證:file: `scripts/lumos:10699` `_list_key_scalar_to_list` 的 `if sval:` 把這個非空白字串判定為「有值」,插入成清單第一項
1. 重現(已在 `/tmp` 跑過,不動 repo):`about_code: "  "` 的筆記跑 `lumos append <note> about_code src/c.ts`,rc0 印「✓ append」,寫回的檔案卻是 `about_code:\n  - "  "\n  - src/c.ts`——多出一筆看起來是空但其實是非空字串的垃圾項,且此欄位在本 PR 的合約是「0~3 支程式檔的清單」。
2. 同一條路徑對 `tags` 等一般 LIST_KEYS 欄位也重現(`tags: "  "` → append 後變成 `tags:\n  - "  "\n  - newval`),不是 about_code 專屬。
3. 對照:未加引號的空白(`tags:   `)與帶方括號的空清單(`tags: "[]"`、`tags: ' [] '`)都已正確回傳空字串,只有「引號包住的純空白」這個形狀漏判——`_list_scalar_value` 判斷用 `t`(已 strip)、回傳用 `sval`(未 strip)兩個不同變數,是這條新函式自己的邏輯縫隙,`atomic_write_verify` 的自我檢查只驗「原項沒被砍」,抓不到這種「憑空多一項」的寫壞。

## 第三輪修法驗收
F19:修到 — `_multi_link_value` 讀寫共用同一判斷,QB/QC 等繞法與清單項寫法均已擋下(直接呼叫 `parse_frontmatter`/`_list_scalar_value` 驗證一致)
F20:修到 — 總結句正則改成只認行首,「## F1 總結」「內文提到總結句/最高並發」等不再誤擋,零條豁免只剝「等級字+0 條」不誤剝「0 台/0/1/0day」(逐條 regex 實測全部符合預期)
F21:修到 — `about_code` 反斜線寫法收下並存成正斜線(`src\a.ts` → append rc0,存成 `src/a.ts`,實測)
F22:修到 — `_about_code_key` 以磁碟真實拼法為準,新增項與舊大小寫錯字項判同一支檔、不疊第二筆
F23:修到 — 目錄可執行不可讀(0o111)時 `_disk_spelling` 回讀不到、`_about_code_path` 擋下並講明「讀不到目錄」(實測)
F24:修到 — `_vendored_state` 以內容指紋比對「原封不動」,改過內容的工具檔(指紋清單未同步)仍被掃到,`t_pitfalls_diff_ignores_vendored_toolchain` 全套(①–⑧)實跑皆綠
F25:修到 — `_vault_write_lock`+`_write_lf` 改 `mkstemp`,8 個併發 `append` 全部 rc0、8 項全部落盤、無殘留暫存檔(實測非測試套件內建案例)
F26:修到 — symlink 別名與正式路徑經 `_about_code_key` 判同一支檔,append 不疊、remove 雙向都刪得掉
F27:修到 — `tags: [a]`(無逗號)擋下訊息改為「同一行的清單」,不再提「逗號」(實測)
F28:修到 — `grep` 全檔搜尋確認路徑正規化只剩 `_posix_norm` 一份,`_about_code_key`/`_impact_about_counts`/`_impact_mark_about`/vendored 判別皆共用,無殘留的第二套實作
F29:修到 — `_impact_mark_about` 改用 `_posix_norm`(會解 `..`),讀碼確認與 append 寫入側同一套
F30:修到 — `verified_by` 同行清單擋下時,`lumos new verification --systems` 仍印「筆記建好了」且新筆記確實落盤(實測)
F31:修到 — 單一值轉清單時原始帶引號項原樣保留(`'[[Systems/API "v2"]]'` 不被重新加反斜線引號),程式碼路徑與測試 ⑨c 一致
F32:修出新洞 — 「同一行清單」偵測本身(QA–QH、`[a]`、`[[A]],[[B]]` 等)已修好,但同一支新函式的「空值判定」邏輯本身出現獨立新洞,見 F36
F33:修到 — `remove` 對同一支檔的多種寫法(`src/../src/a.ts` 與 `src/a.ts`)一次全部拿掉(讀碼+測試 ⑫ 一致)
F34:修到 — `_need_src` 只在來源 repo 跑漂移測試,消費端模擬套件(`t_vendored_consumer_srconly_skip_regression`)實跑全綠、且正確記成 skip 非靜默綠
F35:修到 — 安裝只複製精確清單,對真實 repo 執行 `git ls-files` 比對 `_VENDORED_TREE_FILES`,結果完全一致(零缺漏零多餘)

風險掃描清單:
- `scripts/lumos:10902`(`_vault_write_lock` 的 `open(...)`):誤報 — 開檔後有 `try/finally: fh.close()` 保底關閉,不是未關閉的資源
- `scripts/lumos:17884`:誤報 — 命中的是 docstring 裡描述舊事故的文字「命中 open(...)」,不是真的函式呼叫

總結:最高 severity minor,blocking 共 0 條
