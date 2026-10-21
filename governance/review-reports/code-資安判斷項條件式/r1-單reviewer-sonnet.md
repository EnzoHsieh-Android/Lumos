severity: minor

正確性資料狀態五問、`_secev_kind_verdict` 的 base 與 need_h 兩條路、怪值輸入都核對過,沒找到 blocker 或 major。我另外在 `secev-judgments` 實跑了 `-k secev_s62_cond`(9 passed)與 `-k s40_s62`(6 passed)。以下兩條是 minor。

核對結論:
- **舊紀錄**:舊版的 6 項全蓋人審紀錄,在新判定下仍是 qualified,不會誤擋也不會意外放行。
- **人審簽章**:`content_sha256` 蓋的是整份紀錄的 `judgments`,這次沒改簽章內容的算法,所以簽章、payload、security list 的輸出不受影響。
- **base 與 need_h**:`base = 全部 − 條件式`,所以兩個新條件項不在 base,不會被「誰都要蓋到」連坐。條件成立時,`extra_judgments` 帶進 need_h,必須有 human 蓋到。`manual_check_scope` 的路徑沒有被改動。
- **required_evidence 怪值**:`_secev_format_judgments` 只留字串項,重複、未知種類、空清單都得到空集合,不會崩。非列表的值在更早的 `_secev_control_table` 就已經處理過。
- **替代欄**:掃描種類被替代欄換掉後,必要種類裡沒有 SARIF 種類,校準就不要求,這是合理的。
- **測試**:t_secev_s62_conditional_judgments 的前置斷言(預設護欄沒有壓測或掃描類種類)有檢查。我推演了拿掉 `_secev_format_judgments`、把兩條映射對調兩種變異,③ 的 concurrency 與 static_analysis、dynamic_scan 案例都會翻紅,不是把實作抄一遍。改過的 t_secev_s40_s62_reviewer_kind 改驗 legit_control_real 沒蓋,仍然成立。

F1 條件看「種類允許哪些格式」而不是實際用了哪種格式,concurrency 只用 JUnit 證明時也被要求人蓋門檻
severity: minor
blocking: 否
引句:「return {j for j, fmt in _SECEV_JUDGMENT_FORMATS.items() if any(fmt in _SECEV_KIND_FORMATS.get(k, ()) for k in req)}」
``file: `scripts/lumos:8474` `` `_SECEV_KIND_FORMATS` 的 `concurrency` 允許 `("k6_summary", "junit")`。

- 場景:一條護欄的必要種類有 `concurrency`,證據是 JUnit 並發測試(沒有 k6、沒有任何門檻)。
- 預期:跟授權護欄一樣,沒有門檻就不該要人替不存在的門檻背書(這是 d20 的動機)。
- 實際:`concurrency` 只要允許 `k6_summary` 就會把 `threshold_meaningful` 加進 need_h,人審沒蓋就判 `missing:human_review_missing`。
- 方向是多擋、不會漏放,所以不算 blocker。d20 的 trade_offs 只講了漏列 concurrency 的情況,沒講這個多擋的情況。

F2 舊決策 d8 還是 valid:true,內容仍寫 not_applicable_sound 要人,與新決策 d20 衝突,沒標被取代
severity: minor
blocking: 否
引句:「alternatives: "甲=照舊全部要人;乙=條件式加放寬兩項(本案);丙=全部改成 AI 審也算"」
``file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:135` `` d8 的 content 仍列「門檻有沒有意義、校準樣本有沒有代表性、不適用理由成不成立」為 ai 審放行不了的判斷。

- 場景:下一個 session 先讀到 d8,會以為 `not_applicable_sound` 與無條件的門檻、校準仍要人。
- 預期:d20 部分取代 d8 時,d8 該有被取代或限縮的標記。
- 實際:d20 的 diff 沒有動 d8。程式現況與表格是對的,只有決策紀錄互相矛盾。

最嚴重 severity: minor,blocking 共 0 條
