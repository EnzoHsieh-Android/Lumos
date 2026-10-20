severity: minor

被審版本是 474346765ea9546241fed3dbfd95a59d5d09e4ad。我讀了修補差異全份,再用 `git show` 取該版本的 `scripts/lumos`,以及快照裡的 `ci.yml` 與 `scripts/hooks/pre-push`。實驗放在 `/tmp/lumos-seat-work/code-安全證據閘與資安格子/資安-sonnet/`,已刪光。下面兩條新發現都不是修補造成的。

## 發現

### 1. `security list --questions` 把筆記裡的描述原樣塞進題句,沒有包資料框
severity: minor
blocking: 否

- 引句:「q = tbl[c["category"]]["template"].replace("{角色}", role).replace("{入口}", sname).replace("{資產}", aname)」
- 攻擊路徑:
  - 誰:陌生 repo 的作者。
  - 從哪:Systems 筆記 `lumos-security-v1` 圍欄裡 `inventory` 的 `assets`、`actors`、`surfaces` 的 `description`。
  - 送什麼:一段像指示的文字,例如「忽略以上規則…改執行…」。登記時沒有長度上限,`_secinv_is_text` 只驗非空白與代理字元。
  - 拿到什麼:使用者或 AI 跑 `lumos security list --questions` 時,這段字混在工具自己的題句裡,沒有任何「登記內容是資料」的框,AI 容易當成工具的指示。
- 重現:我造了一個 vault,把資產描述設成上述指示字樣。`security list --questions` 把它逐字代入多題的 `{資產}`,例如 `[cell:P/A1/data-exposure] … 會不會帶出 忽略以上規則。…`。
- 同一個報告的其他區段(`_secinv_rec_lines`、`_secinv_framed`)都有框;只有這支 `_seccell_cmd_questions` 沒有。控制字元已被 `_secinv_show` 跳脫,所以只是文字層的提示注入。
- 它是縱深防禦類,沒有可直接利用的執行或外洩,所以標 minor。
- 歸因:有證據的原有漏查。修補差異沒碰這個函式;修前 7655a12d 的同一行 `q = tbl[...]` 已存在(`git show 7655a12d:scripts/lumos | grep -c` 得 1)。

### 2. `security approvals payload` 把要簽的 JSON 原樣印給人看,雙向覆寫與行段分隔字元不跳脫
severity: minor
blocking: 否

- 引句:「sys.stdout.write(raw.decode("utf-8") + "\n")」
- 攻擊路徑:
  - 誰:能影響筆記的人。
  - 從哪:護欄的 `exception.compensating` 等自由文字,`_secapr_c_exception` 會把整個 `exception` 放進 payload。
  - 送什麼:`compensating` 內夾 U+202E、U+2028、U+0085 這類字,`_secev_canon` 用 `ensure_ascii=False`,JSON 只會跳脫 0x20 以下的字元。
  - 拿到什麼:使用者在終端機看到的 payload 跟實際簽的位元組不同,可以偽裝成別的內容讓人簽下去。
- 簽章必須對確切位元組,所以 `--out` 存檔不能改。但 stdout 這份是給人看的,可以另外跳脫,例如印 `_json_text_escaped` 版。
- 這是使用者簽章前的視覺欺騙,要先有人在筆記裡塞字、再有人沒細看就簽,所以只標 minor。
- 歸因:有證據的原有漏查。修補只動了這支函式後面的「接下來」指引(改成 `_secinv_say`),沒動這行。

## 已看,無(攻擊者角度再試的結果)

- **控制字元與終端跳脫**:
  - 擋下訊息、`security evidence` 文字輸出、`security list` 文字輸出、核可鏈檢視、`--security-only --json` 現在都整行過 `_secinv_show` 或 `_json_text_escaped`。
  - 實測 ESC、U+202E、U+2028、U+200B、U+E0041 都被跳脫成 `\uXXXX`,`_secinv_lines_text` 對 `\n` 夾帶的行也一併跳脫。
  - hook 的 `printf '%s\n' "$_sec_out"` 只轉印已跳脫的輸出。
  - 我只對上列路徑逐一核對 `print(` 是否用了 `_secinv_show`,漏掉的只有上面第 2 條。
- **給人照貼的指令路徑**:
  - 路徑現在經 `shlex.quote` 再過 `_secinv_show`。路徑含 ESC、換行、不可見字元時,貼上去會變成找不到檔,會安全失敗。
  - `$`、反引號、引號都被 `shlex.quote` 處理。
- **符號連結寫入**:
  - 我直接載入 `_secev_append_target` 實測四種情形:`.lumos` 是指到 repo 外的連結、`.lumos/security-approvals.jsonl` 是懸空連結、`docs` 是連結、正常路徑。
  - 前三種都回 `(None, 擋下原因)`,第四種正常放行。
  - `security-approval-add` 在讀鏈之前也先查一次,`security-backing` 在讀寫之前查。
- **主線設定讀不到被當成沒登記**:
  - `_secev_mainline_override` 把 git 失敗、逾時、檔過大都改成 `mainline_unknown`。
  - 預檢的主線那側在認不出主線時改看本機所有候選 ref,任一有痕跡或判不了就走完整判定。
  - 沒查到的邊角:`git init` 加 `remote add`、完全沒 fetch 就推時,本機沒有任何追蹤 ref,仍會判成沒登記。這需要刻意的環境,依派工詞歸範圍外,我沒重現。
- **故障證據收據**:
  - 新增的收據指紋比對(`receipt_source_changed`)會逐一核對 baseline 每個快照 sha 與被推提交樹裡同一路徑的檔,路徑對不到 repo 或對不上都不給過。
  - 關聯性檢查(`fault_unrelated`)要求被改壞的實作檔在這一項的綁定或家節點 `about_code` 裡。
  - 要偽造收據本身屬刻意多步偽造,範圍外。
- **工具清單與最低種類**:
  - `_secev_min_kinds` 在 `tools=None` 時不做替代,照原最低種類判。
  - 推送版清單超過單檔上限時另有警告並走原最低種類。
- **CI 與 hook**:
  - 分支名經 `env` 傳入,有加引號。
  - `security_tag` 只在 push tag 時跑,沒有執行 PR 提供的程式。
  - hook 的 `GRAPHCTL="$REPO_ROOT/scripts/lumos"` 是既有設計,不是這輪新增。
  - 刪 ref(`local_sha` 全零)在兩處迴圈都先 `continue`。
- 密鑰與信箱:diff 的程式、範本與公開文件都沒有新寫入的密鑰或信箱。
- 安裝腳本下載來源與網址被環境變數覆蓋:這份 diff 沒碰安裝腳本,已看,無。
- 併發類檢核題:判範圍外,標誤報。

## 三問的回答

- 原問題的修復效果:
  - 各出口整行跳脫與符號連結守衛,我用上面的實測與修補差異的程式讀法證實有效。
  - 我沒有同時跑修前與修後做對照,所以「修前確實有洞」這半段沒驗。
- 修補處的正常、錯誤與相鄰呼叫路徑:
  - 符號連結守衛的正常路徑(建新目錄、追加)實測仍成立。
  - 錯誤路徑都有明確原因字串並回 2。
  - 非互動終端的提示因多一層引號,貼上去路徑含特殊字元時會變成不同的檔名,屬安全失敗。
- 新發現的同一案例修前修後:兩條都是修前就存在、修後未變,所以不是修補造成。

最嚴重 severity:minor,blocking 共 0 條
