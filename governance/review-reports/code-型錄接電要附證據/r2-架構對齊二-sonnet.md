severity: clean

我讀了 `r2-repair-code.patch` 全文,對照 `check.py`、`kotlin規則包.md`、`test_lumos.py` 的鄰近寫法。沒有找到「跟既有做法不一樣」的地方。上一輪架構對齊 b1 到 b5 都折進去了,折法也沒另起第二種做法。我沒有跑測試。

## 1. 分層與依賴方向

結論:對齊。

- `_batch4_have` 仍是 `check.py` 裡的私有輔助函式,只被 `_wiring_row_problems` 呼叫(`check.py:442`,全 repo 只有這一處呼叫)。問題清單照舊層層往上回傳,最後由 `catalog_problems` 彙總。新增的位置檢查沒有直呼別層。
- 回傳形狀 `(值, 問題清單)` 跟同檔鄰居一致:`dt_evidence_parse` 的 `return None, ["證據樣式要寫成「主:… ;例外:…」"]`(`check.py:195`)、`dt_row` 的 `return row, []`(`check.py:240`、`check.py:249`)。新函式的 `return None, []` 與 `return [...], probs` 走同一套。
- 測試改成只經 `cp.catalog_problems(cp.load_rules())` 讀複本,不再直呼 `wiring_problems`,這就是 b5 要的。依賴方向是測試呼叫總檢查,而不是呼叫內部的步驟。

引句:「        allp = cp.catalog_problems(cp.load_rules())」

## 2. 命名與寫法

結論:對齊。

- b1:列層級兩條訊息都補上〈接電證據〉開頭。現在 `_wiring_row_problems` 與 `_batch4_have` 的訊息都以〈接電證據〉起頭,跟同檔 `_wiring_entry_problems`、`_wiring_source_problems` 的訊息一致(`check.py:419`、`check.py:455` 之後各條)。`pending_problems` 的〈待查證〉前綴(`check.py:562`、`check.py:565`)也是同一寫法。測試的過濾條件同步收斂成單一 `startswith("〈接電證據〉")`,不再需要 `("〈接電證據〉", "通電批次")` 兩種前綴。
- 同一個函式裡 `probs` 的累加與 `out += where` 的併入,跟鄰居的 `out = []`、`out.append`、`return out + ...` 同形。
- 新增的測試沿用同函式既有慣例:`mutate(...)` 一道一個改壞、`check("★前置★ …")` 守前提、註解標「代碼審 r1 審查席 a1/a2」。代碼審註解的寫法跟 `test_lumos.py:126851` 的「代碼審 r1 審查席 1、2、3」同形。
- 筆記端:舊 REVISIT 加 `[closed:2026-11-08 理由]`,格式跟 `存量漂移守衛.md:49` 寫的 `[closed:日期 理由]` 以及 `筆記內容審.md:80` 的用法一致(b3)。公開名稱例外的 WHY 補在 `kotlin規則包.md:61`,並指向 `situation_dir` 這個既有例外(b2)。

引句:「+  WHY:check.py 的 wiring_table、wiring_dir 不加底線,是給測試讀判定表與樣本目錄用(同 situation_dir 的例外)」

## 3. 第二種做法

結論:沒有。

- 批四括號的位置檢查直接用既有的 `_BATCH4_RE`(`check.py:372`),沒有另寫一套比對。
- 在 `_batch4_have` 內部加檢查,而不是在測試或別處另立一套判斷,符合 `kotlin規則包.md` 那條「不在測試裡另立一套」的 WHY。
- b4 的折法是在 `kotlin規則包.md:60` 新增一條 RULE,講樣本要隨壞寫法欄重寫、用 `[retire:when-gone:…/samples/lint-wiring]` 綁住樣本目錄。我另外查了這條 RULE 的欄位:`[依據:審計]` 屬於 CLAUDE.md 列出的 `[依據:人|外部|審計|法規|相容]`,`[since:]`、`[retire:]`、`[confirmed:]` 也都寫齊。同檔另一條 RULE(第 26 行)只寫了 `[依據:外部]`,這條比它完整,沒有偏離。
- `closed` 與 RULE 沒有引入新的欄位或前綴。

引句:「+  RULE:改了型錄某列的壞寫法欄或現成規則欄,那列〈接電證據〉的真跑樣本要照新的壞寫法重寫、照範本設定重跑,判定照結果改」

不對齊共 0 條,其中 major 0 條
