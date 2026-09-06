severity: major
- [major] `_LumosParser.error()` 把「旗標值不合法」誤判成「子命令不存在」，吃掉原本指出旗標名稱與合法值域的關鍵資訊。
  引句:「m = re.search(r"invalid choice: '([^']+)'", message or "")」
  位置:`scripts/lumos:19000`
  blocking:是
  why: 實跑凍結版 `lumos canary record --severity majo`，預期保留 `argument --severity: invalid choice` 並列合法 severity；實際印「沒有 majo 這個指令」，且只導向 `lumos canary record --help`。原因是所有 argparse `invalid choice` 都命中同一 regex，不只子命令錯字。缺必填、整數型別錯、互斥錯仍保留原始 message；但 choices 型旗標是確定的錯誤退化。新增測試只覆蓋 `doctorr` 與 `loop zzz`，未覆蓋旗標 choices。

- [clean] 多層子命令的 `self.prog` 可直接貼上執行。
  why: 實跑 `lumos loop zzz`、`lumos guard zzz`、`lumos canary zzz`，分別正確印出 `lumos loop --help`、`lumos guard --help`、`lumos canary --help`，退出碼皆為 2。

- [clean] 其餘 argparse 錯法沒有漏掉核心錯誤內容。
  why: 實跑裸 `lumos`、`context` 缺 note、`map foo --depth nope`、`impact --file a --diff b`、巢狀指令缺必填與未識別旗標；缺必填、型別錯與未識別參數文字仍在，互斥檢查仍由既有 dispatcher 清楚擋下。唯一確認退化的是上述非子命令的 `invalid choice`。

- [clean] `_node_not_found()` 在目前 428 篇規模成本很低，並呈線性成長。
  why: 用凍結版函式對合成 `env.notes` 各跑三次：428 篇約 4.19–5.13ms、4,280 篇約 41.6–41.8ms、42,800 篇約 422–424ms。消費端大十倍仍約 42ms；大百倍約 0.42 秒，沒有目前規模的阻擋問題。

- [clean] `_node_not_found()` 的廣泛 `try/except Exception` 未找到會吞掉主操作錯誤的現役路徑。
  why: 例外區只包候選名單推導；節點查找 `env.find()` 已在呼叫前完成。候選計算故障時會降級成「沒有名字接近＋lumos search」，仍回 rc2。它會隱藏候選功能自身的程式錯，但不會把讀寫命令誤報成功或吞掉已找到節點後的業務錯誤。

- [clean] 全 repo 現役呼叫端未發現依賴 `impact --node` 無 vault 回 rc2，或依賴 `impact --diff` 無 vault回 rc0。
  why: 排除凍結治理證物與文件後搜尋執行入口；現役 shell hook 對 `impact --diff` 均以 `|| true` 隔離，Claude hook 只解析成功 JSON。既有介面文件已宣告 impact 的 vault-missing rc3。未找到針對舊 rc2/rc0 分支的呼叫端。

- [clean] `impact --diff` 的新前置檢查沒有新增 `--repo` 或上層 vault 的誤擋。
  why: 檢查發生在 git repo root 解析及 `git diff` 成功之後，並以 `_vault_in(repo_root)` 判斷。`--repo` 指向另一個含 vault 的 repo 可正常命中。未帶 `--repo` 時原流程本來就先鎖定最近的 git root，逐檔呼叫也把該 root 明確傳入，因此「vault 只在 git root 上層」原先同樣找不到，不是本 diff 新增的退化。

- [clean] 至少兩支新增測試具備殺傷力，還原修法後確實翻紅。
  why: 直接以舊 blob `00a3929` 重跑兩支測試的核心現場：`doctorr` 恢復 argparse 的完整 66 指令牆，違反近名與輸出長度斷言；`contracts lumos-cli-rea介` 恢復「決策沒地方掛」且沒有候選，違反候選與用詞斷言。兩支皆確實走到被修改分支，不是現場不可達。
