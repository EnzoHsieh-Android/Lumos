severity: major

## F1 「light」判定按「有沒有計劃過關」而非「每支改到的檔都被算過」,可讓不相干的危險改動搭便車跳過全套測試

severity: major
blocking: yes

攻擊路徑四件:
- 誰:任何能推分支的協作者(或被接管帳號、被合入的惡意 PR 提交者)——不需要特殊權限,建圖譜計劃節點是日常操作。
- 從哪裡:同一次推送裡放兩種東西——① 一支已經通過 spec-gate、`plan_risk: low`、`status: doing`、全靠人驗(沒有 `[test:]`)的計劃節點,只改它連到的某個小檔案(讓小改動閘通過);② 另一支完全不相干、風險真正高的程式改動(例如改 `scripts/lumos` 或 `scripts/hooks/pre-push` 本身的執行/驗證邏輯),而且這支檔的「家」(每支檔有家的 Systems 節點)沒有被任何 `status: doing` 的計劃連結,或雖被連結但那個計劃的 `plan_risk` 不是 `low`。
- 送什麼:一次 `git push`,diff 同時包含上述兩塊。
- 拿到什麼:`_spec_gate_push_check` 的判定邏輯是「只看有沒有被掃進來的計劃全過」而不是「這次改到的每一支檔都要被某個已判定的計劃覆蓋到」——不相干的危險檔案如果沒有被任何 doing 計劃連結(或連到的計劃 risk≠low 而被整個跳過評估,見下方 file 引用),就完全不進 `bad`/`oks` 的計算,不會讓 `bad` 變成非空。只要剩下被評估到的計劃全過,`_spec_gate_push_check` 依舊印出「改動風險分級:light」、回傳 0(不擋)。pre-push 這次改動新加的偵測邏輯只用純文字比對這行輸出,危險改動就這樣被貼上「light」標籤。

引句:「if [[ "$_suite_this" == "full" ]] && grep -q '改動風險分級:light' "$_sg_out"; then」

這一行是本次 diff 新增的核心判斷:`grep -q` 純文字比對 `spec-gate --push-check` 印出的整段 stderr+stdout,只要那段輸出裡出現「改動風險分級:light」這行摘要,就把 `_suite_this` 從 `full` 降成 `light`,推送前只跑「文件子集 + 關鍵字子集」,不跑全套。

而「改動風險分級:light」這行摘要本身,判準只在 `bad` 是不是空:

file: `scripts/lumos:5894`(不在 patch 範圍內,是被這次 diff 新接上「跳過全套測試」動作的既有函式)
```python
if not bad and oks and all(mo for _p, mo in oks):   # 計劃風險低+全靠人驗+小改動閘過 → 改動風險分級 light
    print(f"{P} 改動風險分級:light(...)——代碼審只派架構對齊席;lumos loop next <編號> --tier light")
```

`bad`/`oks` 只由 `_spec_gate_push_scan` 逐一掃「被碰到的計劃」(`_spec_gate_push_candidates`)產生;而不相干、沒被任何 doing 計劃連到的改動檔完全不在這個掃描範圍內:

file: `scripts/lumos:5814-5816`
```python
if not tests:   # 全靠人驗:沒有測試可跑,改跑小改動閘(四維度全過才放行)
    sc = _small_change_check(env, rr, idx[4], prel, n)
    ...
```

file: `scripts/lumos:5834-5839`(`_spec_gate_push_scan` 只逐一掃 `plans` 集合,通過才 append 到 `oks`,不通過才 append 到 `bad`;完全沒被納入 `plans` 的檔案不會讓 `bad` 變非空)

換句話說:`_spec_gate_push_check` 原本只是「計劃風險低留痕」這個窄範圍問題的守門員,它的 rc(擋/不擋)和「light」摘要行,天生就沒有「這次 push 動到的所有檔案都被我看過」這個保證——它只保證「我有看到的計劃都過了」。這次 diff 之前,這個 print 出來的「light」字樣只是一句提示文字(建議代碼審派哪一席),沒有任何機械後果;這次 diff 第一次把它接成「跳過全套測試」的機械判準(`_suite_this = "light"` → 分片只帶 `--suite docs`、多跑一趟範圍窄很多的 `--suite keys`),把一個原本只是「建議」的訊號,升格成一個會實際少跑測試的閘門,但沒有補上「light 判定必須覆蓋這次改到的每一支檔」這個前提。

為什麼是 bug 不是風格:這正是報告格式裡列的「該跑全套卻跑了子集=major 以上」——一個真正危險、完全沒被任何 doing/低風險計劃覆蓋到的程式改動,可以搭一個無關的、真的小的、真的低風險的計劃的便車,讓本地 pre-push 把整包 push(包含那支危險檔)判定為 light,本地端只跑文件子集加一個用函式名/檔名字串比對挑出來的小範圍子集(很可能完全挑不中真正該測的那支危險檔案的合約測試,因為 `--suite keys` 靠的是 `affected_keys`——但 `affected_keys` 是由 `_affected_test_keys` 從**這整段 diff**算出來的,不是只從「未被計劃覆蓋的那幾支檔」算,理論上仍可能抓到危險檔的函式名而選中相關測試,但沒有任何機制保證一定選中,純靠原始碼字面提到函式名這個弱連結)。

止血範圍說明:CI 那邊的 suite 判定(`lumos pitfalls --diff ... --json` 的 `suite` 欄)完全獨立於 spec-gate 的 light 判定,只看檔案是不是落在 `_DOCS_ONLY_PATHS` 白名單——危險程式檔不在白名單裡,CI 仍會跑全套,所以 CI 是這條路徑唯一沒被弱化的守門員(patch 註解自己也寫「CI 會跑全套當後盾」)。所以這個洞的實際傷害是:**本地 pre-push 這一關的測試覆蓋被弱化**(開發者/攻擊者本機推送前看到的是「文件子集通過」的假訊號,真正的紅測試要等 CI 才會被抓到,如果 CI 沒有嚴格擋 merge 或攻擊者能在 CI 跑之前就讓變更生效,防線就少了一層),而且這行「light」摘要文字本身也被 code-loop 建議拿來決定「代碼審只派架構對齊席」(`--tier light`),等於同一個判定失誤同時弱化了「測試」與「代碼審派工」兩層。

## F2 已看,無新增獨立發現

已檢查但沒有另外構成獨立發現的路徑(逐一列出,依派工詞的六類走過):

1. 不可信輸入流到危險操作:`--keys` 在 `_keys_suite_select` 用 `re.escape(k)` 逐一跳脫後才組 regex(`scripts/test_lumos.py` patch 新增段),沒有 regex/shell 注入空間。`_SUITE_KEYS` 在 pre-push 裡兩處使用都有雙引號包住(`--keys "$_SUITE_KEYS"`),不會被 shell 重新斷詞或注入指令。CI 的 `$extra` 雖未加引號,但它只會是硬編字面值 `""` 或 `"--suite docs"`,不受攻擊者輸入影響,不構成注入。`_affected_test_keys` 從 `git diff` 的 `def 名字` 只用 `[A-Za-z_][A-Za-z0-9_]*` 這種嚴格字元類擷取,不會帶進特殊字元;檔名關鍵字雖然理論上可以含逗號等字元(可能造成 `--keys` 清單被錯誤切分,產生誤選/漏選測試的正確性問題),但不構成資安洞(不會被當指令執行,頂多讓 keys 子集選錯,而選錯的後果是「更保守」——選不到就退回全套或印訊息,不是「選到更危險的少測」)。
2. 登入與權限:此次 diff 沒有新增任何登入/權限判斷,無新增面。已看,無。
3. 密鑰與個資:`_sg_out`/`runner-args.log`/暫存目錄都用 `mktemp`/`mktemp -d`,沒有寫入密鑰或個資;`suite_reason`/`affected_keys` 這些新欄位只含檔名與函式名,不含機密內容。已看,無。
4. 加密與傳輸:此次 diff 不涉及任何網路傳輸或加密邏輯。已看,無。
5. 執行邊界:`_head_is_shebang` 只讀被推檔案的前 200 bytes 判斷是不是 `#!`,不執行;`inspect.getsource` 只用在 `scripts/test_lumos.py` 自己模組內、已經 import 進行程序的 `t_*` 函式物件上(這些函式定義本身就是這次要合併進主幹、要過審的原始碼,不是從攻擊者可控的外部路徑動態載入執行),沒有把攻擊者可控字串丟進 `exec`/`eval`/動態 import。CI 的 `git cat-file -e "$BEFORE"` 只是檢查物件存在,`before..sha` 兩點差異法即使遇到 force-push 也只是比較兩個真實存在的 commit 樹,不會被騙出錯誤的差異範圍。純文件白名單本身對「白名單不是非程式檔」有機械檢查(`_docs_only_file` 對副檔名與 shebang 都會擋,測試 ②③④⑧ 都覆蓋了 docs/ 下的 .py、shebang 檔、skills/ 的 md、.github/ 的檔仍判 full),`assets/`(svg)本身只被讀取顯示,沒有被當程式解析執行的路徑。真正的執行邊界問題是 F1(spec-gate 的 light 判定範圍不完整,被新接上「跳過測試」這個機械後果),已獨立成篇不重複列。
6. 行動端:此次改動不涉及任何行動端程式碼或發佈流程。已看,無。

另外檢查了 `_BOOKKEEPING_DIRS`(`governance/code-loop/`、`governance/review-reports/`、`governance/replay/`)被整批從 `_test_suite_for_range` 的檔案清單裡剔除、不經過 `_docs_only_file` 的副檔名/shebang 檢查這件事:理論上可以在這三個目錄底下塞一支帶 code 副檔名的檔案而不觸發 full。但實測這三個目錄本身沒有任何地方被 `exec`/`import`/`subprocess` 當程式路徑執行(只被當唯讀的稽核紀錄讀取),而且「每支檔有家」(`home check --diff`,`scripts/hooks/pre-push:202`)是完全獨立、不受這次 diff 影響的另一道閘,既有測試就已經證明「程式檔搬進卷證目錄 → 不豁免,落點外擋」(`scripts/test_lumos.py:43694-43696`)。所以這條路徑有兩層既有守衛頂著,沒有把它算成獨立發現,只在此記錄「已看,推論上有交叉驗證但沒有獨立重現」。
