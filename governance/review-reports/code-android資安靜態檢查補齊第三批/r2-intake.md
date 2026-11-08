# r2 收貨紀錄(code-android資安靜態檢查補齊第三批)

## 修補鏡頭準備(§3.1)

- 兩端:修前 84a2a61777096eeb917b41ef4f7ff1c97f398b9f(r1 派工單 base_commit;用同一範圍重產 r1 材料指紋一致)→ 修後 b3561e61aecffb923faa3b3716a778bb7c0c922b;祖先關係 rc0。差異 `r2-repair.patch`,來源 `r2-repair-binding.json`,fix-check 結果 `r1-fix-check.txt`(通過)。
- 新完整快照 `r2-snapshot.patch`(1abb0f2bd..b3561e61,不含卷證與帳本,765 行)。

### 先列出處清單(r1 各組)

- s1 註解被當成程式:同一種「對整段原文比對」的條件在這條規則有三處——`regex: '^keyboardOptions…'`、`not: regex: 'KeyboardType…Password'`、`regex: 'keyboardType\s*=…'`;三處都受註解與字串影響,形狀凍結不改,〈天花板〉一句涵蓋三處。Jackson 那條的被呼叫端 regex 對 navigation_expression 原文比對,註解在點號前後的寫法同族,同樣列進天花板範圍(未另補例)。
- s2 測試抓不到錯:規則裡每個分支逐一對案例——呼叫名四個(C95、C96、C107、C108)、①沒有 keyboardOptions(C95)、②字面 Default(C102)、②字面括號(C101)、②keyboardType 字面值後接右括號(C103)、後接逗號(C117)、放行 Password(C97)、NumberPassword(C104)、keyboardType 是變數(C105)、`.copy`(C106)、變數(C98)、桌面四項排除(C100、C110~C112);Jackson 四個名字(C113、C114、C118、C119 與樣本裡的 enableDefaultTyping)。
- a1~a3 寫法:同表的字串引號、放置表形狀、測試說明三處各一,沒有別處同族。

### 修補驗證(修前紅、修後綠)

- s2:修後把逗號那支拿掉 → C117 紅;拿掉兩個 AsProperty 名字 → C118、C119 紅;還原後 191 passed。
- s1:修後 C120(註解裡寫 KeyboardType.Password)不報,釘住天花板。
- 保留行為:C95~C116 的原有逐例、S4 放置與排除檢查在修後全綠(t_kotlin_rulepack_security_rules 191 passed)。

## 收貨

- 兩席(審查二、架構對齊二)全部交回後一次從逐字稿存檔;兩份已是正規化格式,審查二引句全數錨定,架構對齊二 0 條(沒有引句)。收貨時 git status 只有卷證目錄的新檔,兩席沒動 repo。
- 臨時目錄 /tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/ 收貨後刪。

## 編號與處置

編號:審查二 t1–t2(照報告順序)。全部 minor。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| t1 | 呼叫名的兩個 ^ 錨點沒有案例釘住,拿掉後自訂元件名、完整套件名從不報變成報,測試照綠 | HIT:補 C121、C122 後拿掉錨點,兩例翻紅(192 passed 2 failed),還原 194 passed | 折:補 C121、C122;測試說明補翻紅釘 |
| t2 | 天花板只寫「括號裡有函式呼叫」,實際是括號裡再有任何括號就不報(例 if (x)) | HIT:C123(if (x) … else …)現行規則不報 | 折:〈天花板〉那句改寫,補 C123 釘住 |

--refuted-set none。--regression-set none:兩條歸因都是原有漏查(規則檔與型錄在 84a2a617→b3561e61 之間沒有改動,審查二附了 git diff --stat 為空;編排者以 `git diff --stat 84a2a617 b3561e61 -- configs/ skills/` 核對為空)。

### 先列出處清單

- t1 錨點:規則裡以 ^ 起頭的比對有四處(呼叫名兩個、`^visualTransformation`、`^keyboardOptions`);後兩處審查二試過拿掉照綠但講不出失敗場景(要有 fooKeyboardOptions 這種參數名),不補例。
- t2 天花板說法:同一句說法只在計劃〈天花板〉一處;型錄 UI-112「情境怎麼認」寫「變數傳進來的鍵盤選項不判」,沒寫括號細節,不衝突。

## 先查世界

- PRIOR-ART:t1、t2——測試抓不到錯與天花板措辭,照 lumos-project-notes〈實作測試品質〉補釘住現行行為的案例;沒有要另查的。
