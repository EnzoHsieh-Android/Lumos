severity: minor

審查範圍是 `646dc3a8`(修後)。我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r3-正確性-sonnet/` 下的獨立 clone 驗證。這輪沒找到會擋合併的問題。寫入鎖的規則本身站得住,漏洞在「拿鎖逾時」那條錯誤路徑,另有兩個小缺口。

**鎖檢查的逐一追查**
- 我用 AST 列出全部 27 處 `atomic_write_verify(` 呼叫,每條都追到入口。
- 全在 `_vault_write_lock` 或 `_vault_locked` 內:set/append/remove、summary、conditions、question-*、決策五支、dref 三支、guard 的 plan/settle/abandon/bind/audit/kill-add/kill-rm、drift fix。
- 沒有「合法但鎖外」的路徑。
- `scripts/` 以外沒有別的模組呼叫它(除測試檔)。
- 全專案的 `atomic_write_verify` 呼叫者與 `_vault_locked` 範圍,我追不出自己卡自己的路徑:
  - 被裝飾的函式之間是可重入的。
  - 被裝飾的函式沒有再啟動 lumos 子程序,只有 `git`,而且有 20 秒逾時。

**測試結果**
- 我跑了 `-k qfm`(171 全綠)、`-k dref`(38 全綠)、`-k decision`(127 全綠)。
- `-k guard` 跑了超過 8 分鐘還沒結束,我中止了,所以守衛子集沒有結果。

**發現**

1. 拿鎖逾時時,三個指令噴追蹤訊息、rc=1,而不是「擋下:」rc2。
   - `decision-amend` 的分派只接 `ValueError`。`guard bind` 與 `guard audit` 的分派整段沒有 `try`。
   - 這三支在修前沒有鎖,這輪才加上 `@_vault_locked`,所以鎖逾時是修補新引進的失敗面。
   - `lumos-cli-write.md` 的 WHY 寫「鎖殘留時這些指令會等 60 秒才回『擋下』」,與實際不符。
   - 同一個分派區塊裡 `guard plan`、`guard abandon` 本來就沒接;它們屬原有漏查,只有 bind、audit、amend 是新增。
severity: minor
   - blocking: 否
   - 引句:「+@_vault_locked」
     - 說明:這個引句在 patch 中出現多次,取自 `cmd_decision_amend` 等處的裝飾器行。
   - 佐證:`scripts/lumos:41595`(`cmd_decision_amend`)、`scripts/lumos:53002`(`except ValueError`)、`scripts/lumos:52827`(`guard bind` 分派)、`scripts/lumos:52830`(`guard audit` 分派)
   - 重現:把 `~/.cache/lumos/vault-lock/<key>.lock` 預先建一個檔,再跑 `lumos decision-amend a_計劃 d2 --field content --text 改`。
   - 修前結果(`c0265db0`):0.6 秒成功,忽略鎖。
   - 修後結果:等 60 秒後丟 `RuntimeError` 追蹤,rc=1。
   - `guard audit` 與 `guard bind` 修後同樣是追蹤 rc=1,已實跑。
   - 歸因:有證據的修復回歸。

2. 鎖檢查只看「有沒有任何一把鎖」,沒綁到被寫檔所在的筆記庫。
   - 拿著 vA 的鎖,`atomic_write_verify` 寫 vB 的檔照樣成功,已實跑。
   - 現在所有入口都鎖自己的 `env.vault`,所以沒有可觸發的實際失效,只是「一條規則保證互斥」的說法比實際強。
severity: minor
   - blocking: 否
   - 引句:「+    if not any(_VAULT_LOCK_HELD.values()):」
   - 佐證:`scripts/lumos:19923`
   - 歸因:有證據的修復回歸。

3. 測試 `t_qfm_frontmatter_writers_take_lock` 的 ② 沒有守到它宣稱要守的事。
   - 註解寫「`--all` 不拿鎖 → ② 翻紅」。我拿掉 `cmd_decision_reindex` 的 `@_vault_locked` 重跑,② 仍綠。
   - 原因:沒鎖時 `reindex --all` 在 `atomic_write_verify` 丟 `RuntimeError`,被迴圈吞掉。測試只檢查 `rcs[1:]` 與題數,沒看 `rcs[0]`,也沒看決策有沒有真的被編號。
   - 實際守住這個入口的是別的 reindex 測試。我拿掉 `decision_amend` 的裝飾器重跑,`-k decision_amend` 有 3 條紅,證明整體還是抓得到。
   - 同一輪缺一支「鎖逾時走『擋下』」的測試,所以發現 1 沒被抓到。
severity: minor
   - blocking: 否
   - 引句:「+    check("② decision-reindex --all 跟六個 question-add 同時跑(三回合):每回合六題都在", not lost, lost)」
   - 佐證:`scripts/test_lumos.py:56481` 附近,該測試函式內
   - 歸因:有證據的修復回歸(新加的斷言)。

4. 圖譜 `規格閘.md` 的「管到的檔」仍列已刪除的 `_pq_git_read_many`。
   - 該函式在這輪被拿掉,程式碼已查無此符號。
   - 同一篇的推送前說明也沒提「改名的計劃會跟舊路徑那版比」。
severity: minor
   - blocking: 否
   - 引句:「-def _pq_git_read_many(rr, specs):」
   - 佐證:`docs/lumos-toolchain-knowledge/Systems/規格閘.md:81`
   - 歸因:有證據的修復回歸。

**對你點名的其餘項目**
- **決策連結的快取鍵 `"\0paths"`:** 快取的其他鍵都是以 `.md` 結尾的相對路徑,不可能撞鍵;全程沒有遍歷整個 dict。
- **新增的行為差異:** 短名與路徑比對改成不分大小寫、NFC。只差大小寫的兩篇筆記現在會被判 `bad`,原本是精確命中。這在 macOS 上不會發生,不構成問題。
- **`_pq_push_remind` 的各種範圍寫法:** 我逐一讀過解析:
  - `a..b`、`a...b`、`..b`、`...b`、`a..`、`a...` 都能得出起點。
  - 改名對照 `{新: 舊}` 的 key 與 `touched` 都是 NFC,所以對得上。
  - `_nodehome_cat_blobs` 回 `None` 時印「跳過」並放行,不改回傳碼。
  - 僅有的小缺點:`_pq_renames` 沒限定路徑,整段範圍都做改名偵測,逾時 60 秒會回 `{}`,等於當沒改名,屬靜默降級。
- **`pq_parse` 的字元規則:** 改用 `_PATH_SPECIAL_CATS` 後,題目文字含 Cf 類字元會被拒,包括 emoji 的 ZWJ 連接符。中文題不受影響。
- **圖譜固定席:**
  - `lumos-cli-write.md`:「所有入口都拿同一把鎖」成立;但「鎖殘留時回『擋下』」只對 set/append/remove、question-*、decision-add/supersede/reindex 成立,對 bind、audit、amend 不成立(發現 1)。
  - `lumos-cli-read.md`:新增的 lint 平台前綴說明與程式一致。
  - `pitfalls-code-loop.md`:`--stage` 那段行為對應的 `-k qfm` 測試全綠。
  - `規格閘.md`:見發現 4。

**三問**

1. **原問題的修復效果有何行為證據?**
   - `atomic_write_verify` 沒拿鎖就丟 `RuntimeError`,已實跑確認。
   - 把 `cmd_decision_amend` 的裝飾器拿掉,`-k decision_amend` 立刻 3 條紅。
   - 決策與 question-* 並發的測試在 qfm 子集全綠。

2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 正常路徑與相鄰路徑成立:27 個呼叫者全在鎖內,可重入,沒有自卡。
   - 錯誤路徑有缺口:bind、audit、amend 在拿鎖逾時時不走「擋下」(發現 1)。

3. **新發現的同一案例在修前、修後各是什麼結果?**
   - 發現 1:修前 0.6 秒成功(沒有鎖);修後 60 秒後追蹤、rc=1。
   - 發現 2:修前沒有鎖檢查;修後跨筆記庫的寫入也不會被擋。
   - 發現 3 與 4 是這輪新增的測試與文件,修前不存在。

總結:這輪沒有會擋合併的問題。上面的 minor 只有第 1 條有實際使用者影響,它發生在鎖殘留時;建議給 `decision-amend` 的 `except` 補上 `RuntimeError`/`OSError`,並替 `guard bind` 與 `guard audit` 加 `try`。
