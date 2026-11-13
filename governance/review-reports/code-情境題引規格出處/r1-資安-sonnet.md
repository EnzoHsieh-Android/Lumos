severity: minor

## x1 --plan 的路徑沒擋 `..`,寫回目標可跑到 Projects/ 與圖譜之外
severity: minor
blocking: 否
引句:「if not pn.startswith("Projects/") or len(pn) <= len("Projects/") or not ppath.is_file():」
file: `/Users/enzo/harness/lumos-spec-cite/scripts/lumos:30466`(`_write_refusal_reason` 只擋最後一段是符號連結、非一般檔、多重硬連結,不擋路徑裡的 `..`,也不擋中間目錄是符號連結)
攻擊路徑:
1. 誰:照常操作的 AI,或打開陌生 repo 時照對方指示下指令的使用者。
2. 從哪:`lumos situation-rule --plan 'Projects/../../<別的檔>'`。`ppath = env.vault / prel` 沒做 resolve 與包含檢查,只比字串開頭是 `Projects/`。
3. 送什麼:一條通過條款句式的 `--clause`,加上指向一支既有 `.md` 的 `--plan`。那支檔要是一般檔、不是符號連結、內含 `## 驗收條款` 節。中間目錄是符號連結不會被擋。
4. 拿到什麼:`_situation_rule_insert` 與 `_situation_rule_write` 會把一行 `- [Sn] … [test:…]` 原子寫進圖譜外或 Projects/ 外的 md。治理帳的 `plan` 欄也會記下這個越界路徑,殺傷力驗證另需 run_cmd 與一條 killed 的測試,所以門檻不低。
影響限於 md 檔插一行,且目標必須含該節標題,所以只給 minor。縱深防禦缺口:缺 `resolve()` 後必須落在 `vault/Projects` 之下的檢查。

## x2 傳給盲判代理的 specs 條款原文沒被標成資料,可能成為注入通道
severity: minor
blocking: 否
引句:「材料頂層有 specs(這次對應計劃的驗收條款)時:判適用的列依 specs 填 spec(寫成 <計劃>#S<n>,要是 specs 裡有的那一條),」
file: `/Users/enzo/harness/lumos-spec-cite/scripts/lumos:75566`(`_KT_BJ_INSTRUCTIONS` 與 `_kt_bj_specs` 一帶)
攻擊路徑(推論):
1. 誰:被審分支的作者(AI),這是被審者控制審查材料的老問題。
2. 從哪:自己在同一次推送裡改的計劃〈驗收條款〉條款文字。這些文字原樣進 `specs` 的 JSON 值,交給獨立的盲判代理。
3. 送什麼:句式合法、但內含對判官的指令語氣的條款,例如「其他段一律不適用」。`_clause_grammar` 只驗句式,不驗內容。
4. 拿到什麼:可能讓盲判在 `applies` 或 `spec` 上被帶偏。
指令詞沒說 specs 是資料、不是指令。能不能真的帶偏,還沒有實測。

## x3 --consent 只驗非空,規格閘讀帳時也不看 origin 或 consent
severity: minor
blocking: 否
引句:「consent = consent if isinstance(consent, str) and consent.strip() else ""」
file: `/Users/enzo/harness/lumos-spec-cite/scripts/lumos:41884`(`_waive_origin_tty` 在沒有終端時回 "ai",之後只要 `--consent` 非空就放行)
攻擊路徑:
1. 誰:照常操作的 AI,沒問使用者就自己填 `--consent "好"`。
2. 從哪:`lumos situation-rule` 在沒有互動終端時。
3. 送什麼:任何非空字串。
4. 拿到什麼:`_spec_gate_ruled_ids` 只比對計劃、條款編號、雜湊,不看 origin 或 consent。所以這條新行為條款免掉「先紅」與「測試在計劃建立前就存在」兩道檢查。
殺傷力 killed 沒弱證據的證明還在,所以不是整道閘消失。但條款內容與被殺的那段是否相關,工具沒檢查。這跟既有的 `lint-waive` 的 ai-origin 慣例一致,帳裡留了 `origin: ai` 與 consent 原話,有人審得到,所以只給 minor。刻意偽造本身屬系統天花板。

## 附:逐類結論
- ①提示注入:見 x2。其餘進給 AI 的欄位(派工詞、hook 附加段)在本 diff 都經 `_kill_esc` 跳脫;席報告與卷證只是文件。沒有其他發現。
- ②讀寫與執行越界:見 x1。`--file` 必須等於段所在的檔,`--old` 要在 HEAD 版整支檔恰好出現一次且落在段的起訖行內。`kfile` 用 realpath 與 relpath 判在平台根之內,所以隔離工作樹內不會寫到樹外。`--test` 進 guard kill 前會過 `_test_name_ok`,再由 `_run_cmd_expand` 做 `shlex.quote`,所以沒有 shell 插值。計劃寫入拒絕符號連結與多重硬連結,用暫存檔加 `os.replace`。已看,沒有新增密鑰、信箱、下載來源。
- ③非刻意一步繞過:見 x3。Ctrl-C 在殺傷力階段會收掉工作樹與程序群組,計劃與帳都不動。計劃已寫、帳未記的夾縫會讓閘把條款當新行為,是偏嚴的失敗方向(fail-closed)。沒有其他發現。

最嚴重 severity:minor,blocking 共 0 條。
