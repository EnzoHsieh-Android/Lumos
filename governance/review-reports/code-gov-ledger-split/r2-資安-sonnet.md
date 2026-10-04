severity: minor

## 類1 不可信輸入流到危險操作
已看。git 子程序參數(ls-files、check-ignore)的檔名來自常數,無注入;ts 欄經 fromisoformat 後只做比較。唯一寫路徑問題見 F1。

## 類2 判定繞過
已看,無。code-loop、fix-check、design-loop 不在 _GOV_LOCAL_PAIRS 白名單,且 _gov_routes_local 要求 hard 恰為 False,擋人事件仍進版控帳;CI 判代碼審留痕只讀版控帳。偽造或強制提交的本機帳只被 doctor 統計、度量提醒與 cmd_gov 讀,都是軟提醒,不放行推送。_BOOKKEEPING_FILES 加兩個本機帳名只豁免那兩個檔自己的內容變動,不豁免其他程式檔。

## 類3 密鑰與個資
已看。本機帳只存閘名、種類、節點路徑與 note,沒有新增密鑰。F2 是個資(本機檔內容)被複製進 repo 的推論路徑。

## 類4 加密與傳輸
已看,無。沒有網路或加密變動。

## 類5 執行邊界
已看。_write_lf 用 uuid 隨機暫存檔名加 O_EXCL 建檔,再 os.replace,不跟捷徑、名稱不可預測。.gitignore 本身是捷徑時換掉的是捷徑本身。docs/ 目錄本身是捷徑時仍會寫到 repo 外,但這與既有版控帳寫法同一類,不是本次新增。見 F1、F2。

## 類6 行動端
已看,無。

## 類7 新依賴
已看,無。

## F1 使用紀錄本機帳沒有捷徑防護
severity: minor
blocking: 否
引句:「p = _docs_ledger_path(env.vault.parent, USAGE_LOCAL_LOG_NAME)」
file: `/home/user/Lumos/scripts/lumos:16308`
攻擊路徑(四件):
- 誰:惡意 repo 的作者。
- 入口:被害者 clone 該 repo 後執行唯讀的 `lumos show` 或 `lumos context`。
- 送什麼:repo 內提交一個 `docs/.usage-local.jsonl` 捷徑,指向被害者家目錄下的某檔(例如 `~/.ssh/config`)。上一輪只在 _gate_event 與 _append_governance_log 擋了捷徑,_usage_log 漏了同樣的 is_symlink 檢查,所以 open(p, "a") 會跟著捷徑寫。
- 拿到什麼:往 repo 外任意被害者可寫檔追加一行 `{"ts":…,"node":…,"cmd":…}` JSON。內容受限(單行、json.dumps 跳脫換行,node 是被害者自己選的),只能弄壞設定檔,拿不到執行權。屬推論加實際缺口,影響低。

## F2 補忽略規則時捷徑形式的 docs/.gitignore 內容被複製成一般檔
severity: minor
blocking: 否
引句:「_write_lf(gi, (raw + chunk).decode("utf-8"))」
file: `/home/user/Lumos/scripts/lumos:17727`
攻擊路徑(四件,推論):
- 誰:惡意 repo 作者。
- 入口:被害者在該 repo 跑 `lumos init` 或 `lumos update`(走 _init_additive_setup → _ensure_docs_gitignore)。
- 送什麼:repo 內提交 `docs/.gitignore` 捷徑,指向被害者家目錄的 UTF-8 文字檔(例如 `~/.aws/credentials`)。
- 拿到什麼:gi.read_bytes() 讀的是捷徑目標內容,_write_lf 用 os.replace 把整份內容加上補的兩行寫成 repo 內的一般檔;被害者若接著 `git add docs/` 並推送,該檔內容進了 repo。需要被害者推到攻擊者可讀的遠端,且要猜對路徑,所以只標推論。

總結:這次改動沒有找到能讓代碼審留痕誤判或繞過放行推送的路,只有兩條需要特定前提的低影響寫入面缺口。
