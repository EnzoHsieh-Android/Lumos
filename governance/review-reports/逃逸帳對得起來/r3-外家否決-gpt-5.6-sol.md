severity: major

## F1 共用追加函式沒有設計宣稱的帳本防護
severity: major
blocking: 是；照字面只靠該函式寫撤回紀錄，符號連結會被跟隨並寫到帳外檔案，漏掉既有帳本安全合約。
引句:「寫入走既有的 `_jsonl_append_verified`(跟記帳同一支,承接它的讀回自驗與帳本防護),不另寫一段開檔追加。」
file: `scripts/lumos:8024` `_jsonl_append_verified` 直接以 `open(path, "a")` 追加，沒有檢查符號連結。
file: `scripts/lumos:9520` 現行手動逃逸記帳另行執行 `log.is_symlink()` 與 `O_NOFOLLOW` 建檔防護，證明防護不在共用函式內。
重現：令 `docs/.escape-log.jsonl` 指向外部檔，再照本節只以 `_vault_write_lock` 包住 `_jsonl_append_verified` 實作 `--withdraw`；撤回資料會寫進連結目標。設計須明定撤回路徑沿用現行符號連結／普通檔案檢查，或把防護真正下沉到共用函式並驗所有呼叫者。

## F2 分母混入永遠收不到自動逃逸的 code 迴圈
severity: major
blocking: 是；照 spec 算出的逃逸率會被 code 迴圈額外分母系統性壓低。
引句:「分母:放行了的迴圈數。放行 = 治理帳有這個迴圈 `kind=converged` 的紀錄(處置閘過關時寫的;設計審與代碼審過處置閘都寫在 `gate=design-loop` 這個閘名下,`nodes` 帶迴圈編號——代碼審通過留痕 `gate=code-loop, kind=passed` 不帶迴圈編號,不用它),而且審查帳裡有這個編號的審查紀錄(排除測試或別的工具寫出、審查帳沒有對應審查的收斂紀錄)。」
file: `scripts/lumos:9426` CI／推送閘自動逃逸由碰到的計劃檔產生迴圈編號；`scripts/lumos:9431` 使用 `_loop_id_for_plan`，只會得到不帶 `code-` 的計劃／設計編號。
file: `docs/.governance-log.jsonl:55222` `收工點名問版本控制` 有 converged；`docs/.governance-log.jsonl:55642` 同一功能的 `code-收工點名問版本控制` 也有 converged。
具體失敗：同一功能先過設計審、再過代碼審，之後 CI 自動記一筆逃逸。分母依本文納入兩個迴圈；自動列只歸到不帶 `code-` 的設計編號。本文又只按「分級 × 範圍類」分組，未按 `loop_kind` 拆開，兩個迴圈會落進同格，結果成為 1/2；code 迴圈即使漏掉同一缺陷，也永遠保持無逃逸。需定義各 loop kind 各自的分子歸因與分母，或排除沒有對應逃逸寫入路徑的 code 分母。

## F3 回退會把撤回紀錄本身算成新逃逸
severity: major
blocking: 是；照回退段執行後，治理統計與規則缺口會產生不存在的逃逸資料。
引句:「撤回與 `loop_kind`、`defect_ref` 規矩:還原寫入端、`_escape_rows_for` 的參數與各讀者的過濾;已寫進帳的撤回紀錄與新欄位留著——但撤回會失效,被撤的列重新被算,舊版 `--list` 會把撤回紀錄印成可疑列。回退說明要寫這兩點。」
file: `scripts/lumos:7397` 現行 `_escape_rows_for` 對任何可解析 JSON 直接呼叫 `d.get` 並回傳；撤回物件在回退過濾後會被當一般逃逸列。
file: `scripts/lumos:6743` `gov --stats` 直接以 `_escape_rows_for` 回傳長度當逃逸筆數。
file: `scripts/lumos:20238` `rule-gap` 對每列取 `rule`；撤回紀錄會被計成一筆未標規則。
重現：先有一筆逃逸，再追加一筆撤回，依回退段移除讀側過濾但保留兩列。`gov --stats` 會報兩筆逃逸而非一筆，`rule-gap` 也會多一筆未標規則；不只是文中承認的「原逃逸重新被算」與舊 `--list` 變吵。回退必須保留最小的 `kind=withdraw` 跳過邏輯，或明定回退時另行封存／遷移撤回列。

## F4 缺佐證理由沒有定義帳本欄位
severity: minor
blocking: 否；核心寫入仍可實作，但不同實作者可能只驗旗標而不保存理由，稽核輸出會失去一致格式。
引句:「兩個都沒有時,要另給 `--missing-defect-ref "<為什麼沒有>"`」
本文沒有定義理由落帳的欄位名，也沒有條款要求 `--list` 或 escape-stats 顯示／區分「有理由缺佐證」與舊版無理由列。應明定例如 `missing_defect_ref` 的持久化形狀與讀側呈現。

已看,無: 第一節排除 `kind=spec-gate` 的判準與現行帳形一致；代碼審自動逃逸刻意去掉 `code-` 的現況成立。第二節現行手動 `--sha` 確實未落帳，修正方向成立。第三節的目標驗證、重複撤回防護、撤回不能再撤、`--list --withdrawn` 修飾關係、非物件 JSON 跳過及自動去重須包含已撤列，除 F1、F3 外可執行。第四節所稱代碼審處置閘也產生 `gate=design-loop/kind=converged` 已由帳本驗證；r2-intake 對該項判 MISS 正確，現帳為 258 筆 converged，其中 code 編號 173 筆、114 個不同迴圈。`_loop_anchor_tier` 取第一筆帶 tier 的行為、146 個 code 迴圈中 33 個未定錨、`_plan_for_loop` 現況及 NFC 修正落點均核對。`loop next`、`loop status --disposal`、`canary record`、`quote-check`、`loop escape`、`gov` 的現行旗標皆經 `--help` 核實；新增旗標與 `escape-stats` 尚未實作屬本案預期。所有 wiki 交叉引用可解析，指定計劃與 `Systems/loop-convergence-recording`、`Projects/逃逸自動記_計劃`、`Projects/自主審查量尺_計劃` 均無已登記的「動了會壞」合約；本設計保持 append-only、既有自動去重與收斂事件形狀，除上述 findings 外不破壞其宣稱。r1、r2 修正紀錄與兩份 intake 對得上。實務隱患逐類：併發——撤回確認與自動記共鎖、重複撤回在鎖內重驗，無新增問題；效能——約 15MB 帳本只由手動／週報唯讀，且不進閘，無 blocking；守衛面——有影響，符號連結缺口見 F1；金流——無，只處理本機帳本；對外送出——無，不呼叫外部服務；不可逆——正常路徑只追加且可用撤回沖銷，回退失真見 F3。

總結:最高 severity major，blocking 共 3 條。
