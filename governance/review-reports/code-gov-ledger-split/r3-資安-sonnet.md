severity: minor

## 類1 不可信輸入流到危險操作
已看。本機帳的寫入端(_gate_event、_append_governance_log、_usage_log)都先擋 is_symlink 再寫;_ensure_docs_gitignore 是追加寫、擋捷徑/硬連結、新建用 O_EXCL;subprocess 用 list 參數、檔名來自常數(_LOCAL_LOG_IGNORE_LINES),沒有 shell 插值。反序列化只有 json 逐行解析,壞行跳過。僅有 F1 的讀端捷徑一條推論。

## 類2 判定繞過
已看,無。判定類讀者(code-loop、fix-check、design-loop)只讀版控帳,本機帳不進判定;_GOV_LOCAL_PAIRS 是白名單、要求 hard 恰為 False,且名單內沒有判定類的閘。兩本本機帳加進 _BOOKKEEPING_FILES 後,惡意作者強制提交這兩個檔,只會被當純簿記增量豁免,但簿記檔在該判定路徑上本來就不比模式、內容是 JSONL 資料而非可執行碼,和既有的 .governance-log.jsonl 同信任等級,沒有新增偽造留痕的路(留痕讀的是版控帳)。

## 類3 密鑰與個資
有一條推論,見 F1。其餘已看,無:寫入內容只有閘名、種類、備註、節點名,不含密鑰。

## 類4 加密與傳輸
已看,無。沒有網路或加密相關改動。

## 類5 執行邊界
已看。鎖檔仍放既有的家目錄快取(_vault_lock_where),不在 repo 內;O_EXCL 建檔加 is_symlink 檢查,懸空捷徑下 O_EXCL 也會失敗;hook 與 CI 的呼叫沒有新增 shell 插值。check-ignore / ls-files 的參數是常數檔名。

## 類6 行動端
已看,無。

## 新依賴
已看,無(只用標準庫)。

## F1 讀端跟捷徑讀本機帳(推論)
severity: minor
blocking: 否
引句:「        if not p.is_file():      # 跟捷徑讀,但只讀一般檔案(特殊裝置檔、管線讀不到底;代碼審 code-gov-ledger-split r2 併發席)」
file: `scripts/lumos:8271`(以 diff 為準,cmd_gov 的 load)
攻擊路徑(推論,講不出具體拿到什麼):
1. 誰:惡意 repo 作者。
2. 入口:提交一個名為 docs/.governance-local.jsonl 的捷徑(強制提交被忽略檔),指向受害者家目錄下某個每行是 JSON 物件的檔。
3. 送什麼:受害者在 clone 後跑 lumos gov / doctor。
4. 拿到什麼:只有每行是 JSON 物件、且通過 _gov_event_types_ok 的行會被讀進統計;非 JSON 的密鑰檔(私鑰、token)一行都不會進輸出,輸出也只在本機終端、不寫回 repo。寫入端已擋捷徑,故沒有內容被寫進 repo 的路。講不出具體可外洩的檔,所以只標推論。

所有類別看完,未見能被利用的洞,僅一條推論性的輕微讀端疑慮。
