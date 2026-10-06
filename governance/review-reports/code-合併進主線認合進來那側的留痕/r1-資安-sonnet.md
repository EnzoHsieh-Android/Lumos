severity: minor

## F1 合進來那側的紀錄不看分支名、不驗來源,手寫帳本行照樣放行(與直推同信任等級,非新增洞)
severity: minor
blocking: 否 — 帳本可手寫是既有信任模型,新路徑沒有放寬到比直推更容易;只是把「分支名要對」這道弱綁定拿掉了
攻擊路徑:誰=開發者或被注入的 AI agent;從哪裡=自己分支第二個母 p2 的 docs/.governance-log.jsonl;送什麼=一行手寫 gate=code-loop、kind=passed、branch 任意、head_sha=分支上含主線頂端的提交(其後只動簿記檔);拿到什麼=帶 evil.py 的未審分支用 --no-ff 合進主線,守衛放行。
實測(臨時 repo,主線 p1、分支 evil 含 evil.py 並合了主線、再加一行手寫 pass、branch=zzz,最後 --no-ff 合進 main):呼叫 _codeloop_merge_side 回 ((p1, p2), None),_codeloop_merge_side_lookup 回手寫那筆事件、None 錯誤。
同樣手寫在直推路徑(_codeloop_read_from_ledger 取 branch==目標分支那筆)也成立,所以本 diff 沒有新增能力;差別只是不再需要猜對分支名。建議:若要縮小,至少要求事件 branch 與合進來那側的分支同名,或事件需有 pass --note 產生的非手寫標記。
引句:「cands = [ev for ev in _codeloop_ledger_events(text, kinds) if ev["head_sha"] in window]」

## F2 力推改寫主線時起點條件形同認分岔點(推論)
severity: minor
blocking: 否 — 推論;需要存心繞過本機掛鉤並力推主線,專案已明文劃在後盾範圍外,且進主線的程式仍是被審過的
攻擊路徑:誰=有主線寫入權的開發者;從哪裡=力推 main;送什麼=第一母是舊主線提交 p1_old、第二母含 p1_old 且有紀錄的合併提交,遠端舊頂端本機找不到所以掛鉤把起點改寫成分岔點;拿到什麼=合併後主線丟掉 p1_old 之後的主線修補(被審的是 p1_old 之上的程式,不是未審程式)。程式註解自己承認這條路上起點條件形同認了分岔點。我沒有實測掛鉤改寫路徑,故標推論。
引句:「這條路上起點條件形同認了分岔點,安全性靠後面的祖先、只差簿記檔與紀錄要包含第一個母三條,不靠起點」

## F3 帳本內的 branch 字串原樣進 reason(縱深防禦)
severity: minor
blocking: 否 — 要先能寫帳本,而能寫帳本的人本來就能放行;只影響日誌乾淨度
攻擊路徑:誰=能改分支帳本的開發者;送什麼=branch 欄位含換行加 `::warning::` 之類 GitHub Actions 指令字或終端跳脫序列的事件;拿到什麼=放行時 reason 印進 CI log/推送輸出,可偽造工作流指令行或洗版(沒有未審程式進主線)。建議印前剝掉控制字元並截長。
引句:「合進來那一側的留痕({ev['kind']}@{ev['head_sha'][:8]},分支 {ev.get('branch')})」

## 逐類結論與查過沒繞法的項目
1. 不可信輸入進危險操作:已看,無洞。rec 只有落在 git rev-list 吐出的 window 集合內才進 git 參數列(精確字串比對,前綴撞名、以 - 開頭都進不來);marker_sha 必須等於 _lens_full_sha 解出的完整 sha;_lens_full_sha 用 --end-of-options。json.loads 包在 try、非 dict 丟棄。
   引句:「if (isinstance(ev, dict) and ev.get("gate") == "code-loop" and ev.get("kind") in kinds」
   順帶:既有路徑把帳本的 rec_sha 不經 --end-of-options 丟給 git merge-base(未改動),第一個 git 因未知選項回非 0 就走「找不到」,到不了 git diff,故不可利用。
2. 權限繞過(臨時 repo 與程式推演):
   - 假合併(未審分支擺第一個母):p1 必須等於推送範圍原始起點。引句:「if p1 != start:」
   - 退掉主線修補/改名藏刪檔:要求 p1 是 p2 祖先,且 p2→合併結果用 _codeloop_record_valid_ex(--no-renames、-z、--raw、簿記資料夾內程式檔判定)只差簿記。引句:「ok, why, _unsure = _codeloop_record_valid_ex(repo_root, p2, marker_sha」
   - 還原提交借主線舊紀錄:紀錄提交必須包含 p1。引句:「merge-base", "--is-ancestor", p1, rec」
   - 合併提交手寫帳本:帳本讀的是 p2 那棵樹,不讀合併結果。引句:「["show", f"{p2}:docs/.governance-log.jsonl"]」
   - range 終點不是目標:引句:「if start is None or end != marker_sha:」
   - 新分支首推/全零/空樹:拒認,另一半見 F2。引句:「推送範圍起點是全零或空樹(新分支首推),不認合進來那一側」
   - 淺 clone、逾時、git 出錯一律不認(失敗關閉)。引句:「這份 repo 是淺 clone,歷史不全,判不了合進來那一側」
   - 簿記資料夾夾帶程式:沿用 _codeloop_bookkeeping_code(可執行位、副檔名、shebang),新路徑沒有改它。
   - 分支手寫指向自己頂端的 pass:見 F1,與直推等價。
3. 密鑰與個資:reason 只含 sha 前 8 碼、固定句與帳本 branch 字串(見 F3),已看,無密鑰洩漏路徑。
4. 加密與傳輸:已看,無。
5. 執行邊界:diff 沒讓 CI 或掛鉤執行任何不可信位置的檔;子程序全是固定 git 參數列、無 shell=True。引句:「return _sp.run(["git", *args], capture_output=True, cwd=str(repo_root), timeout=left」
6. 行動端:不適用,已看,無。

總結:最高等級 minor;四道新條件(第一母=起點、第一母為第二母祖先且只差簿記、讀第二母帳本、紀錄含第一母)在我構造的假合併、手寫帳本、借舊紀錄情境下都按設計生效,殘留的 F1 是既有「帳本可手寫」信任模型、F2 為推論、F3 為縱深防禦,全為 minor。
