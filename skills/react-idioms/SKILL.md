---
name: react-idioms
description: 寫或審 React(函式元件+Hooks,含 Next.js 的用戶端元件)代碼前必讀——通用不變量層的慣例規則:並行等待、回應亂序與卸載、計時器擁有者、effect 依賴與清理、StrictMode 重掛載、衍生值、清單 key、時間注入、焦點與測試。每條附壞例→好例與機檢對照。狀態管理(Redux/Zustand/Context)、資料抓取庫(SWR/React Query)、路由選型不在此裁——查該專案圖譜。Vue 另有 vue-idioms,Node 後端另有 node-idioms。
---

# React 慣例（通用不變量層）

**這份文件治的病**：AI 寫出「看起來能跑但一換時序就壞」的 React——舊回應晚到蓋掉新資料、離開畫面後結果回來還寫狀態、StrictMode 下多發一次請求、三個地方各自起一條輪詢、用 effect 同步本來算得出來的值。

**分層原則**：只寫不隨框架選擇改變的原則。狀態管理、資料抓取庫、路由——查該專案的知識圖譜與 CLAUDE.md（`lumos search` 起手）。

**機檢欄**：`eslint:規則名`＝現成；`不可機檢`＝只有本文件與審查鏡頭能守（排最前）。

> **核對邊界**:`react-hooks/rules-of-hooks`、`react-hooks/exhaustive-deps` 兩條 2026-10-15 用 eslint 9.39.5 + eslint-plugin-react-hooks 5.2.0 實跑過(在 order-web 對違規樣本各報一條;recommended 設定裡 rules-of-hooks 是 error、exhaustive-deps 只是 warning)。`react/jsx-key`、`react/no-array-index-key`(eslint-plugin-react)本機沒裝,**未實跑**,接入時以該工具當前的規則清單為準。條目取材自一個專案(order-web 的設計審與代碼審),**還沒在第二個 React 專案驗過**。
> REVISIT:2027-01-15 第二個 React 專案跑完第一輪代碼審後,回填哪條沒用上、漏了哪些坑,並補 eslint-plugin-react 兩條的實跑紀錄。

---

## 一、並行、亂序與生命週期

> **審查時機管道**:本文標「⚠ 不可機檢」的條目,其載重問已由 lumos 效能檢核機制在三時機自動推送(動手前 impact hook 注入/push 前 pitfalls advisory/終審 code-loop 鏡頭;題目 react-parallel、react-race、react-effect、react-strict 等,內容源=lumos-toolchain 圖譜 Systems/效能檢核目錄)——可機檢條目歸 linter,勿靠人記。

### R1. 互不依賴的等待必須並行 ⚠ 不可機檢，頭號條款
```tsx
// ✗ 延遲相加
const user = await fetchUser(id)
const prices = await fetchPrices()

// ✓ 並行
const [user, prices] = await Promise.all([fetchUser(id), fetchPrices()])
```
迴圈裡逐筆 `await` 同理:能一次發出就一次發出,量大時用有界並行。

### R2. 回應亂序要有序號或中止;被取代的中止不算失敗 ⚠ 不可機檢，最常見的 bug
輪詢或快速切換時,舊請求晚回來會把較新的資料蓋掉。每次發請求帶序號(或 AbortController),回來時只收最新那次的結果。
```tsx
// ✗ 誰晚到誰贏
useEffect(() => { fetchStock(id).then(setStock) }, [id])

// ✓ 中止上一次;被中止的那次不進錯誤狀態
useEffect(() => {
  const c = new AbortController()
  fetchStock(id, { signal: c.signal })
    .then(setStock)
    .catch(e => { if (e.name !== 'AbortError') setError(e) })
  return () => c.abort()
}, [id])
```
「中止舊請求」被算成抓取失敗、跳出錯誤提示,是同一族的另一面。

### R3. 卸載後在途結果不得寫狀態或觸發後續動作 ⚠ 不可機檢
離開畫面後,下單、付款這類請求的結果才回來,不能再 setState、也不能再觸發重查或起新計時器。用 effect 清理時設的旗標或 AbortController 擋住;寫在 `await` 之後的每一步都要先問「元件還在嗎」。

### R4. 計時器與輪詢鏈只能有一個擁有者 ⚠ 不可機檢
前景事件、操作完成、定時器各自 `setTimeout` 起下一輪,就會變成多條輪詢鏈同時跑。把排程收進一個物件(或一個 effect),其他地方只能「請求重查」,由擁有者合併、決定下一輪時間;清理時一次停掉。

### R5. effect 依賴陣列照實寫，清理函式收掉每個副作用（機檢為主）
`eslint:react-hooks/exhaustive-deps` 不准關、不准用 `// eslint-disable-next-line` 繞;recommended 預設只是 warning,建議在專案設定升成 error。effect 裡起的計時器、訂閱、監聽都要在回傳的清理函式裡收掉。Hook 只能在元件頂層呼叫:`eslint:react-hooks/rules-of-hooks`。

### R6. StrictMode 重掛載要安全 ⚠ 不可機檢
開發模式下 effect 會「掛載→清理→再掛載」一次,`useState` 初始化函式與 state 更新函式會被呼叫兩次。所以:
- setup 跑兩次不能重複送出、重複訂閱(清理要真的收乾淨)。
- 更新函式與初始化函式要是純的,不在裡面發請求或產生 id。
- 用世代號(或 ref)擋「第一次掛載的請求晚到」:晚到的舊結果不得清掉新一代的「在飛」旗標——否則會多發一個併行請求。
```tsx
// ✓ 每次 setup 換一代,舊代的回應一律丟掉
useEffect(() => {
  const gen = ++genRef.current
  load().then(r => { if (gen === genRef.current) setData(r) })
  return () => { genRef.current++ }
}, [])
```

## 二、狀態與渲染

### R7. 衍生值直接算，不用 effect 同步 ⚠ 不可機檢
```tsx
// ✗ 第二份 state,會漂、多一次重繪
const [count, setCount] = useState(0)
useEffect(() => { setCount(items.length) }, [items])

// ✓ 直接算;真的貴才 useMemo
const count = items.length
```

### R8. 清單 key 用業務 id（機檢）
key 不能是陣列索引或 `Math.random()`;會插入、刪除、重排的清單用索引當 key,輸入框狀態會跟錯列。`eslint:react/jsx-key`、`eslint:react/no-array-index-key`(未實跑)。

### R9. 重繪範圍有意識 ⚠ 不可機檢
高頻更新的狀態(輪詢、計時、輸入)放在用到它的最小那棵子樹;Context 的 value 不要每次 render 重建新物件;`useMemo`/`memo` 只在量級值得時才加,不是預設。

### R10. 現在時間與亂數從參數或注入時鐘進來 ⚠ 不可機檢
純函式裡不直接呼叫 `Date.now()`/`Math.random()`;元件從注入的時鐘取時間。分頁回到前景時(`visibilitychange`)要立刻重讀時間——只靠計時器下一拍,過期的東西會繼續顯示成可操作。

## 三、無障礙與測試

### R11. 重繪不能讓鍵盤焦點跑掉 ⚠ 不可機檢
按鈕改成停用、清單被輪詢整段換掉時,原本有焦點的元素消失,焦點會跳回頁首。停用用 `aria-disabled` 或保留元素、清單用穩定 key 原地更新;狀態訊息放在一開始就存在的 `aria-live` 區塊裡。

### R12. 測試照使用者看得到的行為查 ⚠ 不可機檢
用 Testing Library 依角色與文字找元素(`getByRole`、`getByText`),網路用替身;不斷言元件內部 state、不 mock 自己的純函式。

### R13. 不把使用者內容當 HTML 插進頁面（資安）
`dangerouslySetInnerHTML` 只收經過消毒、來源可信的字串;跳轉網址要驗。

---

## 機檢接線（一次設好）

```js
// eslint.config.js 要點(flat config)
// 1. eslint-plugin-react-hooks:recommended 之上把 react-hooks/exhaustive-deps 升成 'error'
// 2. eslint-plugin-react:開 react/jsx-key、react/no-array-index-key(未實跑)
// 3. typescript-eslint:type-aware 必開 no-floating-promises、no-misused-promises
```
專案把 ESLint 指令(`@microsoft/eslint-formatter-sarif`)宣告進 `.lumos/lint.json`,`lumos pitfalls --diff` 自動吃 SARIF 進審查 manifest;`lumos doctor` 的 [F] 段看到 eslint 設定會印可貼的範本。

## 審查鏡頭（code-loop 用）

「對照 react-idioms R1–R13 逐條掃 diff;finding 必須引用條號(如『違反 R2:輪詢回應沒有序號,舊回應會蓋掉新庫存』),引用不出條號的風格意見不要標。」

## 誠實邊界

1. 最重要的幾條(R1 並行、R2 亂序、R3 卸載、R4 計時器擁有者、R6 StrictMode)全部不可機檢——本文件＋審查鏡頭是唯一防線。
2. 本文件不裁框架;與專案當地慣例衝突時當地贏,衝突記進該專案圖譜。
3. 回填:被人工糾正的寫法先記進該專案圖譜;確認它在多數專案都會再犯,才走 [[Projects/idioms自維護迴路_計劃]] 的候選流程加進本文件。
