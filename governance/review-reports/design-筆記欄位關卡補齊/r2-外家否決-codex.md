severity: major

## F1 about_code 新規則抓不到本案列出的錯誤

severity: major
blocking: yes
引句:「`about_code`:每一項要在版本控制的索引裡」
現有錯誤值是一篇已受版本控制的 Markdown 筆記；`git ls-files --error-unmatch` 對該路徑成功，因此新規則會放行。手動修掉這一篇不能防止同型錯誤再次進入圖譜，S9 也只測未追蹤檔。
file: `docs/lumos-toolchain-knowledge/Issues/把自己的推論寫成repo明文寫過.md:12`
file: `scripts/lumos:21636`
file: `scripts/lumos:21659`
file: `scripts/lumos:21601`

## F2 lands_in 存在性要求會擋合法的新節點落點

severity: major
blocking: yes
引句:「而且每一項都要是 `Systems/<名稱>` 的純字串、指到存在的節點」
現行處置閘刻意允許不存在的 `Systems/<名稱>`，並把它標成「新開」後放行，讓設計先審、實作時再建立節點。新 lint 若要求目標已存在，本 repo 設成 `note_lint.gate:on` 後，任何以新 Systems 節點為落點的計劃都會在提交、推送與 CI 前被擋；稿中「跟設計審落點那一步同一套判法」與現況相反。
file: `scripts/lumos:17920`
file: `scripts/lumos:17923`
file: `scripts/lumos:17966`
file: `scripts/lumos:17967`
file: `scripts/test_lumos.py:42409`
file: `scripts/test_lumos.py:42410`

## F3 responsibility 的空白計數與既有建檔入口不一致

severity: major
blocking: yes
引句:「去掉空白後不到 10 個字就擋、檔案不動」
既有 `lumos new --responsibility` 使用 `_nodehome_resp_ok`，只以 `strip()` 去除首尾空白，內部空格與 tab 仍算字數；例如 `甲  乙  丙  丁` 只有四個非空白字但長度為十，實際會通過。若 `set` 沿用既有 helper，S11 直接失效；若另寫真正去除全部空白的判定，同一欄位又會因寫入入口不同而有兩套門檻。修訂稿沒有統一 predicate，也沒有內部空白／tab 測例。
file: `scripts/lumos:15052`
file: `scripts/lumos:15053`
file: `scripts/lumos:21492`
file: `scripts/lumos:21496`
file: `scripts/lumos:21497`

## 已讀、無 finding

實務隱患逐類：金流無，沒有交易或計費路徑；對外送出無，新增檢查只讀筆記與本機 git；不可逆無，設定與筆記皆可由版本控制回退；守衛面有，F1 是假陰性、F2 是假陽性、F3 是平行寫入入口判準分裂。

圖譜鏡頭逐條：計劃節點本身沒有登記合約；`Systems/lumos-cli-read` 的 search 排除 superseded 合約不受本案影響；`Systems/lumos-cli-write` 沒有登記合約，既有原子寫入路徑未被設計要求削弱。

最嚴重 severity: major；blocking: 3 條。
