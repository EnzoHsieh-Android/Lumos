severity: major

# 鏡頭:正確性與邊界

## 發現一:lint 新測試的第 3 條斷言測不到它宣稱要測的東西(vacuous assertion)

`t_lint_warns_empty_revalidate_when` 的第 3 段(驗 `valid_under` 空著要出聲)拿節點名
`Verification/前提空的.md` 來測,斷言寫成 `"前提" in r.stdout or "valid_under" in r.stdout`。
問題是 lint 的輸出格式一定會印出被檢查的檔路徑(例:`lint Verification/前提空的.md`),
而這個測試節點的檔名本身就叫「前提空的」——所以不管底下那段 `valid_under` 檢查有沒有存在,
`"前提"` 這個字都會出現在 stdout 裡(來自檔名,不是來自警告訊息)。

我實測驗證:把 `scripts/lumos` 還原回這個 patch 之前的版本(即拿掉整段
`valid_under`/`revalidate_when` 檢查),重跑這支測試——

```
python3 scripts/test_lumos.py -k t_lint_warns_empty_revalidate_when
```

結果:5 個斷言裡只有第 2 條(檢查 `revalidate_when`,節點名叫「沒寫的」,不含觸發字)
真的翻紅;第 3 條(檢查 `valid_under`,節點名叫「前提空的」)在功能完全不存在的情況下
依然印出 `✓`。也就是說,測試自己在檔頭寫的「翻紅釘:把那段檢查拿掉 → 第 2、3 條翻紅」
是假的——只有第 2 條會真的翻紅,第 3 條不管拿不拿掉都是綠燈,對 `valid_under` 這個欄位
完全沒有回歸保護。

這正好命中鏡頭 3 要查的東西:「新加的測試……有沒有斷言到的其實是別的東西?」——這裡斷言到
的是檔名字串,不是警告訊息本身。而 `valid_under`/`revalidate_when` 兩個欄位正是這次修法要
解決的鐵則四(承認風險要附回頭看的條件)缺口,這條測試理論上該是這個功能唯一的機械防線,
結果一半形同虛設。

引句:「check("★前提欄空著也要出聲★(不寫前提=不知道這個結論在什麼條件下才算數)",
              "前提" in r.stdout or "valid_under" in r.stdout, r.stdout[:300])」

`路徑:scripts/test_lumos.py:42200`(對應本次 diff 內文中 `t_lint_warns_empty_revalidate_when`
函式內的第 3 段斷言;行號依目前 HEAD 版本計)

修法建議:把該節點改名成不含「前提」/「valid_under」的中性名字(例如「甲」),或斷言改抓
更精確的子字串(例如警告訊息裡的固定片語「這個結論在什麼前提下才算數」),讓斷言真的綁在
警告內容上而不是巧合的檔名上。

severity: major
blocking: 是

---

## 查證所得(佐證用,非本次發現的獨立問題)

以下是我為了排除疑慮做的查證,結論是「沒問題」,附在這裡讓下一個看這份報告的人不用重查:

- **`rel-cascade visited` 是否會汙染既有折疊/判定邏輯**:`_ledger_fold` 用
  `(neighbor, edge_type, from_decision_id)` 三元組、`all(k)` 過濾。`visited` 事件只帶
  `from_decision_id`,沒有 `neighbor`/`edge_type`,`all(k)` 必為 False,所以無論如何都不會
  被折進 `state`,不影響 `confirmed`/`pruned` 計數,也不影響 `resume`/`confirm`/`prune` 的既有
  判定路徑。`cmd_rel_cascade_list` 算「最後活動時間」`last` 時確實會把 `visited` 的 `ts` 算進去
  (`all_ts` 收 header+trans 全部有 `ts` 的項目)——這是刻意的、正是文件宣稱的「讓體檢不再嘮叨」
  的機制,不是汙染。
- **「只有待辦單真的空才准記」這個保證有沒有繞得過去**:`cmd_rel_cascade_visited` 每次呼叫都
  重新 `_ledger_read` + `_rel_cascade_pending` 現場重放帳本與展開鄰居,不接受呼叫端自報空/不空,
  我用一支有 `verified_by` 連回決策來源的節點造出「非空」的 cascade,實測會被擋(`rc=2`)且帳本
  不落筆(`t_rel_cascade_visited_only_for_empty` 第二段本身就覆蓋了這個案例,我又額外對它做了
  mutation test:把「空集合檢查」拿掉、改成無條件記錄,測試確實翻紅,證實這段防呆不是裝飾)。
- **doctor 既有的 Check E4(`_casc_unseen_ts`)是否真的會因為 `visited` 停止嘮叨**:讀
  `scripts/lumos:1786-1794` 確認 E4 的判準是 `elif not _trs: _casc_unseen_ts.append(...)`——
  `_trs` 來自同一支 `_ledger_read`,`visited` 事件被收進 `trans` 後 `_trs` 不再是空列表,
  E4 確實不會再把這張單算進「零筆判定」清單。與文件宣稱一致。
- **lint 新增檢查對奇怪型別欄位值的行為**:用型別是 list(空/非空)、`None`、純空白字串、
  整個欄位缺失等輸入實測過,`if not str(n.fields.get(_f) or "").strip():` 這段對這些輸入都不會
  丟例外,行為在我能想到的邊界內都合理(空白字串會觸發、空 list 會觸發、None 會觸發、缺鍵會
  觸發)。唯一不直觀的邊界是欄位值恰好是數字 `0`(`0 or "" == ""` 會誤判成「空」),但 `valid_under`
  / `revalidate_when` 設計上就是給文字用的,實務上不會有人填 `0`,這條我不升成發現。
- **`t_rel_cascade_visited_only_for_empty` 整體 mutation kill 測試**:把 `visited` 動詞整個拿掉
  (還原到 patch 前),第一個 `run(..., expect_rc=0)` 就直接因為 argparse 不認得 `visited` 這個
  verb 而丟例外中止整支測試——確認測試對「動詞消失」這個 mutation 是有效的。

以上查證沒有發現「發現一」以外的正確性問題;lint 部分的產品程式碼(`scripts/lumos:4344-4357`
一帶)與 `rel-cascade visited` 的產品程式碼本身讀起來邏輯是自洽的,問題只出在測試的斷言字串
選得不夠精確。
