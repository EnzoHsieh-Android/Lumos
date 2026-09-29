severity: major

## F1 專案宣告缺少可互通的設定 schema

severity: major

blocking: 是

判準：不改，實作者必須自行發明欄位名稱、資料形狀與錯誤策略，消費專案會產生彼此不相容的設定。

spec 段落：〈要做什麼〉第 1(a) 點、[S1]、〈回退〉。

引句:「當專案宣告清單裡有兩條樣式都命中同一支檔,角色判定應取清單裡第一條的角色,且宣告優先於匯入與副檔名判定」

問題：spec 沒有定義 `.lumos/config.json` 的實際鍵名、清單元素形狀、樣式與角色的欄位名稱、合法角色值，以及非清單、缺欄位、未知角色或非字串樣式的處置。實作者可以各自做出 `review_roles`、`path_roles` 或 `applyTo` 等不同協定；測試若沿用實作自己的形狀仍可通過，但消費專案無法知道該寫哪一種。畸形設定若未定義 fail-open 行為，也會讓 `pitfalls` 或派工掛鉤整段失敗。

佐證：

file: `scripts/lumos:20505` 現有設定讀取器 `_stack_questions_config` 明確定義區塊名稱、回傳形狀與非法值處置。

file: `scripts/lumos:20522` 現有設定對精確鍵 `stack_questions.gate` 驗證值域並在非法時回退。

file: `scripts/lumos:20527` 數值欄位也明定型別、範圍與預設值。

file: `scripts/lumos:26394` `_cochange_excluded` 只提供 glob 比對語意，沒有提供新設定欄位的 schema 或錯誤策略；「沿用比對寫法」補不了上述合約。

## F2 角色判定沒有定義要讀哪個 Git 版本

severity: major

blocking: 是

判準：不改，同一個 `A..B` 會隨目前 checkout 的工作樹不同而得到不同角色卡，並可能把錯誤結果快取在同一組 commit 下。

spec 段落：〈要做什麼〉第 1(b)–(d)、第 3 點、[S3]–[S5]。

引句:「手機與 Android 畫面:看檔案本身的匯入——.kt/.java 匯入 android 或 androidx、.swift 匯入 SwiftUI 或 UIKit、.dart 匯入 flutter 套件 → 前端」

問題：spec 只規定刪除檔讀改動前版本，沒有規定新增或修改檔的匯入、最近的 `package.json`、以及 `.lumos/config.json` 應從範圍終點、工作樹或其他快照讀取。具體輸入為：checkout 在 C，執行 `lumos dispatch-lens A..B`，而 B 與 C 的 `package.json` 或角色宣告不同。照既有 helper 直接實作會讀 C，角色卡卻被當成 A..B 的結果；換一個 checkout 再跑同一範圍便得到另一答案。

佐證：

file: `scripts/lumos:31303` `cmd_dispatch_lens` 接受呼叫者給的任意 `<base>..<head>`。

file: `scripts/lumos:31314` 目前只要求兩端是本地存在的 commit，沒有要求 head 等於工作樹 HEAD。

file: `scripts/lumos:20455` `_node_flavor` 從工作樹路徑開始尋找 `package.json`。

file: `scripts/lumos:20463` `_node_flavor` 直接以 `Path.is_file()`、`read_text()` 讀工作樹，不讀範圍終點。

file: `scripts/lumos:30627` 現有派工鏡頭在需要版本一致時會明確用 `_json_at_ref` 讀 base 版設定，證明此處不能靠工作樹讀取隱含決定。

## F3 兩條派工通道尚未真正與圖譜計算解耦

severity: major

blocking: 是

判準：不改，照最直接的接法把角色卡加入 `cmd_dispatch_lens`，圖譜計算一超時，Claude 與 Codex 兩條通道仍會一起失去角色卡，直接違反 [S5]。

spec 段落：〈要做什麼〉第 3 點、[S5]、[S6]、〈實務隱患〉時間預算。

引句:「角色卡另走一次快速計算,只看改動檔清單、檔案匯入與 package.json,不跟圖譜那段共用預算與快取;圖譜那段超時或算出空白時,角色卡照附。」

問題：spec 宣告「另走一次」，但沒有定義兩份結果在何處、以何種失敗語意合併。Claude 掛鉤目前只啟動一個 `dispatch-lens` 子行程，子行程超時後整份 stdout 被丟棄，只附固定超時說明。Codex 的 `--arm` 更是在完整圖譜計算成功後才建立可認領 token；圖譜慢住或回錯時根本沒有武裝內容可領。必須明定兩通道各自的組合順序、獨立 deadline 與「圖譜失敗但角色成功」的輸出形狀，並各有超時驗收案例；目前 [S5] 沒有覆蓋 Codex 武裝失敗路徑，[S6] 只驗正常領取。

佐證：

file: `scripts/hooks/claude/dispatch-lens-hook.py:298` Claude 通道只組一個 `dispatch-lens` 命令。

file: `scripts/hooks/claude/dispatch-lens-hook.py:315` deadline 只加在同一個圖譜命令上。

file: `scripts/hooks/claude/dispatch-lens-hook.py:320` 該命令逾時時只附超時說明並返回，沒有第二份結果可保留。

file: `scripts/lumos:30988` Codex `--arm` 先同步呼叫完整 `cmd_dispatch_lens`。

file: `scripts/lumos:30991` 圖譜命令非零時立即返回，不會建立角色卡武裝。

file: `scripts/lumos:31033` 武裝 metadata 與 token 只在完整圖譜計算成功後寫入。

## F4 Java 手機資料層在兩節得到相反角色

severity: minor

blocking: 否

判準：[S3] 已替實作者選定「後端」，不至於無法施工；但〈已知限制〉會向使用者承諾相反行為，必須訂正其中一處。

spec 段落：〈要做什麼〉第 1(c) 點、[S3]、〈已知限制〉。

引句:「(c) 副檔名:.vue/.svelte/.tsx/.jsx/.css/.scss/.html → 前端;.cs/.java/.py/.sql → 後端(.java 已先過 b)。」

引句:「不匯入畫面框架的手機端檔(例如純資料層)判不出、不附卡;這是刻意的,寧可不附也不附錯。」

問題：Android 專案中的 `UserRepository.java` 若沒有 `android` 或 `androidx` import，第 1(c) 點與 [S3] 判後端並附後端卡；〈已知限制〉卻說手機純資料層判不出且不附卡。這不是邊界解讀差異，而是同一輸入得到兩個輸出。

## F5 消費專案的 vendored 工具檔沒有排除規則

severity: minor

blocking: 否

判準：不改不會破壞推送閘，但消費專案例行更新 Lumos 時會只因工具自身的 Python 檔而附後端卡並灌高後端檔數，形成具體注意力噪音。

spec 段落：〈要做什麼〉第 2–4 點、〈實務隱患〉、消費專案可得性。

引句:「兩張角色鏡頭卡,內容單源放在 lumos 本體(跟棧別題庫同處,消費專案拿得到)」

問題：spec 說角色計算只看改動檔清單，卻沒有沿用現有的消費專案 vendored 排除政策。具體輸入是消費專案執行 `lumos update`，diff 只有原封不動更新的 `scripts/lumos`、測試與 hooks；按副檔名規則它們會被算成後端，於是沒有應用程式變更仍附後端卡。角色統計與派工提示應明定是否使用現有 `vend_skip`；本體 repo 則仍須保留掃描。

佐證：

file: `scripts/lumos:27227` 現有風險掃描特別區分工具鏈本體與消費專案。

file: `scripts/lumos:27231` 消費專案會根據 diff 兩端計算原封不動的 vendored 工具檔並排除。

file: `scripts/lumos:27030` `_stack_changed_ok` 是既有改動檔過濾入口。

file: `scripts/lumos:27036` 程式內已記錄不排除 vendored 工具會讓消費專案的報告全被工具碼撐滿、要求審查非專案自行撰寫的程式。

## 逐節讀取結果

- Frontmatter、summary、decisions：已讀，無 finding。
- 〈現況〉：已讀；所述 `_node_flavor`、棧別題組、慣例 skill、Claude/Codex/設計審三條通道均已對照，無其他 finding。
- 〈要做什麼〉：已讀；finding 為 F1、F2、F3、F5。
- 〈已裁〉：已讀，無 finding。
- 〈已知限制〉：已讀；finding 為 F4。
- 〈驗收條款〉：已讀；F1、F2、F3 指出的失敗路徑尚未被條款完整覆蓋。
- 〈回退〉：已讀，無 finding；有列出掛鉤指紋重核、設定死鍵與不碰帳本。
- 〈實務隱患〉：已讀；時間預算問題見 F3，消費專案問題見 F5。
- 〈撤除條件〉：已讀，無 finding。
- 〈不做〉：已讀，無 finding。
- 文件內所有 `[[…]]` 交叉引用均已核對，目標全部存在；沒有壞交叉引用。

## 實務隱患鏡頭結論

- 併發：無。新增判定本身是唯讀；Codex 現有領席以原子 rename 認領，沒有新增共享寫入競態。
- 效能與派工時間預算：有，見 F3。兩通道尚未定義真正獨立的計算與超時合併。
- 回滾：無。spec 已列出範本、兩通道、輸出、設定讀取與測試的撤除順序，也承認消費端會留下無人讀取的死鍵。
- 消費專案與 vendored Lumos：有，見 F5。功能本體可隨 vendored CLI 取得，但角色輸入缺少既有 vendored 排除政策。
- 設定輸入健壯性：有，見 F1。新欄位沒有 schema 與錯誤處置。
- Git 版本與快取一致性：有，見 F2。角色輸入來源沒有綁定 diff 端點。
- 對外送出、金流、不可逆資料操作：無。功能只讀 repo 與設定並產生提示文字，不呼叫外部服務、不改業務資料或治理帳。

總結:最嚴重 severity 是 major、blocking 共 3 條。
