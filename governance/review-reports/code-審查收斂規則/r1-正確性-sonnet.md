severity: minor

我讀了主 patch 的全部內容,也對照了 review-converge 工作樹裡的 `scripts/lumos`;沒有動工作樹,也沒有跑實驗。測試 patch 沒讀。以下結論都來自讀程式,不是實測。

寫入驗證(決策狀態、checker、只准問一次、合約指紋)大致守得住,沒有發現 major 或 blocker。有三條 minor。

severity: minor
blocking: 否 — 只有索引寫入失敗時才發生,doctor 事後會唸,但重跑指令修不好
引句:「已經有了:{rel[:-3]} 這條合約行尾已經有 [residual:」
問題:`guard residual --add` 先用 `atomic_write_verify` 寫合約行,成功後才呼叫 `_residual_index_write`。索引寫入失敗時,標記已經在磁碟上,指令卻印「擋下」並回 2。失敗原因可能是 `governance/residual-index.json` 是符號連結、硬連結或不是一般檔,也可能是 `mkdir` 或 `_write_lf` 丟 OSError。OSError 不在 `except (ValueError, RuntimeError)` 裡,會直接冒出堆疊。
具體失敗情境:
- 輸入:`--add` 時索引檔是符號連結,標記寫成功、索引被拒,回 2,訊息說「沒有寫」。使用者照指示重跑同一條 `--add`。
- 結果:`ref in have` 成立,印「已經有了」並回 0,沒有重建索引。`--remove` 重跑則回「沒有這個標記」並回 2,同樣不碰索引。
- 影響:索引一直缺這一筆。`_residual_tier_hits` 讀到空索引就回空清單,pitfalls 不升 high,「碰到殘留就走高風險代碼審」這條防線悄悄失效。只有 doctor 的警告會提醒,警告不擋推送;`--reindex` 也沒人在重跑流程裡提到。
佐證:file: `scripts/lumos:19068-19110`(`_cmd_guard_residual_locked`),`scripts/lumos:19030-19043`(`_residual_index_write`)

severity: minor
blocking: 否 — 屬於資料衍生層的漂移偵測缺口,不會誤放行既有分級
引句:「elif sorted(g.get("residuals") or []) != e["residuals"] or sorted(g.get("about_code") or []) != e["about_code"]:」
問題:索引的 `test_files` 只在寫入當下算一次。doctor 比對時用 `with_tests=False`,只比 `residuals` 與 `about_code`,完全不比 `test_files`。
具體失敗情境:
- 輸入:殘留合約綁的測試方法從 `a/test_x.py` 搬到 `b/test_x.py`,或測試被改名。
- 結果:doctor 全綠。索引仍列舊的 `a/test_x.py`,之後改 `b/test_x.py` 不會升 high。
- 附帶:`_residual_test_files` 對測試檔用原文 `finditer`,沒有像 `discover_test_methods` 那樣先剝註解。被註解掉的方法簽章也會被當成測試所在的檔,這邊是多升不是漏升。
佐證:file: `scripts/lumos:19152`(doctor 比對),`scripts/lumos:19033`(`_residual_index_write` 重算)

severity: minor
blocking: 否 — 「只准問一次」的鍵是呼叫者自己取的字串,只能擋逐字重複,擋不了換名重問
引句:「prev = [d for d in rows if d.get("case") == case]」
問題:去重的鍵是 `--case` 的字串比對,大小寫與寫法都算不同鍵。
具體失敗情境:
- 輸入:反例 `c1` 被第二個代理判 `testable`。同一個反例改叫 `C1`、`c1b` 或 `c01` 再問,換個代理重問。
- 結果:全部放行。`--add` 只檢查「這個編號有一筆 untestable」,聽到想要的答案後就能寫殘留標記。
- 同組缺口:`--add` 時 `ref in have` 的早退,會讓同一個決策再加 `--case c2` 時,c2 完全沒被驗證也沒被記錄,卻回 0。
- 第二個代理是不是真的不同的人,也只靠 `--checker` 的自報字串。這部分是設計的天花板,我只列出,不當成缺陷。
佐證:file: `scripts/lumos:18899`,`scripts/lumos:19077`

已讀,無 finding:
- `INV_TAG_RE` 加 `residual` 後的既有呼叫點。`_kill_find_contract` 與 guard audit 都用同一支剝除,合約指紋也一併剝除,加標記不會改指紋。
- 舊合約行、沒有索引的專案。索引不存在且圖譜沒有殘留時,doctor 不唸,`pitfalls` 回空清單,分級照舊。
- 新版寫、舊版讀的相容性。沒有更新的 lumos 不剝 `[residual:]`,只會讓定位多帶一段字,不會崩。
- 殘留索引讀起點與頂端兩版的聯集。可以防住同一個提交把標記和索引一起拿掉再改程式;`A...B` 用 merge-base 起點,單一版本再補讀工作目錄。索引壞掉或缺檔時是空集合,另有 doctor 的警告。
- `loop escape --residual-ref`。`--auto`、`--list`、撤回都會擋。驗證和 `--add` 共用 `_residual_ref_problem`,空字串與 `#dN` 短寫都被擋。`escape-stats` 的 `residual_ref` 計數已排除撤回列。
- doctor 新檢查的例外處理、索引內容壞掉(非 dict、缺 key)時的處理。
- `_gov_vc_gate_events` 從 `_retro_gov_events` 抽出後,行為不變。
- 派工鏡頭徽章。徽章接在 `bidx is None` 之外,平台設定讀不到也照標,用的是未截斷的原文。
- `residual-ask` 只寫版控帳,沒有進本機帳的白名單。

總結:最高 minor,共 3 條,blocking 0 條。
