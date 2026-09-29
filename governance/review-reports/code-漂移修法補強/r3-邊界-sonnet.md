severity: minor

## F1 證據頁「完整清單」指令遇到含引號、反斜線、tab 的目錄名會少列
severity: minor
blocking: 否
引句:「git --literal-pathspecs -c core.quotePath=off show --name-only --diff-filter=AR --format= {sha} -- {rr}/」
file: `scripts/lumos:28030`(_drift_c4_more_cmd)、`scripts/lumos:27990`(_drift_c4_same_commit 用 -z 讀,不受 quote 影響)
1. 輸入:同一提交加進 8 個卷證目錄,名稱為 `a b`、`q"uote`、`back\slash`、`中文計劃`、`tab<TAB>here`、`plain`、`x<U+202E>y`、NFD 的 é(在臨時 git repo 用 `_drift_c4_same_commit` 與 `_drift_c4_more_cmd` 實跑)。
2. 證據頁側(-z、不加引號)列出 8 個,頁面印「共 8 個」;照貼指令(沒有 -z)輸出只有 5 行:含 `"`、`\`、tab 的三個被 git 加上 C 風格引號,awk 切出的第 3 段是 `q\"uote"` 之類,`[ -d ]` 判不到而被靜默丟掉。--core.quotePath=off 只管非 ASCII,不管這三種字元。
3. 壞在哪:指令宣稱「同提交的完整清單(共 N 個)」,實際少於 N,且無任何提示。第 2 輪為了「指令與證據頁同一套定義」改寫這段,沒有把 -z 一起帶過來(只修了報上來的非 ASCII 那個輸入)。實務上這類目錄名罕見,故 minor。

## F2 磁碟上只改了大小寫的卷證目錄,同提交來源整個對不上
severity: minor
blocking: 否
引句:「out += [x for x in (by_key.get(nfc(d), []) if d else []) if x not in out]」
file: `scripts/lumos:27997`(_drift_c4_same_commit)
1. 輸入:提交時 git 裡是 `governance/review-reports/Code-Foo/r.md`,之後在 macOS(core.ignorecase=true)把磁碟目錄改名成 `code-foo`,git 索引仍記 `Code-Foo`。
2. 實跑:`_drift_c4_existing` 回 `{'code-foo'}`,`_drift_c4_same_commit(d, sha, {'code-foo'})` 回 `[]`(同提交一個都沒對到),證據頁該目錄只剩計劃名比對那一路,計劃名對不上就整個消失。
3. 壞在哪:NFC 鍵只處理正規化差異,沒處理不分大小寫檔案系統上「磁碟名與 git 名只差大小寫」;跟 NFD 同一族的輸入,r2 只修了 NFD。非 blocking:需要有人手動改過卷證目錄大小寫。

## 已實跑、未發現問題的邊界(供對照)
- 刪除守衛兩態(`_delguard_vendored_skips`,用臨時 git repo 逐案跑):無 HEAD(首個提交)→ 刪除集空、新增集含工具檔;清單只在 HEAD、暫存區把它 rm --cached / 壞 JSON / 缺 files 欄 / files 是清單 → 兩份皆空(保守多掃);lumos update(工具檔與清單同時更新)→ 兩邊都跳;專案改過工具檔 → 都不跳;暫存區原樣、工作目錄被改 → 仍照暫存區跳(H);git mv 走並改內容(K2)、git rm 整支(K3)→ 刪除行跳、新增行不跳,正確;工具檔在暫存區變 symlink、路徑是目錄 → 不算原封不動;diff_text 只含 `scripts/lumosX` 這種相似名 → 不誤觸發。CRLF 工作目錄但 HEAD/暫存區內容變更 → 不跳,正確。
- 清單帶 BOM 時 `_json_at_ref` 回 None,兩態都不跳(保守方向,非本輪引入,不報)。
- 佔位字變體:全形/半形混用的兩邊括號(`＜卷證>`、`<卷證＞`)、括號內多空白、tab、NBSP、全形空白、換行、`SHA`/`Sha`、`＜ sha ＞` 都擋;`<SHA-1>`、`<git-sha>`、`<sha256>`、`<卷 證>`、單邊括號照收,符合第 3 項修正的意圖。全形字母(`＜Ｓｈａ＞`)與括號內夾零寬字元不擋,佔位字是 ASCII 且需刻意才會打出,不報。
- 格式字元:U+202E 印成 `‮`;控制字元被 `_esc_clean` 換空格;NFD/NFC 同一目錄只印一行(磁碟名)。

## 圖譜鏡頭逐條判定
- Systems/存量漂移守衛.md:c4 證據頁與 drift fix 行為的家;本 diff 修的是這份的實作,F1/F2 只是證據頁輸出瑕疵,不影響「c4 只列證據不寫檔」的行為。
- Systems/bound-tests-gate.md(INVARIANT 綁測試逐支真跑):不影響,本 diff 未動閘的邏輯;新增/改動的測試需在綁定範圍內跑綠,我未跑全套。
- Systems/guard-kill.md、授權與歸屬.md、lumos-cli-read.md、lumos-cli-lifecycle.md、design-loop.md、測試假綠形態.md:本 diff 未碰對應函式(rc 優先序、授權檔白名單、search 濾網、re-inject、處置閘)。授權與歸屬的「LICENSE 不得入 _VENDORED_TOOLKIT」:`_delguard_vendored_skips` 只讀 `_VENDORED_ALL`,不改清單內容,不影響。

最高等級:minor
