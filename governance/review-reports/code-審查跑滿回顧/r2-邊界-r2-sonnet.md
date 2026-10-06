severity: major

席名:邊界-r2-sonnet(極端輸入立場)。實跑環境:臨時 repo(照 test_lumos.py 的 _cr_repo/_cr_loop 造帳,沒碰真帳)。
已打過且沒問題的邊界(不列 finding):治理帳檔尾 空檔/只有一個換行/CRLF/只有 \r/半行(補一個換行,新事件單獨成行、讀得回);_loop_records 新切行法遇 CRLF、最後一行沒換行、空行(都照常算 3 輪);回顧檔剛好 262144 位元組合格、262145 回 1 並說超過 256KB;--template --write 遇同名目錄、懸空符號連結、唯讀資料夾(都回 2 不丟堆疊、不建檔);非物件 JSON 行;回顧檔 evidence 含 NUL;回顧檔含孤立代理字元(--check/--record 回 1,retro-stats 與 --json 照算);回顧檔巢狀深度 1000;治理帳 decision 的 rounds 含孤立代理字元時 doctor/retro-stats/處置閘不炸。

### F1 孤立代理字元只防了「回顧檔」這一條來源,--template 的 context 與 --write 仍丟堆疊並留下 0 位元組檔(修補引起)
severity: major
blocking: 是 — 直接違反規格 S11「context 帳上欄位壞時印 null 不丟錯誤」;--write 是上輪新加的,失敗後留下空檔,下一次 --template --write 被「已存在」擋住
- 輸入:審查帳(docs/.canary-log.jsonl)某列的 auditor、report_path,或治理帳人裁事件的 rounds,含 JSON 跳脫的孤立代理字元(例如 "s1\ud800x";手改帳、或舊工具寫過都會有)。
- 走到哪:cmd_loop_retro 的 template 分支,ctx 把 auditor/report_path/round 原樣放進 skel,`_j.dumps(skel, ensure_ascii=False)` 得到含 \ud800 的 str;不加 --write 時 `print(text, end="")` 丟 UnicodeEncodeError;加 --write 時先 os.open(O_CREAT|O_EXCL) 建好檔,再到 `data = text.encode("utf-8")`,那一行在 `except OSError` 之外,丟 UnicodeEncodeError(ValueError 家族),fd 的 finally 雖然關了,檔卻已建成 0 位元組。
- 壞在哪:(a)堆疊而不是 null/訊息;(b)--write 留下空檔,之後 --template --write 回 2「回顧檔已經存在」,--check 回 1「不是合法 JSON」,要人手動刪;(c)同一份孤立代理字元的修補(`_retro_safe`)只套到印出與 stats,沒套到骨架。
- 重現:
  ```
  c=_cr_repo(); _cr_loop(c); 把最後一列 auditor 改成 "s1\ud800x"(json.dumps 預設 ensure_ascii); _cr_decide(c)  # rc 0
  lumos loop retro crx --template          # rc 1,UnicodeEncodeError ... print(text, end="")
  lumos loop retro crx --template --write  # rc 1,UnicodeEncodeError ... data = text.encode("utf-8"); cap-retro.json 大小 0
  ```
  report_path 含 "\ud800" 同樣重現;治理帳人裁事件 rounds 含 "r3\ud800" 時 --template 也重現。
引句:「data = text.encode("utf-8")」
佐證行:file: `scripts/lumos:13612`、file: `scripts/lumos:13623`
佐證行:file: `scripts/test_lumos.py:69593` — t_cap_retro_surrogate_no_crash 只造「回顧檔含代理字元」,沒有一條造「帳上欄位含代理字元」,所以這條路徑沒被測到。

### F2 --note 含非 UTF-8 位元組(或帳上輪次含孤立代理字元)時 cap-decision 與 --skip 丟堆疊,沒有「沒記到」訊息
severity: minor
blocking: 否 — 回碼是 1、沒有半行寫進帳;缺的是規格要求的說明
- 輸入一:`lumos loop cap-decision crx --decision extra-round --note $'\xff\xfe invalid bytes note here ok'`(argv 非 UTF-8 → surrogateescape 孤立代理字元,長度夠 10 字)。輸入二:`loop retro crx --skip --note $'\xff\xfe skip note bytes invalid'`。輸入三:審查帳某列 round 是 "r3\ud800" 時 cap-decision。
- 走到哪:`_retro_text_ok` 只看長度;cmd_loop_cap_decision / skip 呼叫 `_gate_event`,裡面 `json.dumps(..., ensure_ascii=False)` 後 `f.write(line)`,UnicodeEncodeError 不是 OSError,`except OSError` 接不到。
- 壞在哪:印出堆疊(rc 1),不是規格 S7/S10 的「寫不進去應回 1 並說沒記到」那句。
- 重現:上面指令,stderr 末行 `UnicodeEncodeError: 'utf-8' codec can't encode characters in position 140-141: surrogates not allowed`。
引句:「ok = _gate_event(root, "loop-retro", "cap-decision", note.strip(), hard=False,」
佐證行:file: `scripts/lumos:1502`

### F3 cap-decision 成功訊息把帳上輪次 id 原樣印到終端(控制字元未清)
severity: minor
blocking: 否 — 只影響終端顯示,不影響帳
- 輸入:`canary record none --loop crx --round $'r4\x1b[31m' ...` 這條正常 CLI 路徑就收(實測 rc 0、寫進審查帳);之後 `cap-decision crx ...`。
- 走到哪:cmd_loop_cap_decision 最後一行 `', '.join(rounds)` 沒過 `_esc_clean`,同一函式裡 loop_id 都有清。
- 壞在哪:實測 stdout 含 `r3\x1b[2Jevil‮` 原樣(ESC 與雙向覆寫字元)到終端。同一輪修補目標就是「帳上字串印終端前清掉」,這一處漏了。
- 另:`_esc_clean` 本身不清 U+202E/U+2028/零寬字元(只清 C0、DEL、C1),寬字元只按碼點截斷不按欄寬;與規格無直接條文,只註記,不另列 finding。
引句:「print(f"✓ 已記人裁:{_esc_clean(loop_id, 60)} {decision}(帳上輪次 {', '.join(rounds)})")」
佐證行:file: `scripts/lumos:13540` 附近

### F4 回顧檔是目錄或符號連結時,--check 叫人「--template --write 產骨架」,--write 又叫人先刪,提示繞圈
severity: minor
blocking: 否 — 有出口(手動刪)但提示不引導
- 輸入:cap-retro.json 是目錄、或懸空符號連結。
- 走到哪:--check 走 `_retro_read_bytes` 失敗 → 訊息尾端固定接「(lumos loop retro X --template --write 產骨架)」;照做則 --write 的 O_EXCL 回 FileExistsError →「已經存在…要重來先自己刪掉」。
- 壞在哪:第一句沒說「要先刪掉那個目錄/捷徑」,照貼會被第二句擋;doctor/stats/閘第八步的「沒有」提示(_cap_retro_template_cmd)在這個狀態是 state=stale,走 stale_hint 還算有說「刪掉後」,但 --check 這條與 record 前的 probs 沒有。
- 重現:`mkdir governance/review-reports/crx/cap-retro.json; lumos loop retro crx --check`(印 --template --write)→ `lumos loop retro crx --template --write`(回 2 已經存在)。
引句:「probs = [f"{rerr}:{_esc_clean(rel, 200)}(lumos loop retro {_esc_clean(loop_id, 60)} --template --write 產骨架)"]」
佐證行:file: `scripts/lumos:13009`(_retro_read_bytes 的錯誤字串由此帶出)

### F5 審查帳只用 \r 當行尾時,新切行法把整本當一行丟掉,帳被當成空的、不報帳壞(修補引起)
severity: minor
blocking: 否 — 沒有任何寫入端會產生純 \r 行尾;屬格式怪的檔,但與 S17 fail-closed 精神不合
- 輸入:docs/.canary-log.jsonl 的行尾全是 `\r`(舊 Mac 編輯器另存)。
- 走到哪:`_canary_ledger_scan` 的 `text.split("\n")` 得到一整串,json.loads 因 extra data 丟 ValueError → 被當壞行跳過;舊的 splitlines 會正確切開。
- 壞在哪:實測 `cap-decision crx` 回 2「crx 不在人裁紀錄的範圍」(帳上讀不到任何列),而不是「帳壞」;canary record 擋點也因此當成沒有人裁紀錄放行。CRLF、空行、無結尾換行都正常。
- 重現:`p.write_bytes(p.read_text().replace("\n","\r").encode()); lumos loop cap-decision crx ...` → rc 2 + 不在範圍。
引句:「for line in text.split("\n"):」
佐證行:file: `scripts/lumos:11882` 附近(_canary_ledger_scan)

### F6 圖譜:Systems/loop-retro.md 的 PITFALL 把「孤立代理字元不炸」寫成已涵蓋,實際只涵蓋回顧檔來源
severity: minor
blocking: 否 — 筆記句子比程式能做的寬,是線索不是合約
- 圖譜鏡頭(impact 固定席):loop-retro.md 第 26 行寫「含孤立代理字元的回顧判型別不合格,retro-stats 與 doctor 每個迴圈各自 try [test:t_cap_retro_surrogate_no_crash]」。實測帳上來源(審查帳欄位、治理帳 rounds)與 argv 來源(--note)仍讓 --template、cap-decision、--skip 丟堆疊(F1、F2)。
- 固定席其餘逐條看過:canary-record未落盤事件(寫後讀回合約)——本輪沒動 canary 寫入,補換行只在治理帳,不衝突;loop-convergence-recording 的 RecursionError PITFALL——新讀法 `except (ValueError, RecursionError)` 有接,未見衝突;reversibility-governance-ledger 的 4KB 整行與「只在換行切行」——補換行使整行最多 +1 位元組(O_APPEND 一般檔仍原子),未見可重現的失敗,不標;design-loop 的 spec-gate 略過列——`_canary_ledger_scan` 有略過,未見衝突。
- 修法方向只一句:F1/F2 併成「帳上字串與 argv 字串進骨架/進帳前一律 _retro_safe、write 路徑接 ValueError」一組根因修,並補「來源=帳、來源=argv」兩條先紅的測試,再把該 PITFALL 的出處補全。
引句:「回顧含孤立代理字元:--check 判型別不合格;retro-stats(含 --json)與 doctor 只標那一個、不炸。」
佐證行:file: `docs/lumos-toolchain-knowledge/Systems/loop-retro.md:26`

總結:最嚴重 major,blocking 1 條
