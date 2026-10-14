severity: major

我只讀、沒寫任何檔案,所以暫存目錄沒建,也沒有東西要刪。以下行號都對照 `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos`。

## 第 5 條:碰到帶殘留合約就升 high

severity: major
blocking: 是 — 照字面做會把約 4.7 秒的圖譜載入塞進推送前的熱路徑,而且不載圖譜就做不出來。
引句:「改動碰到的檔若在某篇帶 `[residual:]` 合約的節點 about_code 裡,分級升為 high」
問題:`_pitfall_tier` 的註解明講它是 vault-free,因為 pre-push 熱路徑不載圖譜。
- 它的輸入只有 `claims`、`files`、`repo_root`、`diff_range`,見 `scripts/lumos:43677`。
- `cmd_pitfalls` 的註解也寫「Env(vault) 實測 4.7s,不能每輪付」,見 `scripts/lumos:44389`。
- 要查「哪些節點帶殘留」和「哪些節點的 about_code 管這支檔」,就得載入整個圖譜。
- 計劃沒說要放寬 vault-free,也沒說改在別處升級。例如 `spec-gate --push-check` 本來就載圖譜,`_pitfall_tier` 的註解也這樣分工;派工鏡頭也有「檔對節點」的對照。
- `--no-lint --json` 這條路徑也被 `code-loop` 的 tier 判定用,見 `scripts/lumos:51064`。

失敗情境:
- 實作者在 `_pitfall_tier` 裡加 `Env(vault)`,每次 push 多付約 4.7 秒。若他改在別處升級,`pitfalls --diff` 與 `code-loop` 讀到的 tier 又不一致。
- 該讀哪棵樹也沒定。若讀 HEAD,一個提交同時拿掉合約上的 `[residual:]` 並改程式,就不會被升 high。依計劃全文,殘留的 tier 升級也沒有「讀 base 樹」的規定。

佐證:`scripts/lumos:43677`、`scripts/lumos:44389`。
S5 要寫成先紅的測試,需要一個含圖譜的臨時 repo,而 `_pitfall_diff_collect` 現在不接 vault。

## 第 3 條:`[residual:]` 要進 `INV_TAG_RE`

severity: major
blocking: 是 — 計劃沒說要改這支共用正規式,照做會讓寫過殘留的合約對不上它的家與定位。
引句:「`[audit:]` 照舊,`guard audit` 重審不碰 `[residual:]`,所以重審不會抹掉殘留」
問題:計劃只談 `AUDIT_REF_RE` 的覆蓋行為,沒提 `INV_TAG_RE`。
- 它的註解已說明:剝掉標記家族,是為了讓「乾淨宣稱文字」不被標記污染,見 `scripts/lumos:5487-5495`。
- 有 11 處行號、8 類呼叫點用它,包括 `_kill_find_contract`(`scripts/lumos:17391`)、`_guard_formal_line`(`scripts/lumos:16282`)、`strip_test_refs` 和 `guard audit` 的 `check` 閉包(`scripts/lumos:18759`)。
- 不剝的後果有兩個:
  - 位置子字串可以誤命中 `[residual:Projects/a_計劃#d12]` 裡的字。
  - 家筆記正式行與計劃宣稱文字的比對,會因為多出一段 `[residual:…]` 而相等判斷失敗。

失敗情境:
- 合約行先加了 `[residual:…]`。之後 `guard kill-add` 或 `guard settle` 用原宣稱句去找家的正式行,比對失敗,回「找不到」。
- 或是 `guard audit "d12"` 誤命中殘留標記內的 `d12`。
- 註解也說 `[audit:]` 和 `[test:]` 同家族,所以實作者很可能漏掉這一步,因為計劃沒列。

佐證:`scripts/lumos:5495`、`scripts/lumos:17391`、`scripts/lumos:16282`、`scripts/lumos:18759`。
S2 `t_guard_audit_keeps_residual` 會綠,因為 `guard audit` 目前只換 `AUDIT_REF_RE` 的匹配。它抓不到這個洞。

## 第 3 條:`guard residual` 的定位、寫入位置與 `--remove`

severity: minor
blocking: 否 — 實作者有合理預設可選,但有四處要猜,可能與審查預期不一致。
引句:「可以多個,一個殘留決策一個標記;節點寫圖譜相對路徑、不帶 `.md`;用最後一個 `#` 切」
問題:計劃沒回答以下幾點。
- **定位用哪個函式**:現有有兩種。
  - `guard bind` 只剝 `[test:]` 再比,見 `scripts/lumos:16943`。
  - `guard audit`/`kill-add` 共用 `_kill_find_contract`,剝整個標記家族。
  - 計劃寫的「KEY 子字串」沒指明用哪支,兩者對「同時對到好幾條」的行為不同。
- **寫入位置**:`guard audit` 是行尾附加,重審時原地替換。`[residual:]` 沒寫是否也行尾附加。若殘留先於 `[audit:]` 寫入,順序就是 `[residual:]` 在前、`[audit:]` 在後,與先審後殘留的行不同。計劃沒規定順序,而且沒說是否允許寫在沒有 `[audit:]` 或沒有 `[test:]` 的合約行上。
- **重複與找不到**:同一個 ref 寫兩次怎麼辦(`guard bind` 有「已綁無需重綁」回 0)?`--remove` 找不到該 ref 時回什麼?`--remove` 是 `guard residual … --remove` 的旗標,還是位置參數,計劃沒寫。
- **「內容非空」指哪個欄位**:四欄(content/context/why/decided)中哪一欄,計劃沒寫。`valid` 的判斷可以重用 `_pq_decision_state`(`scripts/lumos:7602`),它回 `ok/missing/superseded/bad`。但計劃寫的「寫入當下就驗」只列了三種情況,沒對應到 `bad`(例如短名撞名)。

## 第 4 條:鏡頭徽章

severity: minor
blocking: 否 — 徽章的組法大致可行,但有三個條件計劃沒交代。
引句:「代碼審派工範本加一句:看到帶殘留徽章,去讀那幾筆殘留決策」
問題:`_lens_render_listed` 現在只在 `kind == "INVARIANT" and bidx is not None` 時才算並印綁定徽章,見 `scripts/lumos:48357-48364`。
- 殘留徽章若照樣放在那個 `if` 裡面,平台設定讀不到(`bidx is None`)時就不顯示,S4 就會是偶發紅。計劃沒說殘留徽章要獨立於 `bidx`。
- 鏡頭的合約行來自 base 版節點全文,不是工作樹。同一個分支裡才新加的 `[residual:]` 在鏡頭裡看不到。這對「前一次已合併的殘留」沒影響,但計劃的「碰到帶殘留的改動一律走高風險」沒提這個時序。
- 「筆數」要算標記數還是不同決策數,沒說。同一決策被標兩次時兩者不同。

佐證:`scripts/lumos:48350-48364`、`scripts/lumos:47705-47707`。

## 第 6 條:`loop escape --residual-ref` 的驗證

severity: minor
blocking: 否 — 能做,但漏掉的互斥檢查會造成靜默忽略,與該函式的既有慣例相悖。
引句:「`lumos loop escape` 加選填 `--residual-ref <節點>#<決策 id>`,記進逃逸帳的 `residual_ref` 欄」
問題:計劃沒寫驗證,只有「記進」。
- **格式與存在性**:`cmd_loop_escape` 對迴圈編號有實存驗證,對 `--defect-ref` 沒有。`--residual-ref` 若不驗存在性,錯字會被記下來,RETIRE-IF 與 REVISIT 的計數就會被污染。若要驗,可重用 `_dref_parse` 和 `_pq_decision_state`;計劃沒說驗不驗、驗失敗回幾。
- **互斥旗標**:該函式有三處明確擋「不相關參數混用」。
  - 撤回路徑的 `others=(…)` 元組(`scripts/lumos:12561`)。
  - `--list` 的混用檢查(`scripts/lumos:12604`)。
  - `--auto` 路徑。
  - 新增參數若不加進這三處,`--residual-ref` 搭配 `--list` 或 `--withdraw` 會被靜默忽略,剛好是那段註解說要避免的情況。
- **歸因**:沒要求該迴圈的合約確實帶那筆殘留,所以歸因是否真實全靠人。計劃已在別處承認這點,這裡只提醒 RETIRE-IF 的量測品質取決於此。
- `escape-stats` 的 `_escape_stats` 要加欄位、`cmd_loop_escape_stats` 的「另列」行要加輸出,兩處計劃只說「印帶 `residual_ref` 的筆數」,沒點名。

## 驗收條款 S1 到 S7 能否寫成先紅的測試

severity: minor
blocking: 否 — S1 到 S6 都能先紅,S7 的斷言對象沒定義。
引句:「應讀得到兩類分法與「對外入口測得到就是局部退化」的判準」
- S1、S3、S6:能先紅。
- S2:現況就綠,見上面 `INV_TAG_RE` 那條,抓不到真問題。
- S4:能先紅,但要先決定上面徽章獨立於 `bidx`。
- S5:要先決定升級發生在哪一層(見第一條 finding)。
- S7:`t_reference_audit_q3_rules` 要讀 `skills/lumos-project-notes/reference.md` 的某一段,但計劃沒給要斷言哪些字串,也沒說防應試化的「不逐字貼」怎麼驗。寫測試的人只能寫成含幾個關鍵詞的寬鬆斷言,容易變成把文字抄一遍的測試。

## 其他節

- 緣起、PRIOR-ART、RETIRE-IF、REVISIT、不做、回退:已讀,無 finding。
- 第 1、2 條(反例分類、分類權責):這輪沒有新增可執行性問題,已讀,無 finding。
- 第 7 條(要一起改的說法):已讀,無 finding。

最高等級 major,共 2 條 blocking(第 5 條的 vault-free 衝突、`INV_TAG_RE` 漏列),另有 4 條 minor(non-blocking)。
