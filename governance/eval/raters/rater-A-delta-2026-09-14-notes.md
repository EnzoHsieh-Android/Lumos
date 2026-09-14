# Rater A — delta 標註筆記(2026-09-14)

## 標註方式

222 筆候選拆成 8 批,每批各自獨立打開節點讀過內容再判 0/1/2(不看檔名猜)。過程中有幾批的判斷需要交叉核對——凡是不同讀法之間有實質分歧、且分數落差夠大(尤其牽涉到「2」)的項目,都回頭直接重讀原始節點與程式碼(`scripts/lumos`)裁定最終值,不是憑印象定案。以下 ① 是判 2(必看)的理由,② 是難判、認為可能跟另一位獨立評審不一致的項目。

## ① 判 2 的理由(逐筆一句)

- E17 / Systems/授權與歸屬.md:逐字寫明 marked.min.js 這支第三方檔的授權標示狀態、已知缺口與回頭條件,是編輯這支 vendored 檔前必須知道的合約。
- S05 / Issues/code-loop-pass不能指定分支.md:「留痕」機制在 detached worktree 下失效的實際案例與繞法。
- E16 / Systems/授權與歸屬.md:逐字點名 3d-force-graph.min.js 1.80.0,上游 minified build 沒帶版權聲明、standalone 匯出會整段內嵌成再散布,帶 REVISIT:2026-12-06 升版重跑授權核對。
- S19 / Projects/全repo審視_計劃.md:全圖唯一提到 kill_recipes 的地方,且帶關鍵資訊——抽樣輪替協議已 08-14 停用、裁定不排進每日治理。
- S29 / Issues/code-loop-pass不能指定分支.md:狀態 open,代碼審機制在 detached worktree 下失效的真事故,附繞法與 REVISIT。
- S29 / Projects/自足性審計閉環_計劃.md:整篇是審計(自動審→修→複審)閉環機制的設計與裁定過程,是「審」字在圖譜裡少數以審計機制為主體的節點。
- 標籤系統盤點_調研(S21):實測證據——search evals 前十筆有七筆唯一命中行是 scope/evals 標籤,證明 scope 標籤靠欄位權重 1.5 意外進了 BM25F 排序,跟另篇宣稱「不進排序」矛盾。
- 標籤系統精簡_計劃(S21):可重現實驗,候選集從兩篇減為一篇,節點分數從 0.8838 掉到 0.4561,證明 BM25F 統計量取自候選集而非全庫。
- 檢索核心重建_計劃(S21):排隊中的檢索重建案,正面處理不換掉既有 BM25F、BM25F 統計量取自候選集等設計決定。
- 修法A_lumos先行ablation_計劃(E21):對 scenario_probe.py 做過大量實質修改並走完整代碼審,留下具體判準設計與測試合約。
- git-hooks路徑指向樹內_checkout即執行分支碼(S18):直接指出 anchor-integrity 機制防線缺口——只擋改錨點檔後 push,擋不住 checkout 觸發樹內 hook 任意執行。
- code-loop-pass不能指定分支(S20):整篇講 detached worktree 下 code-loop pass 把留痕記成 HEAD、推送到 main 查不到的真實踩雷經過與繞法。
- 共用工作目錄的未追蹤檔讓全套測試假紅(S20):git worktree add --detach 是這篇解法核心手段,教你怎麼用 worktree 隔離判斷測試紅是不是真的。
- 健檢技術棧那段撞到多平台設定就整支中斷(S17):記錄 pitfalls --diff 掃描把工具鏈自己安裝的檔當成消費專案程式碼,風險分級被撐成 high、推送被擋的真實 bug。
- E22 → 合約測試閘什麼時候跑_計劃.md:DEP 明寫綁 .github/workflows/ci.yml,整篇就是在裁「CI 用 LUMOS_SKIP_BOUND_TESTS 跳過、本機 pre-push 真跑」這條規則本身,不看會直接誤改這條剛裁定的政策。
- S30 → 簿記白名單漏canary與bypass帳.md:標題本身就是「帳」——記著一個「記審查帳這個動作把留痕自己打失效」的死結事故與根治法,是這批候選裡唯一真正以帳本機制為主題的節點。
- S02 → 2026-08-25_設計審收斂重定義落地.md:查詢字面「收斂」對應到的就是這篇——設計審「收斂」定義怎麼重寫、驗證過什麼,標題完全對應。
- E18 → 2026-08-27_自主loop遷處置閘.md:直接是 autonomous-loop.sh 這次改動(TIER/CROSS_VERDICT 那段)的驗證記錄,驗的就是 runner 的 tier 守衛從 --gate 遷到 --disposal,改這段前不看會不知道剛遷過閘、可能改回舊協議。
- E09 / Codex完全支援_計劃.md:diff 那一行 HOOKS_DIR 上方註解直接對應這份計劃的設計決策(不碰 config.toml、Claude/Codex 雙目標走 --target),權威合約文件。
- S10 / GraphRAG對節點關聯_調研.md:PageRank 排序已 2026-07-28 被消融實驗殺掉,不看會重做已否決的輪子。
- S10 / 檢索核心重建_計劃.md:排隊中的核心專案,標題即含「排序」,S5/S9/S11 直接決定排序要不要動。
- S10 / 多路召回與宣告式欄位_調研.md:專門研究多路候選怎麼合併成排序(RRF vs 線性加權)的第一手調研。
- SY03 / 節點還原SOP_計劃.md:PRIOR-ART 一整節專門拆解 openwiki(定義、SOP 怎麼反著用、承認唯一塌陷回失效模式的例外),對這個概念最完整的應用說明。
- E10 / Systems/每支檔有家.md:about_code 明列 scripts/hooks/pre-push,內容就是在講推送前逐提交看寫回那段檢查機制。
- E10 / Systems/bound-tests-gate.md:about_code 同列 scripts/hooks/pre-push,詳細記著高風險擋/低風險只提醒兩條路徑怎麼呼叫 code-loop check。
- S27 / Systems/convergence-evidence-gate.md:節點名字本身就是「證據閘」,design-loop 收斂判準最完整最權威的說明。
- E19 / Systems/risk-tiered-review.md:about_code 直接列 confidence_report.py,KEY 行逐字對上被改動的函式簽章。
- E11 / 消費專案接入靜默失效_計劃.md:正文④直接寫「標記檔per-machine不版控、治理帳CI唯一權威」設計,並記錄 init 產生的新專案把規則寫反的真實事故。
- E11 / pitfalls-code-loop.md:decisions d3 明文「governance/code-loop/被gitignore,CI乾淨checkout永遠沒有marker,上線後第一筆high推送假紅」,唯一解釋這條因果鏈的權威節點。
- S04 / 驗形式與驗內容_調研.md:整篇圍繞「治理品質」概念展開(機械強制vs散文治理、27.3%化妝式合規),本組裡唯一真正解釋這個詞而非字頻巧合的節點。
- S23 / Python補棧_計劃.md:本機實跑核對的 SARIF 支援矩陣(ruff/bandit/mypy/ty/pip-audit)。
- S23 / iOS與Node後端補棧_計劃.md:同樣本機/世界事實核對的 SARIF 矩陣(SwiftLint/Periphery/ESLint/Biome)。
- S23 / 社群規則覆蓋每次提交_計劃.md:明確主張共用接口是既有SARIF橋,並記載 OSV-Scanner SARIF 嚴重度欄位陷阱。
- E05 / 固定席降噪A層_計劃.md:操作對象就是 retrieval_eval.py(edit_universe/eval_edit/must_ratchet),立了機械合約。
- E06 / 每支檔有家.md:about_code 明列 scripts/hooks/pre-commit,是正式的家。
- S26 / 簿記白名單漏canary與bypass帳.md:直接記錄canary-log.jsonl沒被簿記白名單涵蓋導致留痕失效的真實事故。
- S22 / Codex完全支援_計劃.md:dispatch-lens armed token TTL 機制(10分鐘、--arm/--claim)的原始設計文件,記著TTL優先序被重寫時掉了的真bug修法,權威說明。
- S22 / 主session鏡頭利用率_計劃.md:詳細記錄 impact-hook 自己的TTL冷卻窗機制(20分鐘)、r1代碼審抓到的TTL標記時機真bug與修法、專屬測試,權威說明。
- S07 / vendored自測3紅_來源repo專用測試漏標skip.md:自陳「本篇為歷史事故敘述」,完整記錄真實消費端事故。
- S07 / 探針沙盒改動真全域機器狀態.md:摘要開頭直接標[事故],記錄探針把使用者真實~/.claude/skills弄斷的事故。
- E02 / bound-tests-gate.md:文中明講波及計算靠pre-push算一份寫進暫存檔給這道閘(bound-tests --from-json)讀,正是被改那行_prosp.get(rel_file)服務的下游消費者。
- E13 / 收工閘漏掉純Bash改碼.md:活樣本明確舉例另一session用Bash改daily-governance.sh卻沒被收工閘偵測到,正是本次用Bash改同一支檔案不看會漏掉的前提。

## ② 難判、可能跟另一席不一致的幾筆

- E17 / Projects/全repo審視_計劃.md(判1):這篇是後來 Systems/授權與歸屬.md 這個系統節點的源頭發現,內容其實重疊(同一批事實),但它是巨型審視文件裡一小段。另一位評審如果覺得「源頭發現」比「後來的權威節點」更該算 2,可能會標更高;我認為權威節點已經完整吸收了這段內容,所以降一級。
- S09 / Projects/Agentflow吸收_調研.md(判1):這篇深入討論「合約(★INVARIANT★)不能建在推測上」的來源守衛機制,內容紮實,但它是從很窄的一個角度(Check J 來源軸)切入合約這個詞,不是泛用的「什麼是合約」解說,難判是不是「必看」。
- E16 / Projects/全repo審視_計劃.md:逐字點名該檔但已被授權與歸屬.md取代為權威版本,判1;另一席可能判2。
- S28 / 兩篇 Issues:已結案真實坑事故但範圍窄,另一席可能判0或2。
- S29 / codex-harness.md 與 辯方表態記帳.md:都只是審查/審計主題底下的子面向,另一席可能判0或2。
- SY01 / 檢索核心重建_計劃.md:Check K 只當評測金標例子引用,沒解釋本身,判0;另一席可能判1。
- E12 / bound-tests-gate.md:同屬 impact 分析家族但 about_code 沒列該 hook、正文沒提 incidents 欄位,判0;另一席可能判1。
- 全repo審視_計劃(S21,判1):986行清單只有一條具體提到BM25F,其餘不相關,另一席可能判0。
- 圖譜進迴圈入口栓_計劃(S21,判1):有一句關於BM25F分數跨查詢不可比的技術結論,但整篇主題是另一個機制,另一席可能判0或2。
- 多路召回與宣告式欄位_調研(S21,判1):明確寫BM25F佔六成權重並討論融合方式,但屬背景說明,另一席可能判0或2。
- autonomous-iteration-loop.md(E21,判1):只順帶提到情境探針,沒討論scenario_probe.py的Agent工具設計本身,另一席可能判0。
- git-hooks路徑指向樹內(S18判2、S20判1):同一篇在不同查詢分數不同——anchor查詢直接點出破口(2合理),worktree查詢只是列受影響範圍之一(1或0都說得過去)。
- 自足性審計閉環_計劃(S20,判1):有明確worktree死刑結論但整篇主要講另一個loop設計收斂,另一席可能判2。
- enforcement儀表板_計劃(S18,判1):anchor baseline是九層防護裡明確一層,但整篇是講更大的儀表板,另一席可能判0。
- E22 → 全repo審視_計劃.md:裡面 #17 那段確實明寫 ci.yml/LUMOS_SKIP_BOUND_TESTS,是這個決定的「發現源」,但內容已被另一篇專門的裁定計劃取代覆蓋,所以標 1 不標 2;另一席若認為「原始事故發現點也算必看」可能標 2。
- S30 → 條款綁測試算進度_計劃.md 與 設計審收斂重定義_計劃.md:兩篇都大量使用「CI 帳」「治理帳」「記帳型態」等詞,是真的在討論帳本設計,但都不是「帳」這個概念本身的權威定義節點,標 1 或 0 見仁見智,偏向 1(有實質內容,非巧合疊字)。
- S30 → 建了沒人跑批次裁定_計劃.md:「帳」在裡面只當「次數證據」用(如「帳 0 用」),沒有真的在講帳本機制,標 0,但因為它反覆出現「帳」字,另一席可能誤標高。
- SY02 → 檢索核心重建_計劃.md:唯一命中處是把「confused deputy」當成評測金標題目的例子引用,不是在講這個安全概念本身(真正權威節點是 Systems/nested-agent-permission-scope.md,但它不在本次候選清單裡)——標 0,如果另一席把「查詢詞逐字出現」直接算相關,可能標 1。
- E09 / Systems/anchor-integrity.md:merge-claude-settings.py 實際不在 ANCHOR_FILES 清單(已核對 anchor-baseline.json),但同屬 hook 安裝註冊這條線,另一席未查 baseline 可能標 1。
- E03 / Projects/推播miss量測_計劃.md:內文提到「test_lumos.py 是錨點檔,改完要 anchor approve」是真實重要事實,但該專案主題本身(推播漏網量測)跟這次 diff(融合權重測試值)無關,1 分或 0 分見仁見智。
- S10 / 標籤系統盤點_調研.md 與 標籤系統精簡_計劃.md:各記一條具體排序分數異常,內容扎實但已被檢索核心重建_計劃引用總結過,算不算獨立必看見解不同。
- S12 兩篇:「審計」在兩篇裡都不是標題主題而是技術內容的一部分,換評審可能標 0。
- S08 / 標籤系統精簡_計劃.md:S6 那段回滾教訓真實可泛化,但整篇主題是標籤精簡不是回滾機制,1 分是否足夠呈現價值見仁見智。
- SY03 / Agentflow吸收_調研.md 與 OpenSpec_調研.md(皆判1):不是權威節點,只是拿 openwiki 當比較對象或已撤回類比,另一席可能判 0 或 2。
- E10 / enforcement可觀測性_計劃.md(判1):改了 pre-push 好幾個退出點的記帳行為,但靠內容深度關聯不是 about_code 宣告,另一席可能升到 2。
- S27 / 推新分支時風險分級拿空樹當起點.md(判1):經典「閘失真變儀式」案例,另一席可能升 2 或降 0。
- S13 / 檢索核心重建_計劃.md(判0):文中出現「guard kill」四字但只是題庫例題名稱,沒解釋本身,另一席可能單憑字面命中給 1。
- S13 / 其餘四筆(皆判1):每篇只在一兩行提到 guard kill 旁側事實,沒有權威說明本體,另一席可能整批降 0 或個別升 2。
- S04 / 棧別提問表態閘.md 與 棧別提問表態閘_計劃.md(皆判1):大量描述治理帳機制細節但核心主題是表態閘功能,嚴格評審可能判0。
- S04 / 沒有圖譜的專案答不完表態題.md 與 loop-list開著的迴圈.md(皆判1):各帶一段治理帳運作說明但整篇主題是別的議題。
- E11 / 2026-07-05_code-loop必用守衛.md 與 code-loop必用守衛_計劃.md(皆判1):HEAD-sha綁定機制源頭設計文件,但沒碰「要不要版控」這個具體問題,可能壓到0。
- S26 / 簿記白名單漏canary與bypass帳.md(判2):已resolved歷史事故筆記,不是解釋canary機制「現在怎麼運作」,另一席可能只值1。
- E11 / 兩席相反時端出張力_計劃.md(判1):只有實務隱患段落一句話提到marker不版控,其餘全文是張力表態機制,邊界判斷。
- S22 / 執行DAG_調研.md 與 codex-harness.md(判1):只是引用/摘要TTL屬性沒有深入展開設計過程,但帶出TTL寫死600秒不可調的具體事實,1或2見仁見智。
- S22 / 世界repo掃描2026-09-02_調研.md(判0):唯一TTL是外部工具MCP Agent Mail的lease+TTL,不是本repo機制且已裁定不辦。
- E07 / autonomous-iteration-loop.md(判1):明講機制本體見risk-tiered-review、定位為背景,但自己CONVERGED段落max cap=6輪跟risk-tiered-review的high=cap≥8是否衝突沒把握確認。
- S07 / 把自己的推論寫成repo明文寫過.md(判1):內容豐富但是行為/紀律層自我糾錯記錄不是技術系統事故,0/1/2見仁見智。
- E02 / bound-tests-gate.md:原判 2(理由:pre-push 靠 impact 算一份 payload 給這道閘讀,被改的 _prosp.get(rel_file) 屬於 impact 的一部分),但親自對照 scripts/lumos 原始碼後發現這行實際餵的是「incidents 事故比對」那段邏輯,不是 bound-tests-gate 真正讀的「固定席合約測試」那段——連結存在但比原判弱,改判 1。這筆兩次判讀落差最大,最可能跟另一席不同。
