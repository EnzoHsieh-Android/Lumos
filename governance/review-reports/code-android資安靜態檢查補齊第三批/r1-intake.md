# r1 收貨紀錄(code-android資安靜態檢查補齊第三批)

## 收貨

- 兩席(審查、架構對齊)全部交回後一次從逐字稿存檔。審查席最後一行總結寫成「max severity: minor」,report-normalize 判成格式不合的等級宣告,退回該席改寫總結句後重交(只差那一行)。架構對齊席三處 severity 行前有縮排,report-normalize --write 只搬到行首(純格式)。
- quote-check 兩份都全數錨定;refcheck missing 0。收貨時 git status 只有本卷證目錄,兩席沒動 repo。
- 分級:pitfalls 判 light(改動沒有產品程式檔),照第二批做法拉高到 standard(新增一條推送前會擋的規則)。材料不含卷證與帳本(governance/、docs/.canary-log.jsonl、docs/.governance-log.jsonl),742 行,沒拆包。
- 派審前編排者自己逐條改壞密碼欄規則五處(拿掉字面 KeyboardOptions 那支、名單拿掉 BasicTextField2、放行不認 NumberPassword、拿掉 desktopMain 排除、等級改 warning),測試各自翻紅。
- 臨時目錄 /tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/ 收貨後刪。

## 編號與處置

編號:審查 s1–s2;架構對齊 a1–a3(照報告順序)。全部 minor。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| s1 | 字面 KeyboardOptions 裡的註解寫到 KeyboardType.Password 就不報 | HIT:ast-grep 0.51.1 實跑,註解那例 0 命中 | 折:形狀已凍結不改規則;〈天花板〉補這種漏報,逐例 C120 釘住不報 |
| s2 | 逗號分支、Jackson 兩個 AsProperty 名字沒有逐例,拿掉照綠 | HIT:實跑三種寫法現在都會報;改壞後補例前無案例 | 折:補 C117~C119;改壞逗號那支 C117 紅、拿掉 AsProperty C118、C119 紅 |
| a1 | 新案例用單引號,舊表全是雙引號 | HIT:diff 新列 | 折:改成雙引號 |
| a2 | 測試說明沒補第三批的改壞清單 | HIT:docstring 只到第二批 | 折:補第三批翻紅釘 |
| a3 | 放置表第四格用字串旗標切換排除清單 | HIT:diff 的 "desktop" | 折:第四格直接放排除清單 tuple,沒寫的照八項 |

--refuted-set none(沒有重現不到的)。

## 先查世界

- PRIOR-ART:s1(註解被當成程式)——ast-grep 的 regex 比對節點原文(https://ast-grep.github.io/reference/rule.html 的 regex 是對節點文字比對),註解是節點文字的一部分;要排除註解得改成逐個子節點判,屬於改形狀,形狀凍結後不改,照第三批計劃寫進〈天花板〉。
- PRIOR-ART:s2、a1~a3(測試抓不到錯、寫法跟鄰居不一致)——照 lumos-project-notes〈實作測試品質〉與鄰居寫法,沒有要另查的。
