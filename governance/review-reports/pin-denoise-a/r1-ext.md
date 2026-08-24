# 外部審稿結果

## 摘要／立案

已讀，無 finding。

## 症狀

已讀，無 finding。

## 診斷

已讀，無 finding。實碼確認：

- `_impact_contract()` 的實際值域為 `IRREVERSIBLE`、`INVARIANT`、`RISK·<risk tag 值>`、`None`；`DEBT` 不算合約。
- `RISK·守衛面` 來自 frontmatter 的 `risk/守衛面` tag，不是硬編碼的完整字串。
- 現行 indirect 保送字面條件確為 `if contract and hop <= min(eff_depth, _pin_hop)`，因此所有 `RISK·*` 都會保送。
- hop 不會是 0：direct 另桶處理，BFS indirect 的 hop 定義為 `1..depth`。

## 反事實

### f1 — blocker

spec 段：反事實／主案第 3 項「治標籤」

引句:「被誤降的必看 3 條:E06/E12 `anchor-integrity`(守**所有** hook,about_code 卻只標 pre-push)」

問題：這三筆不能直接定性為「about 漏標」。前案已經三輪審清楚：`about_code` 表示「這篇主要在講哪支檔」，是必看集合的高精確度子集，不等於「改此檔會受它影響」。前案甚至用同一個 `anchor-integrity` 案例證明 about 與 impact 是兩個欄位，並明載 held 的第三筆 `design-loop → test_autonomous_loop.py` 可能是考卷標寬、不得回頭裁。投稿卻把這些負例直接補進 about，等於為了讓 R1 過卷而改寫欄位語意及答案，會把 about 從「關於」污染成「影響」，日後所有依賴 about 精確性的排序、巨檔門檻與人工標註規範一起失真。

這不是普通補資料，而是以修標籤掩蓋降級規則的召回缺口；必須先做人核裁決「金標錯、about 錯，或其實需要 impacts_code」，不能預設三筆全補 about。

查證：

- `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:222-230`
- `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:239-258`
- `docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md:70-73`
- `docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md:85`
- `docs/lumos-toolchain-knowledge/Verification/2026-08-23_影響欄位離線驗證.md:28-44`

## 主案：硬合約保送＋about 豁免＋治標籤

### f2 — blocker

spec 段：主案第 2 項／實務隱患召回風險

引句:「被 1 降級的節點若 `about_hit`(語意上真的關於這支檔、stamp 未過期)→ 留固定席。」

問題：此豁免依現碼無法覆蓋巨檔。`about_hit` 不只要求路徑命中且 stamp 有效；當某檔被至少 `LUMOS_IMPACT_ABOUT_MAX` 篇標記時，`_impact_mark_about()` 會在掃任何結果前直接返回，預設門檻是 8。也就是巨檔上的 RISK indirect 全部拿不到豁免，正好落入 spec 未處理的「降自由席→動態閾值→top/quota 截斷」路徑。

自由席實際不是「排隊後總會輸出」：先受 `max(0.20, 0.65 × max_free)` 門檻，再受最多 8（且 quota 10）的名額限制；既有 rescued 只挑 `kind == direct`，完全不救 indirect。因此未在 goldset 的真正必看 RISK indirect 可能被靜默砍掉。spec 所稱「about 豁免＋治標籤＋棘輪三層接」在巨檔上實際只剩 goldset 棘輪一層；過期 stamp 也同樣失去豁免，而 spec 沒有另定 fail-safe。

需明確裁定巨檔與過期的行為，例如把「豁免用 about」和「排序加分用 about」拆開門檻，或為被降級的 RISK indirect 設獨立召回桶／上限；不能直接復用現有 `about_hit`。

查證：

- `scripts/lumos:14108-14131`
- `scripts/lumos:14469-14475`
- `scripts/lumos:14483-14497`
- `scripts/lumos:14498-14521`
- `scripts/lumos:7736-7740`
- `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:280-290`

### f3 — major

spec 段：主案第 4 項／實務隱患回滾

引句:「總開關 `LUMOS_IMPACT_HARD_PIN`(預設?——★開關預設值走考卷:train 掃、held 驗一次★),0=舊制逃生。」

問題：關鍵上線語意仍未決，且「一顆開關可回滾」不成立。

第一，預設值是正式行為合約，不應留成 `預設?` 交給一次 held 觀測後決定；還需定義非法值、未設定值、是否只包 indirect pin 謂詞，及關閉時是否連 about 豁免一起停用。現有 `_impact_knob()` 是浮點解析、非法值回預設的評測旋鈕，docstring 明言不是使用者旗標；不能僅列一個名字便視為具備產品級逃生門。

第二，第 3 項會永久修改圖譜的 `about_code`／stamp。即使 `LUMOS_IMPACT_HARD_PIN=0` 恢復舊固定席規則，補標仍會改變既有固定席內 about 排序，所以不會逐 byte 回到舊行為。spec 沒有列出這批人工修正的精確清單、provenance、撤回方法或驗證方式。

查證：

- `scripts/lumos:14134-14139`
- `scripts/lumos:14476-14487`
- `scripts/lumos:7723-7749`
- `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:292-297`

## 已試已殺

已讀，無 finding。

## 尺

### f4 — blocker

spec 段：尺／實務隱患召回風險

引句:「**must_in_out 棘輪**:硬底線,掉一個就紅(擋 R1 誤傷)。」

問題：現有棘輪不足以保證「held 掉一個就紅」。不帶 `--split` 時雖然會產生 all/train/held 三份報告，但棘輪只選 `_rat_split = "all"`，以全體 `must_in_out_count` 比最近同 goldset revision 的 PASS。若 held 少一筆、train 多一筆，全體數量不退，棘輪可通過；這與 spec 的 held 單次驗證及「掉一個就紅」直接矛盾。

此外，換 `goldset_rev` 或找不到同 revision PASS 時，棘輪會無條件放行並把本次結果建立成新基線。因此第 3 項一旦補標或調整答案造成 revision 改變，恰好會讓本案最依賴的召回守衛失去比較基線。`pin_noise` 現況也只印不閘，而 spec 仍寫「考慮進閘」及「顯著降」，沒有可執行門檻。

在以 RISK indirect 主動換取精度的變更中，這會允許 held 召回退化或換尺後退化仍通過。需先新增 per-split 棘輪，固定舊／新相同 goldset revision 與基線，並把固定席噪音的成功條件定成可機械判定。

查證：

- `governance/eval/retrieval_eval.py:473-505`
- `governance/eval/retrieval_eval.py:589-618`
- `governance/eval/retrieval_eval.py:409-438`
- `governance/eval/retrieval_eval.py:464-470`
- `governance/eval/retrieval_eval.py:420`

## PRIOR-ART

已讀，無 finding。

## 實務隱患

- 召回：有 blocker，見 f1、f2、f4。
- 守衛面：有 blocker；現有尺不能證成 held 零退化，見 f4。
- 回滾：有 major；開關不能撤回治標籤造成的排序變化，見 f3。
- 效能：無否決級問題。若復用現有 `_impact_mark_about()`，正文雜湊讀盤本來已存在；新 pin 判斷本身是常數時間。但 spec 的「無新讀盤」只在確實復用既有結果時成立。
- 併發：無否決級問題。設計只讀環境變數與行程內快取，未新增共享寫入或鎖；圖譜人工補標的多人協作衝突屬寫入流程問題，已由 f1／f3 涵蓋。
- hop=0：無；indirect BFS 明定 `1..depth`，direct 另桶。
- direct RISK：無；現碼 direct 的 `pinned = bool(contract)`，spec 明確說 direct 不動。
- about 過期：有 blocker；過期即無豁免且无替代召回層，併入 f2。

## 下一步

已讀；但在 f1、f2、f4 解決前，不應進實作。

最嚴重 severity：blocker
