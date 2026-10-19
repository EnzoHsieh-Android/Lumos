# 前端分層目標架構範本

前端專案(React、Vue 都適用)想讓新程式照「API 層、domain、元件」分層寫,又沒有舊鄰居可比(新專案)或不想被架構對齊審查席判成「跟舊鄰居不一樣」時,用這份範本開一篇目標架構節點,再在 `.lumos/config.json` 的 `arch_targets` 宣告哪些目錄照它審。機制本身見 [06-代碼審與推送.md](06-代碼審與推送.md) 的 `arch_targets` 那一列;形狀跟 [target-arch-ddd-template.md](target-arch-ddd-template.md) 一樣。單源 Projects/前端框架從vue分出_計劃。

## 採用步驟

1. 開節點:`lumos new system 前端分層目標架構 --responsibility "前端新程式該遵守的分層寫法;不管任何程式檔,規則套用的目錄由 .lumos/config.json 的 arch_targets 宣告"`(不帶 `--code`:它規範的是範圍內的寫法,不是自己的程式檔)。
2. 把下面範本區塊的 `summary` 五條 RULE 行貼進那篇的摘要,正文照需要貼。**目錄名照專案實際改**(範本寫的是常見預設 `src/api/`、`src/domain/`);用不到的規則整行刪掉。
3. **把 `<採用日>` 換成今天、`<回頭日>` 換成打算回頭檢查的日期(建議一年後)**——沒換就照抄,`lumos lint` 會逐條印「日期要寫成 YYYY-MM-DD」警告(筆記格子目前只提醒不擋,所以要自己換掉)。
4. 在 `.lumos/config.json` 加宣告(路徑照專案實際目錄改;第一條命中算數):

```json
{
  "arch_targets": [
    {"path": "src/**", "node": "Systems/前端分層目標架構"}
  ]
}
```

宣告與規則只讀「分支從主線分出來那一刻」的版本:加宣告的那次推送照舊比鄰居,合進主線之後才生效。

## 為什麼是這五條

- **前三條劃出三層**:只有 API 層碰網路、API 層把 HTTP 的細節翻成型別化的結果、domain 只放純函式。這樣畫面不會散落 `res.status === 409` 這種判斷,業務規則(倒數、能不能付款)可以不開瀏覽器就測。現在時間與亂數從參數進來,是為了讓「到期了沒」這類判斷測得準。
- **第四條壓住全域狀態的擴散**:一頁用得到的狀態先放最近的共同父元件,要跨三層以上才引入 Context 或狀態庫。審查席判得出「為了一頁的清單加了 store」;判不出的「狀態設計好不好」不寫。
- **第五條讓測試跟著行為走**:從使用者看得到的東西(角色、文字)查,網路用替身,不讀元件內部 state、不 mock 自己的 domain 函式——重構元件內部時測試不必改。lumos 的〈實作測試品質〉(見 [03-寫回圖譜.md](03-寫回圖譜.md))要求斷言實際行為,但刻意不規定架構;選了這份範本的專案用這條把「從哪個邊界測」講死。

框架特有的寫法(effect 依賴、StrictMode、key、computed vs watch)不在這裡,歸各棧的慣例 skill(react-idioms、vue-idioms)。

## 範本

```markdown
---
type: system
status: doing
responsibility: 前端新程式該遵守的分層寫法;不管任何程式檔,規則套用的目錄由 .lumos/config.json 的 arch_targets 宣告
aliases:
  - 前端分層規則
  - 前端架構規則
tags:
  - type/system
  - status/doing
summary: |-
  RULE:只有 src/api/ 能呼叫網路(fetch、axios)與讀寫 HTTP 標頭;元件與 src/domain/ 不直接打網路。違反長怎樣:元件的 effect 裡直接 fetch('/api/products') [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:src/api/ 對外回型別化的結果(成功、業務錯誤、程式錯誤、結果不確定、呼叫端自己中止),不把 HTTP 例外或原始 Response 丟給畫面。違反長怎樣:元件裡 catch 之後讀 res.status === 409 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:src/domain/ 只放純函式與型別,不 import 框架、網路與瀏覽器全域;現在時間與亂數由參數傳入。違反長怎樣:倒數函式裡直接呼叫 Date.now() [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:畫面狀態放在用到它的最近共同父元件,用 props 往下傳;要跨三層以上傳遞才引入 Context 或全域狀態庫。違反長怎樣:為了一頁的訂單清單加一個全域 store [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:測試從使用者看得到的行為驗(依角色與文字查),網路用替身;不斷言元件內部狀態、不 mock 自己的 src/domain/ 函式。違反長怎樣:測試裡讀元件內部 state,或把 src/domain/ 的倒數函式整個 mock 掉 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
---
# 前端分層目標架構

> 白話:這篇是前端新程式該長什麼樣的規則清單。專案在 .lumos/config.json 的 arch_targets 宣告哪些目錄照這篇審,架構對齊審查席就改拿上面的 RULE 行當標準,不再要求新程式跟舊鄰居長得一樣;範圍外的舊碼照舊比鄰居。
```

## 調整與撤除

- 用不到某條(例如專案本來就用狀態庫)就刪掉那一行,或加 `[status:superseded]` 並寫 `[被取代:…]`;架構對齊席只看沒作廢的 RULE 行。
- 規則有對應的架構檢查(例:eslint 的 `no-restricted-imports` 擋元件匯入 fetch 包裝、dependency-cruiser 的分層規則)時,在那一行加 `[test:<測試名>]`,讓機器守、審查席補看。
- 到回頭日(`until`)要人裁一次還留不留;過期的規則照樣附給審查席,但會加註「已過 until,待人裁」。
