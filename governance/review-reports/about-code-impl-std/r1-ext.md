# 審稿 findings

## e1 — severity: major

**Spec 逐字引句：**

引句:「①有欄含目標 → pinned 且 `about_hit` 且排首位」
同節規則卻明定：

引句:「四處 `results.append` 都加這個欄位,★不改任何一條路徑的 pinned 邏輯★」
### 問題說明

兩條規則無法同時照字面實作。

現行 `pinned` 是由候選來源決定：

- incident 永遠 `pinned=True`
- direct 只有帶合約才 pinned
- indirect 只有帶合約且 hop 在門檻內才 pinned
- indirect free 明確 `pinned=False`

因此，一個既有的 free 候選即使 `about_code` 命中，依「不改 pinned 邏輯」仍必須是 free；但測試①又要求它「→ pinned」。投稿者可能心裡假設 fixture 本來就是 pinned，但 spec 沒有寫此前提。照測試字面實作，最直接的結果會是把 `about_hit` 當成促升固定席的第四種條件，違反本案核心的「只重排既有固定席」及「free 者不動位置」，並改變 P@8、must-see 與固定席噪音數。

### 查證

- `scripts/lumos:14178`：incident 固定為 `pinned=True`
- `scripts/lumos:14202-14205`：direct 的 pinned 僅取決於 `bool(contract)`
- `scripts/lumos:14211-14217`：indirect 只有合約與 hop 條件成立才 pinned
- `scripts/lumos:14223-14224`：其餘 indirect 明確為 `pinned=False`
- `/tmp/about-code-impl-std-r1.md:397-410`：同節同時要求不改 pinned 與命中後 pinned

**修正所需裁定：**測試①應明寫「建立一個原本就 pinned 的候選」，並另測 free 候選命中 about 後仍為 free；否則不能交付實作。

---

## e2 — severity: major

**Spec 逐字引句：**

引句:「過期即不信——stamp 日期 < git 最後改動日期的節點,其 about_code 視同不存在。」
以及：

引句:「過期 → warn_soft(不擋、不計 issues)。」
### 問題說明

過期守衛只保存並比較 `YYYY-MM-DD`，無法偵測標註完成後、同一天發生的正文修改。這不是單純精度不足，而是會直接做出與「過期即不信」相反的行為：

1. 上午產生 `about_code_stamp: batch-2026-08-23/2026-08-23`
2. 下午修改並 commit 同一篇筆記
3. `git_last_change_dates()` 仍回 `2026-08-23`
4. 比較是嚴格 `<`，所以節點被判為未過期
5. impact 繼續信任已失效的 `about_code`，doctor 也不警告

此 repo 的 spec、存量標註與實作本身都在同一天密集進行；這不是罕見邊界。離線驗證把「預標會過期」視為必須防止的核心故障，但日期粒度不能建立它宣稱的順序關係。

此外，現有 helper 使用 committed Git history；尚未 commit 的工作樹正文修改也完全不可見。因此 PreToolUse impact 在最需要保護「正在編輯」的時刻，仍可能信任已被本地修改弄舊的標註。

### 查證

- `scripts/lumos:13568-13570`：Git 命令使用 `--format=@%cs`，只取得日期
- `scripts/lumos:13575-13580`：只截取 `line[1:11]`，明確丟棄時間資訊
- `scripts/lumos:13568-13580`：只讀 `git log`，沒有檢查工作樹或 index 修改
- `/tmp/about-code-impl-std-r1.md:401-402`：impact 以日期嚴格小於判過期
- `/tmp/about-code-impl-std-r1.md:415-425`：doctor 採同一日期材料
- `/tmp/about-code-impl-std-r1.md:452`：合約候選宣稱「過期即不信」

**修正所需裁定：**stamp 必須能表達可排序的時間或 commit identity，並明定 staged/unstaged 修改如何處理；否則應把合約降格成「只能偵測跨日且已 commit 的過期」。

---

## e3 — severity: major

**Spec 逐字引句：**

引句:「impact 退路徑、印一行。」
但剩四項的測試又要求：

引句:「④過期 → 同②」
而②要求：

引句:「有欄不含 → pinned 判定與 knob=0 時逐 byte 相同」
### 問題說明

過期路徑的輸出合約互相打架。

依「印一行」，過期節點必須產生額外輸出；依「過期 → 同②」及「逐 byte 相同」，它又不得比 knob=0 多任何字元。現行 `cmd_impact` 已會把部分診斷寫到 stderr，因此「逐 byte」若涵蓋完整 CLI 輸出，兩者必然不能同時通過；若只比較 JSON stdout，spec 又沒有如此限定。

這會讓實作者任選其一：

- 為通過 byte-equivalence 測試而沉默，違反讀側的可觀測降級；
- 印過期提示，導致規定的 byte-equivalence 測試失敗；
- 更糟的是把提示混入 stdout，破壞 hook/eval 解析 JSON。

### 查證

- `scripts/lumos:14185-14188`：現有 impact 診斷明確輸出到 stderr
- `scripts/lumos:14009-14011`：其他 impact 診斷同樣使用 stderr
- `/tmp/about-code-impl-std-r1.md:305-308`：要求過期時退回並印一行
- `/tmp/about-code-impl-std-r1.md:406-409`：要求過期輸出與 knob=0 逐 byte 相同

**修正所需裁定：**明定提示只寫 stderr，且 byte-equivalence 僅比較 JSON stdout／結果物件；或撤掉「印一行」要求。

---

## 逐節結論

- 「讀側怎麼用」：有 finding，見 e1、e3。
- 「過期守衛」：有 finding，見 e2、e3。
- 「巨檔失效條件」：已讀，無 finding。
- 「離線驗證結果」：已讀，無新增 finding。
- 「本案新增/修改工具清單」：有 finding，#4/#6 的規格矛盾分別見 e1、e3；✅ 項目未審。
- 「★剩四項的實作規格★ #4」：有 finding，見 e1、e2、e3。
- 「★剩四項的實作規格★ #6」：有 finding，見 e2。
- 「★剩四項的實作規格★ #9」：已讀，無 finding。
- 「★剩四項的實作規格★ #10」：已讀，無 finding。
- 「合約候選」：有 finding；第 3 條無法由目前日期粒度實現，見 e2。

最嚴重 severity：major
