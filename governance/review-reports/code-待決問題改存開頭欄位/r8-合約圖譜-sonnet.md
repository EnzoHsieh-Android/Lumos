severity: major

審查範圍是 5242975c 相對 ff6565ec 的修補。我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-合約圖譜-sonnet/` 建了修前、修後兩份副本，跑了行為重現和 23 個故障變體。

整體上，三條單一規則在核心行為上成立。清單外的題目形狀（頂格整題、決策底下的流式題）現在會被擋。看不見字元的放行與阻擋、決策換行的拒寫，都有行為證據。但有一處合約被打破：guard 子指令的擋下訊息沒有清洗控制字元。另有幾處文件說得比程式多，以及幾道守衛沒有測試釘住。

1. 丙規則「只由 main 最外層接、先 `_esc_clean` 再印」不成立，guard 子指令會印出原始 ESC
severity: major
blocking: 是
引句:「各分派既有 try 仍只接自己的其他錯誤，非此信號的程式錯誤不吞」
- 佐證 file: `scripts/lumos:16840`、`scripts/lumos:16801`、`scripts/lumos:16515`。`WriteBlocked` 同時是 `ValueError` 和 `RuntimeError`，所以全檔約 25 處「`except (ValueError, RuntimeError) as ex: print(f"擋下:{ex}")`」都會先接住它，印出時沒有清洗，也沒有回到 `main` 最外層。
- 這輪新訊息帶了檔名（`file: scripts/lumos:9075`），所以檔名裡的控制字元會直接印到終端。
- 最小重現（`/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-合約圖譜-sonnet/t3.py` 同一套 `mk()`/`run()`）：
  1. 建一個 vault，放 `Systems/Real.md`，裡面有一條 `KEY:★INVARIANT★ 甲合約 [test:BoundTest]`。
  2. 建符號連結 `Systems/Sym\x1b[31mRED.md` 指向 `Real.md`。
  3. 跑 `lumos guard bind Systems/<該名> 甲合約 OtherTest`，另外 `guard audit`、`guard kill-add` 也各跑一次。
- 修前 stderr 是乾淨的舊訊息（不含檔名）。修後三支指令的 stderr 都含原始 `\x1b[31m`。同一個檔名跑 `set`、`summary-line`、`signoff` 則已清洗。
- 歸因:有證據的修復回歸。
- 查證命令：同一支腳本分別指向 `before/scripts/lumos` 和 `after/scripts/lumos`。修前結果是 `guard bind 2 clean`，修後是 `guard bind 2 RAWESC`。
- ⚠ 要攻擊得先讓使用者的 repo 帶這種檔名，實際風險不高。但它直接違反第三條規則和 `Systems/lumos-cli-write.md` 的那句保證。

2. 文件說「帶註解的 block scalar header 不算」，程式其實算
severity: minor
blocking: 否
引句:「帶註解不算 block scalar，內容仍逐行套鍵名規則」
- 佐證 file: `scripts/lumos:7262`。`_pq_block_key_col` 先用 `_pq_unquoted_value` 去掉 ` #` 註解再比對 `BLOCK_SCALAR_HEADERS`，所以 `x: | # c` 會被當成 block scalar。
- 條款 S2 的「其他 header 不視為 block scalar」同樣說錯：實作是「`|`、`|-`、`>`、`>-` 加註解仍算」。這是文件寫錯，程式的行為才符合 YAML。
- 最小重現：front matter 是 `pending_questions` 一題，後面接 `x: | # c` 和一行 `  text: a`。修前、修後的 `pq_parse` 錯誤都是 0 筆。而 `x: |+` 加同樣內容，修後才會擋，修前不擋。
- 歸因:有證據的修復回歸。行為兩版相同，錯的是 r8 新寫的文件句。

3. 清單外規則對連續 `- ` 是平方級，修前沒有這個成本
severity: minor
blocking: 否
引句:「while text.startswith("- "):」
- 佐證 file: `scripts/lumos:7205`、`scripts/lumos:7215`、`scripts/lumos:7237`。每剝一個 `- ` 就複製整串字串，而且同一行被好幾個函式各剝一次。
- 重現：`pq_parse` 餵一行 `x:\n  ` 加 N 個 `- ` 再加 `a`。N=5 萬時修後 1.09 秒，N=10 萬 2.36 秒，N=20 萬 6.39 秒；修前三種都是 0.0 秒。
- `t_qfm_linear_cost` 只測了長空白，沒測這種形狀。
- 歸因:有證據的修復回歸。
- ⚠ 要有幾百 KB 的惡意單行才會觸發。

4. 「emoji 只認 Extended_Pictographic」說過頭，碼位表是整段 1F000–1FAFF
severity: minor
blocking: 否
引句:「只認 Unicode 16 Extended_Pictographic 碼位與膚色修飾(不用 Unicode 類別 So」
- 佐證 file: `scripts/lumos:6953`。程式碼註解自己寫了「補充平面取 1F000-1FAFF 整段」。這段包含 U+1F130 方框字母、U+1F1E6 區域指示符等非 EP 碼位。
- 重現：`🄰‍🄱` 和 `🇦‍🇧`（中間是 ZWJ）在 `_pq_scalar_char_problem` 都回 `None`，被當成 emoji 放行。
- 實際容量仍被 16 個總量上限和第 5 點的規則限住，所以是文件過度宣稱，不是新的洞。
- 歸因:有證據的修復回歸（r8 新表）。
- ⚠ 我手上沒有 emoji-data 原檔，無法逐碼位列出差集。

5. 新測試有三道守衛沒被釘住，其中一條由別的守衛代打
severity: minor
blocking: 否
引句:「check("④ 合法位置的看不見選擇仍受 min(8,max(2,可見字//4)) 總量上限",」
- 佐證 file: `scripts/test_lumos.py:57318`、`scripts/test_lumos.py:57314`。
- 變體實測，「整套 qfm 測試」指 `-k qfm`：
  - 把 `_PQ_INVISIBLE_MAX` 從 8 改成 800：整套 qfm 全綠。測試只涵蓋下限 2 和除數 4，上限 8 沒人釘。
  - 把 emoji ZWJ 的「兩側都要是 emoji」（`_pq_zwj_ok`）改成「任一側」：整套 qfm 全綠。我實測 `a😀‍b` 修後會擋，變體卻會放行，測試沒有單側 emoji 的案例。
  - 拿掉 `_pq_dicp_position_ok` 裡的相鄰可忽略字元檢查：整套 qfm 全綠。測試 ③ 的 `❤️‍‌字` 其實是被 ZWNJ 的文字系統規則先擋掉，不是相鄰規則。我檢查後認為這道相鄰檢查幾乎被其他規則涵蓋，是冗餘守衛，不是漏洞。
- 其餘變體都翻紅：清單外鍵名、flow、anchor/tag、block scalar、引號鍵、NFKC、行首 tab、文字系統、emoji 碼位表、總量 16、FE0F、軟連字號、蒙古變體、帳 `truncate`、硬連結、符號連結、`_esc_clean`。
- 歸因:有證據的修復回歸（新測試的缺口）。

6. `decision-add` 的自由文字只擋換行，ESC 與 tab 照寫、照回顯
severity: minor
blocking: 否
引句:「decision 自由文字含任一換行類字元一律拒寫」
- 佐證 file: `scripts/lumos:39824` 附近的寫入原語沒有字元類別檢查。
- 重現：`decision-add ... '採甲\x1b[2Jx\ty' --context 'a\x1b[31mb'` 回 0，筆記裡留著原始 ESC，成功訊息的 stdout 也印出原始 ESC。修前行為相同。
- 換行類字元（`\n \r \x1c \u2028` 等）在 `decision-add`、`decision-amend`、`decision-supersede` 三支修後確實全拒，修前 `\r \x1c \u2028` 會寫進去。
- 歸因:有證據的原有漏查。

7. 舊測試改動大致誠實，但有兩處變弱
severity: minor
blocking: 否
引句:「check("⑥ docs 含 pending_questions 的現存篇仍可讀",」
- 佐證 file: `scripts/test_lumos.py:57092` 起的 `t_qfm_r6_tool_flow_and_repo_compatibility`。
- 原本拿修前版 `pq_parse` 和新版逐篇對拍題號（所有 docs 與有 `pending_questions` 的篇都對）。現在只剩「沒有錯誤」，沒有檢查新讀法讀出的題號和舊版一致。
- `_QFM_BAD` 裡「頂格清單項」「合併衝突標記」的預期字串從「頂格」改成「讀不懂這行」。這兩行現在落在清單範圍內，會被 2/4 格文法擋，所以改法合理，只是訊息少了「頂格」這個線索。
- 其餘改動都可接受：
  - DICP 表測試改成測試端獨立抄錄。我用 Unicode 16 的定義獨立算過，4174 碼位與產品表差集為空，這是強化。
  - `|2-` 的正例改成 `|-`，與新規則一致。
  - 符號連結讀取測試翻轉，與丙規則一致。
  - 移除 `decision-reindex` 預編號，與「決策沒編號不再是錯」一致。
  - `t_fix_check_*` 的改動只是把分號拆成兩行，行為不變。
- 歸因:有證據的修復回歸。

8. 計劃說符號與硬連結「只在真正寫入前」拒絕，但 `drift fix` 的 `--dry-run` 和 c4 也會先拒
severity: minor
blocking: 否
引句:「符號連結與硬連結(`nlink>1`)只在真正寫入前由 `_write_refusal_reason` 統一拒絕」
- 佐證 file: `scripts/lumos:39824`。`_drift_fix_load` 在 `dry_run` 判斷之前就呼叫 `_write_refusal_reason`。
- 重現：照 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-合約圖譜-sonnet/t7.py` 建好 `Verification/G.md`，再對它建硬連結 `H.md`，然後跑 `drift fix ... --dry-run` 和 `--kind c4`，兩者都回 2。修前也是回 2，訊息不同。
- 歸因:有證據的原有漏查。行為沒變，是文件措辭過度。

## 三問

**① 原問題的修復效果有何行為證據？**
- 甲：清單外頂格整題（`id: Q2` 加 `text:` 等）和決策底下的流式題（`{id: Q2, text: …}`），修前 `pq_parse` 回 0 錯，整題靜默消失；修後都擋。引號鍵、全形鍵、anchor、tag、雙層清單，修前已擋，修後仍擋。
- 乙：以下看不見字元的輸入，修前都放行、修後被擋：
  - 拉丁、框線、度數的 ZWJ。
  - 一般標點後的 FE0F。
  - 30 個 emoji 疊 ZWJ，以及 20 個 emoji 疊 FE0F。
  - `﷽‍﷽`。
- 修前誤擋、修後放行的有波斯與馬拉雅拉姆詞尾、`‼️`、蒙古變體；家庭 emoji、愛心、鍵帽修前後都放行。
- 丙：
  - 決策的 `\r \x1c \u2028`，修前三支決策指令（add、amend、supersede）會寫入，修後全部回 2。
  - `set` 對硬連結筆記，修前回 0，修後回 2。
  - 帳半行失敗截回原長度、帳檔是符號連結拒絕，測試都有翻紅證據（拿掉 `truncate` 或符號連結檢查都會紅）。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立？**
- 正常路徑成立：
  - 工具正常流程寫出的筆記（`append aliases 'stage: 架構'`、決策、`question-add`）都會正確加引號，讀得懂。
  - repo 的 docs 都能讀懂。
  - `r8` 四個測試和 `qfm` 全套（我跑的變體底線）都綠。
- 錯誤路徑：除第 1 點外，`set`、`summary-line`、`signoff`、`self-audit`、`decision-add` 的擋下訊息都已清洗。
- 相鄰路徑：
  - 硬連結筆記對所有 `atomic_write_verify` 寫入者變成拒寫。修前 `set` 可寫，是行為變更。依丙規則是預期的，但計劃〈資料相容〉沒有提。
  - `guard bind` 的唯讀 no-op 經符號連結仍可完成。
  - 讀取符號連結照常。

**③ 新發現的同一案例在修前、修後各是什麼結果？**
- 第 1 點：修前 stderr 乾淨，修後 `guard bind`、`guard audit`、`guard kill-add` 印出原始 ESC（修復回歸）。
- 第 2 點：兩版 `x: | # c` 都 0 錯，只有文件說反。
- 第 3 點：修前 0.0 秒，修後 N=20 萬 6.39 秒。
- 第 6 點與第 8 點：兩版行為相同（原有漏查）。

總結：三條規則的核心行為成立，但 guard 子指令的擋下訊息沒有清洗控制字元，違反丙規則，需要修；其餘是文件過度宣稱、一個平方級退化和三道未被釘住的守衛。
