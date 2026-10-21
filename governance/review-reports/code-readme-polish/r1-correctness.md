severity: minor

已審材料：`governance/review-reports/code-readme-polish/r1-snapshot.patch`（1700 行）  
SHA256：`349553ceae205bbab8be10137b6e27be08dd25652f44385d2b7d85b5342de80f`

severity: minor  
blocking: no  
引句:「由未參與前一輪的 AI 審查員重新檢查：檢查修補有沒有副作用。」  
README 將新審查員定義為「未參與前一輪」，弱於實際規則要求的全新無脈絡席。例如第一輪 A、第二輪 B、第三輪再用 A 符合 README，卻違反審查規則，會削弱跨輪獨立性。  
file: `README.md:114`  
file: `skills/lumos-code-loop/SKILL.md:50`  
file: `skills/lumos-design-loop/reference.md:347`

severity: minor  
blocking: no  
引句:「("verification-checkout",460,463,"Checkout E2E" if en else "結帳流程測試","green",16,False),」  
英文圖與雙語正文都明確表示端對端測試，中文圖卻改成泛稱「流程測試」，不再傳達 E2E 的測試邊界，雙語語意不一致。  
file: `assets/readme-diagrams/generate.py:254`  
file: `README.md:87`  
file: `README.en.md:87`

severity: minor  
blocking: no  
引句:「Five Swiss-cheese defence layers: risk tiering, multi-seat review, disposition gates, external rules, and tests proven to fail when behaviour is removed.」  
四個本輪變更的中文 SVG，其 `<desc>` 仍由產生器輸出英文。SVG 使用 `role="img"` 及 `aria-labelledby="title desc"`，直接開啟圖檔或由輔助技術讀取時，中文標題後會接英文說明，沒有完成中文無障礙內容。  
file: `assets/readme-diagrams/generate.py:451`  
file: `assets/swiss-cheese-zh.svg:3`  
file: `assets/map-zh.svg:3`  
file: `assets/graph-demo-zh.svg:3`  
file: `assets/risk-review-zh.svg:3`

其餘覆蓋：

- 已逐 hunk 審閱 README 中英文、SVG、產生器與圖譜筆記；安全檢查的 pre-push、CI、風險分席等敘述與 CLI／skill 行為相符，無 finding。
- 固定圖譜席已讀 `Systems/README圖產生器`；產生器與衍生 SVG 的責任邊界相符。除上述雙語問題外，無合約偏差。
- `python3 assets/readme-diagrams/generate.py --check` 通過：22 個雙語 SVG 的 XML、可重現性、靜態 fallback 與揭露順序均通過。
- 抽查四張圖的瀏覽器渲染，未見裁切或重疊；snapshot 與指定 base..HEAD diff 完全一致，`git diff --check` 通過。
- 新舊資料互讀、寫一半、時間邊界與不可逆外部動作不適用；SVG 是可重建衍生資料。未執行全套測試；指定的分層測試建議檔為空。

總結：最嚴重 severity: minor；blocking: 0。
