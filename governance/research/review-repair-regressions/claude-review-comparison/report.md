# Claude 代碼審片段對收斂性的幫助

查證日：2026-10-07。這是原始片段與 Lumos 現有做法的對照，沒有執行外部程式、重發鏡像原始碼、改審查規則或開 PR，也沒有測量真實輪數改善。

## 先辨識來源

- 2025 鏡像固定版本 da716d77 的 src/commands/review.ts 是讀 PR 與 diff、給綜合建議的提示詞：[原始片段](https://github.com/iamdin/Claude-Code-Leak/blob/da716d77b251868918bb5776377f85a18a47ffdf/src/commands/review.ts)。不能外推成完整修復迴圈。
- 另一公開鏡像固定 df18093e 的 package.json 自報 2.1.88。直接讀了 review.ts、security-review.ts、review/reviewRemote.ts、review/ultrareviewCommand.tsx 及 package.json；可查內容與指紋，未獨立認證與官方發布物等同。遞迴樹被服務截斷，不能宣稱全 repo 沒有某功能。
- instructkr/claw-code 現在導向 ultraworkers/claw-code；README 說明當前主要實作是 Rust，並非 Anthropic 維護：[專案說明](https://github.com/ultraworkers/claw-code/blob/08106b0c3771ef5b4a5aa176acccd460e88b7325/README.md)。另兩個舊鏡像名稱已改指其他專案，未拿它們充當原實作。
- 官方公開外掛另固定 8e60c4ca；與託管 Code Review 服務的文件分開看，不能把一份外掛提示詞當成遠端引擎全部實作。每份查證來源、網址、SHA-256與版本見 source-receipts.json。

## 值得借用與不能照抄的地方

| 觀察到的做法 | 對收斂性的幫助與限制 | Lumos 的取捨 |
|---|---|---|
| 官方 code-review 外掛先多席找問題，再逐項派新席查證、過濾及去重 | 可減少無根據的修補往返；文字查證不等於測試已執行 | 既有乾淨席、辯方、收貨與案例證據已部分承接；維持實際重現、未判定與原級別，不加一套分數閘 |
| 官方文件提出修訂輪抑制新增小建議及精簡 REVIEW.md | 可避免修補途中一直換整理標準 | 候選：先界定純風格／自選重構與真行為問題，前者延後，不因 minor 標籤就吞掉邊界或合約問題；先看歷史案例再改規則 |
| 官方 pr-test-analyzer 專看行為、負面情境與能否抓到退化 | 能揭露「有測試但抓不到這次錯誤」 | 本分支的修復／保留配對與相關壞法抽查方向一致；不以覆蓋率或作者綠燈代替正確行為斷言 |
| 官方 review-pr 流程在通過後安排簡化 | 若簡化真的改碼，先前審查結果不再代表交付版本——這是本專案的風險推論 | 保留我們的修補／重構分段、最後固定版本與通過後只交帳本；不直接搬進未複驗的最後整理步驟 |
| 鏡像 reviewRemote 的註解指出短逾時會反覆重派驗證者，程式另界定工作與總時間預算 | 能提示調查「卡住」究竟是修復失敗還是查證一直中斷；註解不是已驗證生產事故 | 次要候選：依既有執行紀錄查逾時／重派成本；逾時保留未完成，不當 clean，也不自動加一輪 |

第一手依據：[官方找問題與查證外掛](https://github.com/anthropics/claude-code/blob/8e60c4cac989c0e0cc6d2c49407a5c67f5a4a8e6/plugins/code-review/commands/code-review.md)、[官方修訂輪及短指令建議](https://code.claude.com/docs/en/code-review#what-you-can-tune)、[測試品質審查員](https://github.com/anthropics/claude-code/blob/8e60c4cac989c0e0cc6d2c49407a5c67f5a4a8e6/plugins/pr-review-toolkit/agents/pr-test-analyzer.md)、[多面向流程](https://github.com/anthropics/claude-code/blob/8e60c4cac989c0e0cc6d2c49407a5c67f5a4a8e6/plugins/pr-review-toolkit/commands/review-pr.md)、[公開鏡像的遠端入口](https://git.jon-e.net/jonny/claude-code/src/commit/df18093e4794389a985649eddf17464fb2224c5a/src/commands/review/reviewRemote.ts)。

## 特別要避免的假收斂

官方公開 code-review 外掛的某段排除依賴特定輸入／狀態的疑慮，並有只讀差異的鏡頭；照字面全面套用，可能漏掉索引撤回、例外類別等必須看狀態與呼叫者的問題。這是提示詞與本案歷史症狀對照的風險推論，沒有跑模型證明它實際漏報；託管服務文件反而描述完整程式脈絡，不能混稱同一限制。

鏡像 security-review.ts 以信心分數篩選，且排除若干安全類別：[固定片段](https://git.jon-e.net/jonny/claude-code/src/commit/df18093e4794389a985649eddf17464fb2224c5a/src/commands/security-review.ts)。只借用逐項查證的結構，不把模型自評八分當校準過的正確率，也不把專門安全審的排除清單套成一般代碼審的規則。

## 建議下一個最小研究

先做三類已有案例的對照：純風格建議、只在特定狀態出錯的真缺陷、修補造成的退化。比較「維持既有完整審查」與「只把非必要建議延後、查證與行為守衛不減」的處置及耗時。必須保留每項證據、未知與漏報，不能用少報問題或少改程式當成已改善。

優先順序：先研究避免非必要修補擴張，再核對查證是否回答實際失效機制，最後才研究派工文字與時間預算。是否值得實作，依可重現歷史案例及實輪試用决定。當前只是候選，不宣告 Lumos 有新的缺口，也不直接改輪數、severity或放行閘。

補充案例核對見policy-risk-cases.json：兩個既有狀態依賴finding與實測新增告警義務，加上一個清楚標示的合成風格建議。這是規則風險的人工比較，不是模型A/B，沒有新跑兩版產品，不把例子數或字面解讀當誤報／漏報率。實測複雜度讓既有閘擋下的lint-F1不屬自選風格，不能藉延後建議把它藏掉。
