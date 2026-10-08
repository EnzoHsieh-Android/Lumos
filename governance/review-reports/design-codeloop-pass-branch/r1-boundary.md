severity: major

## Finding 1：碰撞修補漏掉先執行的 dispositions 讀側

severity: major  
blocking: 是  
引句:「含 `/` 與 `__` 的兩個不同分支也要分清。」

`a/b` 與 `a__b` 會映射成同一個 marker 檔名。設計只替 pass marker 增加分支身分核對，但 `code-loop check` 會先讀 dispositions；該讀側雖然 marker 已存原始分支，卻未核對它。若兩個分支指向同一提交，另一分支的表態可被直接借用，違反「不同分支不得共用」的核心限制。

file: `scripts/lumos:34378`  
file: `scripts/lumos:35333`  
file: `scripts/lumos:35355`  
file: `scripts/lumos:35529`  
file: `docs/lumos-toolchain-knowledge/Issues/code-loop-pass不能指定分支.md:18`

修正設計應一併要求 `_codeloop_read_dispositions` 驗證 `branch`，不符時按完整分支名退讀治理帳；回歸測試須在有適用表態題時覆蓋 `a/b`、`a__b` 同提交互不借用。

## Finding 2：pre-push 仍指示執行會重現原問題的命令

severity: major  
blocking: 是  
引句:「準備推 `HEAD:main` 時，`code-loop pass` 只記在 `feature`；推送前按目的地 `main` 查，會要求重記審查。」

pre-push 已知道目的分支 `_rbranch`，也用它執行 check；但擋下後仍提示執行不帶 `--branch` 的 `code-loop pass`。使用者照做會再次把留痕記到 checkout 分支，下一次推送仍被同一原因擋下。CLI 的過期留痕訊息也保留相同錯誤指令。

此外，訊息仍把 `skip` 列為逃生路，但設計明定維持 skip 現況，因此 `HEAD:main` 情境下 skip 仍無法綁定目的分支。

file: `scripts/hooks/pre-push:398`  
file: `scripts/hooks/pre-push:405`  
file: `scripts/hooks/pre-push:425`  
file: `scripts/lumos:35410`  
file: `scripts/lumos:36036`

驗收應加入：擋下訊息提供 `pass --branch <目的短名>`；對 skip 則明確決定支援目的分支，或停止在此情境宣稱它是可行逃生路。

## Finding 3：舊 marker 的碰撞判準只涵蓋 `/` 與 `__`

severity: major  
blocking: 是  
引句:「舊 marker 沒有分支欄且請求名含 `/` 或 `__` 時也退讀治理帳，不能把檔名當身分。」

這個判準假設碰撞只來自 `/ → __`。在大小寫不敏感或 Unicode 正規化的檔案系統上，`Release` 與 `release` 等 Git 認可的不同短分支名也可能落到同一 marker 路徑；兩者都不含 `/` 或 `__`。舊 marker 又沒有分支欄，設計會直接信任它，可能借用另一分支的 pass。

file: `scripts/lumos:34378`  
file: `scripts/lumos:34383`  
file: `scripts/lumos:34484`

安全做法是：缺少分支身分的舊 marker 一律視為無法證明歸屬，退讀按完整分支名篩選的治理帳；不要以字面字元猜測檔案系統是否存在別名碰撞。

## Finding 4：壞 marker 不會退讀已有的治理帳

severity: minor  
blocking: 否  
引句:「`_codeloop_read` 遇到 marker 名碰撞而內存分支不符時，退讀依完整分支名篩出的治理帳。」

設計只指定「分支不符」時退讀。現況中 marker 存在但 JSON 讀取失敗會直接回 `None`，而 pass marker 又以非原子 `write_text` 寫入；中斷或競爭寫入後，即使治理帳已有正確紀錄，check 仍會誤報無留痕。相鄰的 dispositions marker 已有原子寫入與壞檔退帳本的既有做法，可以直接沿用。

file: `scripts/lumos:34388`  
file: `scripts/lumos:34390`  
file: `scripts/lumos:34484`  
file: `scripts/lumos:35333`  
file: `scripts/lumos:35361`

## 審材

- `governance/review-reports/design-codeloop-pass-branch/r1-snapshot.md`
- SHA-256：`41c3f660ea703b68cca60f1ab3511189aad55252210aa5f8929caa13b246f8d2`，已核對吻合
- `docs/lumos-toolchain-knowledge/Issues/code-loop-pass不能指定分支.md`
- `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- `scripts/lumos`
- `scripts/hooks/pre-push`
- 試行生效脈絡：`Projects/代碼審修復穩定性試行_計劃.md`、`Verification/2026-10-04_代碼審改道生效驗證.md`
- 未讀其他席報告；未寫檔、未還原變更

## 風險類

- 守衛面與跨分支授權隔離
- 分支短名、detached HEAD 與非法／展開式名稱
- marker 命名碰撞與舊格式遷移
- dispositions／pass 讀側借用
- pre-push 修復指引正確性
- 本機 marker 與治理帳的一致性、原子寫入及故障退路