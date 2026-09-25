severity: major

## F1 warn/off 無法避免既有 lint 規則首次升成全圖硬擋

severity: major
blocking: yes
引句:「開關只管這次新增的規則;lint 原本就有的錯誤等級規則照舊擋、不受開關影響。」
現況提交前只對 staged 筆記逐檔執行完整 lint；doctor 的 L 段全圖只讀 `n.lint` 解析指紋。照 spec 擴充 L 段後，既有的 type、summary、aliases、決策結構、合約等 lint error 會首次對全圖硬擋，且依引句不受 warn/off 控制。消費專案若有一篇未碰到的舊筆記缺 aliases，原本可推，更新工具後即使設定 `note_lint.gate=warn` 或 `off`，pre-push 與 CI 仍會被該舊筆記擋下；這與預設 warn、防止未量測消費專案被卡住及回退段宣稱不符。file: `scripts/hooks/pre-commit:91`、`scripts/hooks/pre-commit:97`、`scripts/hooks/pre-commit:103`、`scripts/lumos:1196`、`scripts/lumos:1199`、`scripts/lumos:4802`、`scripts/lumos:4840`、`scripts/lumos:4851`、`scripts/lumos:4914`

## F2 about_code 寫入原語仍會寫入新 lint 明定禁止的筆記路徑

severity: major
blocking: yes
引句:「`about_code`:每一項要是磁碟上存在的檔,而且不在圖譜資料夾裡(筆記不是程式檔)。寫成單一字串而不是清單的,當成只有一項。」
spec 宣稱 about_code 的存在判法沿用寫入指令，但現有 `_about_code_path` 只驗 repo 內、存在且為檔案，沒有排除圖譜資料夾；`append about_code` 與 `new --code` 都直接沿用它。實作後執行 `lumos append Systems/A about_code docs/<slug>-knowledge/Systems/B.md` 仍會成功寫檔，隨後同一值才被新 lint 判錯，官方安全寫入原語會製造自己禁止的狀態。file: `scripts/lumos:13652`、`scripts/lumos:13663`、`scripts/lumos:13669`、`scripts/lumos:13681`、`scripts/lumos:13689`、`scripts/lumos:13693`、`scripts/lumos:15043`、`scripts/lumos:15056`

## 圖譜節點判定

- `Systems/lumos-cli-write`:會受影響；S11 已要求 on 模式拒寫且原檔不變，未破壞 atomic 寫入合約；F2 顯示 about_code 寫入端尚未納入同一語意規則。
- `Systems/lumos-cli-read`:會受 doctor/L 段擴充影響；其 search 排除 superseded 的既有合約不在本案控制流上，不受破壞。
- 凍結快照沒有附加其他合約／事故節點區塊。

## 實務隱患逐類

- 金流：無；只讀取並驗證筆記欄位，不進交易或計費路徑。
- 對外送出：無；lint、doctor、set 不發外部請求。
- 不可逆：無；設定可降級，寫入端要求 atomic 且 S11 明定拒寫時檔案不變。
- 守衛面：有；F1 會讓預設 warn／回退開關失去保護效果，F2 會讓官方寫入入口產生稍後才被守衛拒絕的狀態。

總結:最高 severity major，blocking 共 2 條。
