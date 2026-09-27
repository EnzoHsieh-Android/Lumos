severity: major

# r3 通才審查(opus)——筆記形狀擋 r3-delta

所有重現都在 /tmp 底下用測試檔自帶的輔助函式(`_ns_repo`、`_ns_note`、`_ns` 等)另開臨時 repo 跑。沒改 clone 裡的任何檔,也沒在 clone 裡跑會寫入的 git 指令。
重現共用的開頭 `/tmp/r3o/h.py`:用 importlib 從 clone 載入 `scripts/test_lumos.py`,載入後的模組叫 `tl`。
要跟這批修正之前的版本(8488e989)對照時,把 `git show 8488e989:scripts/lumos` 放到 `/tmp/r3o/old/scripts/lumos`,旁邊擺一份同樣的 test_lumos.py(開頭檔改叫 ho.py)。
`python3 scripts/test_lumos.py -k note_shape`:84 passed, 0 failed。

## F1 喚醒檢查不再剝掉 [src:]:重建筆記 summary 的出處標記,指向同一次新增的程式檔時被誤擋
severity: major
blocking: 是 —— 誤擋;這批修正自己引入(上一版在喚醒那段對整行剝掉 [src:])
引句:「fl, _b = _node_code_ref_tokens(ln, top_dirs, bare_text=True, anchors=True, keep_fences=True,」

這批把逐行檢查的 [src:] 豁免收窄成「帶 regen 的筆記的 summary 才豁免」(`scripts/lumos:23658`),但喚醒那段(`scripts/lumos:23807`)把原本的 `_NS_SRC_MARK_RE.sub(" ", ln)` 直接拿掉,沒有換成同樣的豁免。
結果是同一行被逐行檢查放行後,又被喚醒檢查擋下:逐行檢查放行的行不會進 `seen`,喚醒檢查也不看 regen 與區塊,於是照擋。
會碰到的情境很常見:新增一支程式檔,同一次提交或推送裡重建筆記,重建出來的 summary 寫著 `[src:該檔:行號]`。
重現(`/tmp/r3o/f1.py`):
```
root=_ns_repo(); 新增 src/new.py; _ns_note(summary="KEY:x\nKEY:出處 [src:src/new.py:3]", extra="regen: from-scratch/2026-09-27"); git add -A; note-shape --staged
現版本 → (1, '擋下:… A.md:16  程式行號引用(新程式檔喚醒) `src/new.py:3` …')
對照:[src:src/a.py:5](指向既有檔)→ (0, '')
修正前的版本(8488e989)跑同一支 → new file: (0, '')
```
改法:喚醒這段套用同一個條件,也就是 `regen and regs[n-1]=="summary"` 時先剝 SRC_REF_RE;或者乾脆共用逐行檢查的區塊判定,順便跳過 "other" 區塊。

## F2 上線前開的分支在上線後合進主線,裡面上線前寫的舊帳被當成新違規擋下
severity: major
blocking: 是 —— 誤擋,違反 [S4]「上線前就有的舊內容首次推送不應被擋」;這批的「頂端已在主線就不排除」讓消費專案 CI 推 main 時整段 BEFORE..SHA 都查,這條從此會踩到
引句:「ml = _ns_exclusions(repo_root, tip)」

上線點截斷只截起點(`_nodehome_clamp_base`,`scripts/lumos:22940`),而且只看直線歷史。上線前從主線分出去的分支,它的提交在上線後才合進來時會出現在 `before..merge` 的 rev-list 裡,逐提交算新增行,舊帳就被報成新違規。
這批之前,消費專案照 doctor 那步貼的 CI 會拿 origin/main(=頂端)排除,結果整批不查(那是另一個洞)。現在改成不排除,等於整段都查,這個誤擋就浮上來了。本機推 main 走的是 `origin/main..main` 且只排除主線,情況相同。
重現(`/tmp/r3o/f2.py`):
```
_ns_repo(golive=False);掛鉤先不含標記 → 開 old-side 分支,寫 Old.md「上線前的舊帳 `src/a.py:5`」→ 回主線提交上線點(掛鉤加標記)→ before=HEAD → merge --no-ff old-side
note-shape --diff before..merge → (1, '擋下:… Old.md:5  程式行號引用 `src/a.py:5` …')
```
改法:逐提交時跳過「上線點不是它祖先」的提交,用 `merge-base --is-ancestor gl sha`,因為那個提交的掛鉤還沒有這道檢查。合併提交照舊只算它自己寫的行。doctor 的事後掃描是同一個根因,會把這類舊帳報成「繞過」。

## F3 推送範圍改成照檔案記以後,用來查的路徑沒做 NFC 正規化:NFD 檔名的筆記推送前與 CI 整篇漏查
severity: major
blocking: 是 —— 放過該擋的;這批修正自己引入(上一版用全域文字集合,不受路徑鍵影響)
引句:「if texts_by is not None and ln.strip() not in texts_by.get(p, ()):」

`by_path` 的鍵有做 NFC:`_ns_parse_added` 在 `scripts/lumos:23518` 用 `nfc(p[2:])`,`_renames` 也經過 `_nodehome_name_status` 的 nfc。
但拿來查的 `p` 來自 `_nodehome_split_z(net)`(`scripts/lumos:23633`),只做 fsdecode、沒有 nfc,合併提交那段的 `paths`(`scripts/lumos:23611`)也一樣。
所以 git 裡存的是 NFD 路徑時(Linux 建的、或 core.precomposeunicode=false 的片假名濁音、韓文、帶重音的拉丁字母),`texts_by.get(p)` 永遠查不到東西,那篇整篇跳過。提交前那條路有擋到,但 `--no-verify` 之後的後盾(推送前與 CI)失效。
重現(`/tmp/r3o/f4.py`):
```
_ns_repo(); git config core.precomposeunicode false; 新增 Systems/<NFD「ポリシー」>.md 內含 `src/a.py:5`; commit
現版本 note-shape --diff b..t → (0, '')      對照 NFC 檔名 → 1
修正前版本(f4o.py)→ (1, '擋下:… ポリシー.md:5 程式行號引用 `src/a.py:5` …')
```
改法:`net` 與合併的 `paths` 都過一次 `nfc()`,跟 `_ns_parse_added` 和 `_nodehome_list` 一致。

## F4 裸寫的 `路徑@<含 / 的分支名>:行號` 抽取器根本沒抽到,r2 修的「@origin/main 放過」只修了反引號那半
severity: major
blocking: 是 —— 放過該擋的:[S2] 要求分支名寫成 `@` 形狀時照樣擋,本輪就是在修這一類
引句:「r"(?:@[A-Za-z0-9_.\-~^]+)?(?::\d+(?:-\d+)?|#L\d+)(?![\w/])")」

裸寫的候選正則(`scripts/lumos:19940`)在 `@` 後面的字元類別不含 `/`,所以 `src/a.py@origin/main:5` 對不上。
改從 `main` 或 `origin` 開頭匹配也不行:前面緊鄰 `/` 或 `@`,被前向否定擋掉。整段就沒有任何候選,exists 切分那段根本輪不到。
改掉原本 `src/a.py:5` 的寫法、加一個遠端分支名,就能完整繞過。
重現(`/tmp/r3o/f3.py`,note-shape --staged 的 rc):
```
'見 src/a.py:5' 1
'見 src/a.py@origin/main:5' 0      ← 放過
'見 `src/a.py@origin/main:5`' 1
'見 src/a.py@feature/x#L5' 0        ← 放過
```
改法:裸寫正則的 `@` 段允許 `/`,例如 `@[A-Za-z0-9_.\-~^/]+`。反正切分與合法性都交給 exists 和 `_pin_commit` 判,放寬候選不會多放。

## F5 喚醒檢查把釘版本整批丟掉:先寫 `路徑@HEAD:行號`、後加檔的兩步走,壞釘法永遠不被抓
severity: minor
blocking: 否 —— 窄,要刻意兩步走;這個行為本輪之前就有,本輪改 pins/exists 時沒補
引句:「hits = [(tok, l) for tok, l in fl if tok in became and l]」

喚醒那段傳 `pins=[]` 卻從來不讀它(`scripts/lumos:23810`)。第一步寫 `src/later.py@HEAD:3` 時檔還不存在,不會切,也就不擋。第二步加檔後切成了 pin,卻被丟掉。
對照組 `src/later2.py:3` 有被喚醒擋下。
重現(`/tmp/r3o/f5.py`):`step1 (file absent): 0`;`step2 (files added): 1 later.py@HEAD flagged: False later2 flagged: True`。

## F6 指路行豁免的分隔符太窄會誤擋,連結的 `#標題` 又能夾帶現況
severity: minor
blocking: 否 —— 只是 summary 的 FLOW/DEP 會多擋或少擋一點;單次提交改寫就能過
引句:「_NS_POINTER_ONLY_RE = re.compile(r"^(?:\s*(?:\[\[[^\]|]+\]\]|見|→|,|,|、|\||｜)\s*)*$")」

中文句尾的「。」、連接詞「與」、全形「;」都不在分隔符裡,純指路行會被判成「現況描述沒寫來源」。
另一方面,r2 擋了 `|別名`,但 `[[Systems/Billing#扣款門檻 180 秒]]` 照樣能放過:同一類夾帶換個符號而已。
重現(`/tmp/r3o/f6.py` 與 f3.py):`DEP:見 [[Systems/Billing]]。` → 1;`DEP:[[A]] 與 [[B]]` → 1;`FLOW:→ [[A]];[[B]]` → 1;`DEP:[[Systems/Billing#扣款門檻 180 秒]]` → 0。

## F7 doctor 的 200 提交上限在合併式歷史退掉之後,變成從上線點起全量掃
severity: minor
blocking: 否 —— doctor 不是閘,只影響速度
引句:「if b2 and anc is not None and anc.returncode == 0:」

`tip~200` 沿第一個上一版往回數。用 PR 合併的專案裡,上線後第一個上一版的提交數少於 200、但總提交數遠超過時(例如 150 個 PR、每個 10 個提交),上限會被取消,改從上線點掃全部約 1650 個提交(`scripts/lumos:23885`)。
照 r1 量到的每個提交約 20 ms 算,單次 doctor 約 30 秒以上,還會隨時間線性變長。
建議:改成用 `rev-list --max-count` 在 `gl..tip` 內取最舊邊界;或者退掉上限時也維持只掃「上線點之後、最近 N 個」的提交集合。

## F8 doctor 給消費專案的那一步用 && 串建本地 main,主分支叫 master 的專案照貼,CI 每次都紅
severity: minor
blocking: 否 —— 文字裡有說明要換掉;而且是明顯失敗、不是靜默放過
引句:「"(git show-ref -q --verify refs/heads/main || git branch --track main origin/main) && "」

origin/main 不存在時,`git branch --track` 會失敗,整串 && 跟著中斷,note-shape 沒跑、整步變紅(`scripts/lumos:23844`)。
工具鏈自己的 CI 同一行寫的是 `|| true`(`.github/workflows/ci.yml:132`),兩邊不一致。
建議:照 CI 加 `|| true`。建不成本地 main 時,`_mainline_ref` 找不到主線就不排除,只會多查。

最高 severity:major;blocking 條數:4
