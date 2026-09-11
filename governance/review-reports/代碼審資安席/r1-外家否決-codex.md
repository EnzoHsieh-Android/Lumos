severity: major

已逐節讀完全文，並核對四個圖譜連結、既有函式與欄位、CLI 參數、§7.6／§7.7、決策 d5／d6；新增 helper、常數、§7.8 與測試名稱均按待實作項目理解。

E1 — 前輪資安報告能替不相接的版本背書
severity: major
blocking: 是
判準：會，實作者照 S2 只驗席名與報告指紋，會把沒有版本關聯的舊資安審查當成本輪有效證據。
引句:「資安席在非判定輪(r1 有、判定輪 r2 沒有)→ 這一步 ok(迴圈層級)」
r1 資安席審 A、產出 B，r2 卻改審不相接的 X，只要 r2 自身指紋一致且零發現，兩道條件仍同時成立。
必須驗證採用的資安輪至判定輪之間的版本鏈，並增加斷鏈反例。
file: `scripts/lumos:14958` 現行處置閘只傳入 `[latest]`；唯讀執行實際 helper，單輪輸出 `(None, '1 輪鏈驗訖')`，加入前輪才輸出「鏈續性斷裂」。
file: `scripts/lumos:6515` 跨輪指紋檢查已存在，但傳入單輪時不會執行。

E2 — 凍結會把資安證據失效洗成通過
severity: major
blocking: 是
判準：會，正常問閘應拒絕的缺失報告，會在凍結重算時變成有效證據，之後回放仍宣稱一致。
引句:「所以這一步在該模式下只看帳列(席名、tier、有沒有記 `report_sha256`),不重讀報告檔」
r1 資安報告已刪除或指紋不符、r2 其餘條件通過時，第一趟資安判定失敗不會中止凍結，第二趟依投稿規則跳過讀檔，覆寫成通過。
應將實際採用的前輪資安報告納入凍結閉包，凍結時驗真、回放時驗完整性，並測試凍結前報告已壞的情況。
file: `scripts/lumos:634` 第一趟只在退出碼 2 時停止，退出碼 1 繼續執行。
file: `scripts/lumos:648` 第二趟帶 `spec_sha_override` 重算並覆寫結果。
file: `scripts/lumos:657` 閉包只收判定輪檔案，前輪資安報告不受後續檔案完整性檢查保護。

E3 — 全面排除測試檔會漏掉真正的執行邊界
severity: major
blocking: 是
判準：會，資安席會因檔名而忽略確實會執行的程式，以及其中新增的真實密鑰。
引句:「不報:DoS / 資源耗盡 / 限流(歸併發資源席)、測試檔、非關鍵欄位上沒有攻擊路徑的輸入驗證。」
具體場景是高風險變更在測試檔加入真實服務憑證，或測試把外部輸入拼接進 shell；公開讀者可取得憑證，或該測試執行時跨越命令執行邊界，卻被這條排除規則直接消音。
排除條件應限於不可利用的測試假資料，不能涵蓋真憑證與實際執行路徑。
file: `.github/workflows/ci.yml:25` CI 直接執行 `scripts/test_lumos.py`，測試檔是可執行材料。

E4 — S5 的同步指示與設計審排除範圍衝突
severity: minor
blocking: 否
判準：會造成文件實作選擇歧義，但 S1 已明定範圍，因此屬可局部修正的文字矛盾。
引句:「以「架構對齊」出現的每一處為清單逐一對過(commands/06、code-loop reference.md、design-loop SKILL.md 等),列席位的地方都補上。」
此指示把設計審派席步驟也列為補寫位置，與 S1 的設計審各級不加席矛盾；應明寫只有描述代碼審 high 編制的段落新增席位。
file: `skills/lumos-design-loop/SKILL.md:20` 此處列的是設計審派席流程，並非代碼審 high 編制。

E5 — 資源分析引用的既有函式與 S2 自相矛盾
severity: minor
blocking: 否
判準：不直接造成壞系統，但會讓實作者誤判可沿用的抽象與重構範圍。
引句:「資源:讀檔走既有留痕重驗函式;不開連線、不拿鎖。」
S2 明確說留痕檢查目前內嵌、須先抽取 helper，本節卻稱既有函式；應改為引用 S2 將抽取的函式。
file: `scripts/lumos:15041` 現況為處置閘內的逐席檔案檢查迴圈。
file: `scripts/lumos:5497` 既有 `_sha256_file` 只計算指紋，不負責整筆留痕有效性判定。

E6 — 編制驗收指令原樣執行失敗
severity: minor
blocking: 否
判準：不改核心設計，但驗收者照抄會在進入編制輸出前被參數檢查擋下。
引句:「編制表:`loop next code-x --tier high` 印得出資安席」
實際執行 `python3 scripts/lumos loop next code-x --tier high` 得退出碼 2，訊息要求首次呼叫帶 `--orchestrator claude|codex`；驗收需補此參數，並分別覆蓋兩種編排者。
file: `scripts/lumos:8142` 零帳列的新迴圈未指定編排者時直接拒絕。

逐節覆核：

- 開頭摘要：已讀，問題對應 E1、E2。
- 緣起：已讀，無 finding；⚠ 190 份派工單與九個消費專案的歷史統計未提供固定樣本，不能獨立重建其口徑。
- 人裁：已讀，無 finding。
- PRIOR-ART：已讀，無 finding；已核對 [Anthropic 原始提示](https://raw.githubusercontent.com/anthropics/claude-code-security-review/main/claudecode/prompts.py)、[OWASP Top 10](https://owasp.github.io/www-project-top-ten/) 與 [MASVS](https://mas.owasp.org/MASVS/)。
- 條款：S1、S3、S6 已讀，無 finding；S2 對應 E1、E2，S4 對應 E3，S5 對應 E4。
- 邊界與不做：已讀，無 finding。
- 承認的限制：已讀，無 finding；不重報已明確接受且附覆核日期的觸發範圍、pass 脫鉤及席名冒充限制。
- 實務隱患：已讀，問題對應 E2、E5。
- 驗收：已讀，問題對應 E1、E2、E6。

風險逐類覆核：

- 併發：一般 `loop status --disposal` 會拒絕壞 JSON 行；凍結入口則跳過壞行，投稿的 fail-closed 說明不能概括兩條路。
  file: `scripts/lumos:7364` 一般入口累計解析失敗行。
  file: `scripts/lumos:606` 凍結入口解析失敗後直接繼續。
- 效能／資源：新增掃描與報告雜湊成本有限，但仍沿用整檔讀入；函式現況矛盾見 E5。
- 回滾／凍結：程式可撤回、帳本無新增欄位的判斷成立；凍結證據完整性缺口見 E2。
- payment：排除成立，本案未新增付款動作。
- external-send：沿用既有派席通道的範圍判斷成立；「本機子代理」本身不能證明模型材料沒有對外傳送。
- prod-irreversible：本案沒有新增生產不可逆動作，排除成立；守衛錯判仍須依 E1、E2 處理。

最嚴重 severity 是 major，blocking 共 3 條。