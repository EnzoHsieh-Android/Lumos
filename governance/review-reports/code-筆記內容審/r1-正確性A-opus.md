severity: major

# r1 正確性A-opus:筆記內容審(scripts/lumos + 派工詞範本)

審材:`governance/review-reports/code-筆記內容審/r1-snapshot-a.patch`(整份逐 hunk 讀完)。對照規格 `Projects/筆記內容審_計劃`。
重現腳本都放在 repo 外的 scratchpad(`.../scratchpad/ra/probe*.py`),借 `scripts/test_lumos.py` 的 `_na_*` / `_nh_*` 測試骨架在暫存目錄建 repo,不動 clone-ns 裡任何檔;`-k note_audit` 子集 111 passed(基線確認)。

## F1 已經收尾的計劃只是改名,也被當成「這次收尾」,整篇重新進完成審

severity: major
blocking: 是 — 規格明寫「只改名不重判」,實作卻讓整篇計劃每一行都變成沒涵蓋、推不上去
引句:「old = pairs[-1][1] if pairs else p」
file: `scripts/lumos:_note_audit_closed_plans`(審材第 623–630 行那段)

失敗場景:計劃 P 在範圍起點已經是 `status: done`;範圍裡第一個(也是唯一一個)碰到它的提交只做 `git mv P_計劃.md R_計劃.md`。`git log --follow` 對這個提交回報的是新路徑 R,所以 `old` 是 R;接著 `bb = _nodehome_cat_blobs(repo_root, [f"{base_where}:{old}"])` 去起點版本讀 R——起點只有 P,讀到 None,`base_state=None`。`seq=[None, 'done']` 被判成「從非收尾變成收尾」,整篇(正文、summary、有效決策)全部帶完成審編號進待審。
這跟規格兩處衝突:〈做法〉第 1 節「逐提交讀那篇的 status(…改名照改名偵測找舊路徑…)」——起點版本是存在的(在舊路徑),不該走「起點沒有這篇」那條;〈誠實界線〉「只改小標題或把筆記改名時,底下沒動的行不算新寫的行、不會被收進來重判」。300 行以上的已完成計劃改個名,就得整篇再派判定者(或 skip)。
測試 ⑬(改名同時改成 superseded)會過,但它是靠同一個錯誤過的:起點狀態被讀成 None,不是正確讀到 doing。
修法方向:最舊那個提交若是改名,要先用 `diff -M 起點 最舊提交` 找到它在起點的路徑再讀起點狀態。

最小重現:
```
python3 .../scratchpad/ra/probe1.py
P1 closed: ['docs/kg-knowledge/Projects/R_計劃.md'] items: 7 ['    context: 背景一', '    why_chosen: 因為一', '  WHY:計劃摘要', '# P_計劃', '## 目標']
P1 check rc 1 ...Projects/R_計劃.md:25  [沒判過]  ## 目標
  docs/kg-knowledge/Projects/R_計劃.md:26  [沒判過]  舊的脈絡行一
  docs/kg-knowledge/Projects/R_計劃.md:27  [沒判過]  舊的脈絡行二
```
(起點已經是 done、範圍裡只有一個 `git mv` 提交;check rc1,要求整篇重判)

## F2 筆記裡有 CR 字元(CRLF 換行的筆記)時,整份清單的「脈絡」判定一行都收不下,只能 skip

severity: major
blocking: 是 — 用 CRLF 提交的筆記永遠推不上去,除非 skip;而且同一批(最多 150 行、跨好幾篇)一起連坐
引句:「lst = _note_audit_parse_list(Path(prepared).read_text(encoding="utf-8"))」
file: `scripts/lumos:cmd_note_audit_record`(審材第 1030 行);寫入端 `_write_lf` 照原樣寫 bytes(`scripts/lumos:14153`)

失敗場景:prepare 從 git 讀筆記,`text.split("\n")` 會把每行尾的 `\r` 留著,清單本文照原樣寫出(`_write_lf` 不轉換),清單指紋是對「含 `\r` 的本文」算的。record 用 `Path.read_text()` 讀清單——文字模式會做通用換行轉換,把 `\r\n` 和單獨的 `\r` 都換成 `\n`。`_note_audit_parse_list` 對轉換後的本文重算雜湊,跟開頭寫的清單指紋對不上,`fp_ok=False` → `prov_ok=False` → 這份報告裡所有判 CONTEXT 的行都走「來源對不上,輕的判定不收」。
影響:CRLF 換行的筆記(工具自己在 `load_raw_for_edit` 就預期 Windows 使用者會遇到)推不上去;再怎麼重派判定者都一樣,只剩 skip。筆記裡任何一行夾了一個 `\r`,跟它同一份清單的其他筆記也一起收不下。
修法方向:讀清單用 `read_bytes().decode("utf-8")`(不做換行轉換),或寫清單前把 `\r` 正規化。

最小重現:
```
python3 .../scratchpad/ra/probe2.py
list has CR: True
fp_ok: False rows: 6
.../r.md:沒有能收的行
  06d6a3e061fae3f2:來源對不上,輕的判定不收
  ...(6 行全部)
check rc 1 ... [沒判過]  這是一行脈絡
```
(報告的四行開頭完全照抄清單,六行全判 CONTEXT)

## F3 同一個小標題下一字不差的兩行,清單只列第一處;判定者沒看過的那一處也被「脈絡」涵蓋

severity: major
blocking: 是 — 規格明寫「清單列出每一處」,派工詞第⑦句也預設會列好幾處;現在輕的判定會涵蓋判定者沒看過上下文的那一行,這正是信任方向要擋的
引句:「uniq.setdefault(it["id"], it)」
file: `scripts/lumos:cmd_note_audit_prepare`(審材第 990–996 行);record 那邊的 `cur_ctx.setdefault(it["id"], it["ctx_fp"])` 同樣只記第一處

失敗場景:筆記 `## 小節` 下兩處都寫 `- 理由同上`,第一處接在「當初選這個是因為客戶要求」後面(脈絡),第二處接在「src/a.py 第三個函式只接受整數」後面(推得出)。兩行內容編號相同(路徑、區塊、小標題、文字都一樣)。prepare 用 `uniq` 去重,清單只放第 20 行(第一處)的上下文;判定者只看得到脈絡那一處,判 CONTEXT,record 收下(上下文指紋也只比第一處),check 認為兩行都涵蓋了。
規格〈做法〉第 2 節:「同一小標題下一字不差出現兩次的,共用一個編號,清單列出每一處;判定者對一個編號只給一個判定,兩處語境不同時給較重的那個(派工詞第⑦句)」。範本第 7 條「If the same content id is listed at several places…」現在永遠不會發生。
修法方向:清單照編號分組,但每一處都列(行號、上下文、指紋);record 的上下文比對要涵蓋每一處。

最小重現:
```
python3 .../scratchpad/ra/probe3.py
items with 同上: [(20, '6b6a9c27fec2958b'), (23, '6b6a9c27fec2958b')]
list occurrences of 同上: 1
```

## F4 decision-amend 碰到中間有空行的多行值時,只換掉空行前那段,舊句子留在檔裡,卻回報「改好了」

severity: major
blocking: 是 — 這支指令存在的目的就是刪掉決策裡被判推得出的句子;現在那句會留下來,工具還說成功
引句:「while k1 + 1 <= en and (len(fm[k1 + 1]) - len(fm[k1 + 1].lstrip(" "))) > sub」
file: `scripts/lumos:cmd_decision_amend`(審材第 1262–1268 行)

失敗場景:決策 `context: |-` 下有兩段、中間隔一行空行(本 repo 已經有 5 篇筆記的決策欄用 `|-` 多行值)。續行迴圈用「縮排比子鍵深」判斷續行,空行的縮排是 0,迴圈就停在空行前面。新值只換掉 `context: |-` 到空行之間的內容,空行跟第二段(`      src/a.py 第 3 行把逾時設成 30 秒`)原封不動留著。`atomic_write_verify` 的自我檢查用的是 lumos 自己的 `parse_decisions`:它把新值當單行、跳過那行沒有冒號的孤兒行,所以檢查通過,rc0 並印「改好了」。
後果:①標準 YAML 讀這段會得到 `'只留脈絡\nsrc/a.py 第 3 行把逾時設成 30 秒'`——被判推得出的那句反而黏進了新值;②筆記內容審下一次照樣列出那行(文字沒變、小標題還是 `decisions/d1/context`、之前判 CODE 的編號沒變),check 繼續擋,作者看不出為什麼。
修法方向:續行迴圈要跳過空行(空行後面還有更深縮排的行,就算同一欄),或直接拿 `decisions_items` 的項目範圍配 `parse_decisions` 的塊值終止規則(第一個縮排 ≤ 鍵欄位的非空行)。

最小重現:
```
python3 .../scratchpad/ra/probe4.py
rc 0 ✓ decision-amend Projects/P_計劃.md d1.context 改好了(這條決策還沒推上去)
decisions:
  - id: d1
    decided: 2026-09-01
    context: 只留脈絡

      src/a.py 第 3 行把逾時設成 30 秒
    why_chosen: 因為一
python3 -c "import yaml; …"  →  '只留脈絡\nsrc/a.py 第 3 行把逾時設成 30 秒'
```

## F5 設定檔把 note_audit 寫成字串時靜默照 block,不像第一層會提醒

severity: minor
blocking: 否 — 方向是多擋、不會放過;但使用者不知道自己的設定沒被採用
引句:「na = cfg.get("note_audit") if isinstance(cfg, dict) else None」
file: `scripts/lumos:_note_audit_config`(審材第 568–571 行)

失敗場景:`.lumos/config.json` 寫 `{"note_audit": "warn"}`(少一層 `gate`)。`na` 不是 dict,`g=None`,回 `("block", [])`:check 照擋、doctor 不唸,沒有任何提醒。第一層同樣寫錯會回「設定檔的 note_shape 不是物件,筆記形狀擋照預設擋」(實測:`_note_shape_config(b'{"note_shape": "off"}')` 有提醒,`_note_audit_config(b'{"note_audit": "off"}')` 回 `('block', [])`)。docstring 說「照 _note_shape_config 的讀法」,實際上不一致。

## F6 doctor 兩處跟規格字面不同,實作紀錄沒列:CI 提醒要等接線才唸;判定檔刪除次數讀的是本機 HEAD

severity: minor
blocking: 否 — 行為合理,但規格與程式對不上,屬於內部不一致
引句:「還沒接線(推送前掛鉤裡沒有這道)就不唸 CI」
file: `scripts/lumos:_note_audit_doctor_lines`(審材第 1300、1309 行)

失敗場景:①S16 與〈做法〉第 9 點都寫「專案 CI 沒呼叫 note-audit check 時印一行」,沒有「接線以後才唸」這個條件;程式只在推送前掛鉤已經有標記時才唸(測試 ③ 也把它釘成這樣),但〈實作紀錄〉列的「跟設計字面不同的地方」沒有這一條。②〈做法〉第 9 點寫「(兩件事)都從遠端頂端提交讀」,但刪除次數是 `"log", "--diff-filter=D", "--format=%H", "--name-only", "HEAD"`——本機還沒推、甚至只是實驗性的刪除提交也算進去(測試 ⑤ 的刪除提交就沒推)。要嘛改程式、要嘛把這兩點補進實作紀錄並改 S16 措辭。

## F7 證據驗證:行號範圍的後半段沒驗;search 指向不存在的路徑、寫 `=> 0` 會被當成驗過

severity: minor
blocking: 否 — 證據只做紀錄、不影響涵蓋;但 `evidence_ok` 這個欄位會被當成品質數字看
引句:「st, _ex = _validate_repo_ref(root, m.group(1), m.group(2), at_sha=tip)」
file: `scripts/lumos:_note_audit_check_evidence`(審材第 919–936 行)

失敗場景(實測,src/a.py 只有 20 行):`src/a.py:3-999` → True(`m.group(3)` 抓到了卻沒傳下去,只驗第 3 行);`search: TIMEOUT in no/such/dir => 0` → True(`ls-tree` 對不存在的路徑 rc0、輸出空,`git grep` 找不到 → cnt 0,等於 0)。判定者把「沒有 X」的搜尋寫錯路徑,正好會被標成證據合格。`git grep` 逾時或出錯(`g is None`)時同樣算 0 次,`=> 0` 的證據也會過。修法:把 `f"{m.group(2)}-{m.group(3)}"` 整段傳給 `_validate_repo_ref`;`search:` 的路徑 `ls-tree` 輸出為空就判不合格;grep 失敗不算 0。

## F8 record 讀到不是 UTF-8 的報告或清單時直接噴 traceback,不是 rc2

severity: minor
blocking: 否 — 只影響錯誤訊息
引句:「head, rows = _note_audit_parse_report(Path(rp).read_text(encoding="utf-8"))」
file: `scripts/lumos:cmd_note_audit_record`(審材第 1059–1063 行、第 1029–1033 行)

失敗場景:Windows 上用 cp950 存的報告 → `UnicodeDecodeError` 不是 `OSError`,沒被接住。實測:
```
python3 .../scratchpad/ra/probe7.py
rc 1 UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb2 in position 9: invalid start byte
```
其他子指令都是「擋下:…」加 rc2;這裡的 except 要加上 `UnicodeDecodeError`(清單那一處同樣)。

## 審過沒有問題的地方(摘要)

- 信任方向:重的照收、輕的要 `prov_ok`(四行開頭、編排者、模型、清單指紋、`fp_ok`、派工詞版本)而且上下文指紋對得上;申訴另外要求席名不同、被申訴的檔真的判過那行。沒有找到能讓 CONTEXT 在來源不對或上下文變了時被收下的路(F3 同編號多處是例外)。清單本文裡筆記的每一行都帶 `>>> ` 或四格縮排前綴,偽造 `## <編號> |` 列一定會改變本文雜湊,`fp_ok` 就會失敗;報告開頭取第一次出現,同編號多列取最重,偽造的輕列蓋不掉判定者自己的重列。
- `_note_audit_fold`:申訴按(被申訴檔名, 編號)取最重、一般判定取最重、略過只在沒判定時生效,跟讀檔順序無關;check 只讀頂端提交的樹(`ls-tree` 加批次讀),壞檔略過並印名。
- 共用抽行:`_notelines_new` 對第一層的呼叫方式(`mark or _NOTE_SHAPE_GOLIVE_MARK`、逐提交判、`exclude_remote`、`max_count`)跟抽出前等價;第二層明寫 `per_commit=False`,上線點與截斷改看推送前掛鉤。
- 40 個 0 的起點、淺層 clone、空範圍、刪掉的檔(`--diff-filter=AMR`)、含空白與中文檔名(`-z`、NFC 鍵搭配原樣路徑)的處理跟第一層一致。
- 併發:判定檔用 uuid 命名加 `_write_lf`(暫存檔名每次不同),檔名正則排除 `.tmp-wlf`;兩個 prepare 寫出同名清單時內容一樣,原子取代不會壞。
- 結構行、圍欄內的小標題、決策編號加欄名、已翻案決策只在完成審排除:都照規格,索引從 1 起算(`_visible_lines` 回傳從 1 起)。

## 圖譜鏡頭(固定席節點)

- Systems/pitfalls-code-loop ★RISK★、Systems/loop-convergence-recording ★RISK★:`_BOOKKEEPING_DIRS` 多了 `governance/note-verdicts/`,代碼審留痕的豁免因此也涵蓋「只新增判定檔」的提交。該節點的原則是「pass 不得蓋到新代碼」,判定檔是 JSON 紀錄、不是程式碼,筆記的刪改仍然會讓留痕失效——不破壞。附帶一點:該節點第 45 行寫「三個消費者」,規格這次寫四個,文件那一席可以對一下。
- Systems/授權與歸屬 ★INVARIANT★:範本加進 `_VENDORED_TREE_FILES`,檔頭有兩行 SPDX,也不是授權檔——不破壞。
- Systems/lumos-deinit、slim-install/get/uninstall:白名單多一支工具自己的範本檔,deinit 會把它刪掉,這是對的(工具檔,不是使用者的檔)——不影響。
- Systems/reversibility-governance-ledger:`_KNOWN_GATES` 多了 `note-audit`,只多一個名字——不影響既有閘的統計。
- Systems/lumos-cli-read ★INVARIANT★(search 排除 superseded)、guard-kill ★INVARIANT★(rc 優先序、JSON 純度)、lumos-cli-lifecycle ★INVARIANT★(reinject)、design-loop ★INVARIANT★(處置閘第五步)、check-r-guard、check-t-sentinel、lumos-refcheck、cochange-guard、core-invariant-baseline、judge-severity-gate、canary-audit:這份 diff 沒碰到這些路徑(只改了相鄰的常數、doctor 多一段包在 try 裡的提醒、新增子指令)——不影響。
- Systems/doctor-irreversible-hint:doctor 多一段提醒,包在自己的 try/except 裡、壞了只印一行,不會中斷後面的檢查——不影響。
- Systems/節點範圍與索引守衛:新增的 `.md` 範本不是程式檔,不需要自己的家;第二層的程式碼歸 `Systems/筆記內容審`——不影響(家寫得對不對由文件那一席確認)。
- Systems/bound-tests-gate、Projects/雙向門放行_計劃:判定檔在 `governance/`、副檔名 `.json`,在純文件白名單裡,只推判定檔時跑文件子集——不影響;範本在 `scripts/` 底下,改它會跑全套,這是對的。
- Systems/測試假綠形態 ★INVARIANT★:測試歸另一席;這裡只補一點:測試 ⑬ 會過是因為 F1 那個錯誤(起點狀態讀成 None),不是因為真的偵測到從非收尾轉成收尾。
- Projects/規格落成可驗收條件_計劃、Projects/逃逸自動記_計劃:沒有改到條款綁定或逃逸帳的程式——不影響。

總結:最嚴重 major;blocking 共 4 條(F1–F4)。
