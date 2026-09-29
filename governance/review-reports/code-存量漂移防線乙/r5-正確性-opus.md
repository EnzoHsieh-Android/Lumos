severity: minor

# r5 正確性席(opus)——存量漂移防線乙 修正差異

審的材料:r5-snapshot.patch(484 行)。查證用的是 clone-ns 的 HEAD 5c8ee32f;測試 `/opt/homebrew/bin/python3 scripts/test_lumos.py -k drift_code_review_yi_r` 跑出 60 passed, 0 failed。

## F1 候選篩選的 partial 不分測試檔和程式檔,和正式判定對不上:正式判定確定不成立的行,在候選階段被報成判不了

severity: minor
blocking: 否 — 要有 blob 真的讀不出才會觸發(照 WHY 的前提,只有 git 壞掉才會這樣),而且修改前一樣會報判不了,不是這份差異新引入的;屬於修法沒修到的形狀
引句:「return True if hit else (None if names.partial else False)」

1. partial 的算法:`names_in` 把 `code_touched` 裡測試檔、非測試檔全部放進同一組 key,只要有一支讀不出就標 partial。
   file: `scripts/lumos:26642`
2. 正式判定分兩類:`one("symbol", …)` 只看非測試檔的語料,判不了的依據是 `_unread[False]`;`test` 條件反過來,只看測試檔。
   file: `scripts/lumos:26653`
   file: `scripts/lumos:26692`
3. 最小重現(3.14,在 clone-ns 根目錄跑,只讀不寫):
   `/opt/homebrew/bin/python3 -c "import runpy;m=runpy.run_path('scripts/lumos',run_name='t');f={'src/good.py','tests/test_bad.py'};t=m['_DriftProbeTree']('.','tip',f,m['_nodehome_layout'](sorted(f)));t._text={'src/good.py':'def target(): pass\n','tests/test_bad.py':None};ch={'touched':set(f),'renames':{},'code_shape':False,'code_touched':sorted(f)};print(m['_drift_probe_is_candidate']([('symbol','elsewhere')],ch,'docs/kg-knowledge/',None,lambda:t.names_in(ch['code_touched'])),t.one('symbol','elsewhere'),m['_drift_row_unread']([('symbol','elsewhere')],(),(t,)))"`
   輸出:`None False ['tests/test_bad.py']`。候選階段回判不了,但同一棵樹上的正式判定已經確定是 False(讀不出的是測試檔,`symbol` 條件根本不看它)。這一行會進 unknown,block 模式下就擋了推送(見 t_drift_unknown_blocks_check_not_scan);第三個值也顯示判不了的說明點名了一支和這個條件無關的測試檔。
4. 反過來也一樣:`test` 條件碰上讀不出的非測試程式檔,候選一樣回判不了。
5. 點名那邊同源:`_drift_row_unread` 對不帶路徑的條件用 `_drift_probe_code_path(q)` 篩,沒分 symbol 語料(非測試)和 test 語料(測試),所以會點名到正式判定沒用到的檔。WHY 新增的那行寫「只點名這一行條件實際碰到的檔」,和實際行為不符。
   file: `scripts/lumos:26881`

## F2 r3 回歸測試 docstring 的翻紅釘沒跟著改,還寫著已經刪掉的事先量測

severity: minor
blocking: 否 — 只是文件和測試內容對不上,不影響判定
引句:「候選遇到判不了就停 → B3 紅;3.12 以前不先量最長邏輯行 → C1 紅;」

1. 這份差異把 C1 改成驗 3.14 上 `_drift_py_names(deep)` 和 `_drift_py_names(elifs)` 回 None,`_drift_py_too_deep` 已經刪了;但同一個函式的 docstring(這份 diff 的上下文行)翻紅釘清單還寫「3.12 以前不先量最長邏輯行 → C1 紅」。
   file: `scripts/test_lumos.py:52918`
2. 照現在的 C1,真正會讓它翻紅的是「拿掉 MemoryError/RecursionError 的接法」或「flat 大檔解析不出」,docstring 沒寫,下一個看的人會照舊的描述去做翻紅實驗。

## F3 家筆記的 TEST: 清單沒加上新的 r4 回歸測試

severity: minor
blocking: 否 — 筆記內部不一致,不影響程式行為
引句:「t_drift_code_review_yi_r2_regressions、t_drift_code_review_yi_r3_regressions」

1. 這份差異在 Systems/存量漂移守衛 的摘要新增一條 PITFALL,帶 `[test:t_drift_code_review_yi_r4_regressions]`;但同一篇摘要的 `TEST:` 清單只列到 yi_r3,沒有 yi_r4。
   file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:38`

## F4 SHA-256 repo 的同一類問題還有一處:沒有起點時拿 SHA-1 空樹去比,git 直接報錯

severity: minor
blocking: 否 — 這是差異之前就有的行為,全庫共用同一個常數,不是這份差異的改動弄壞的;記下來是因為它和這份差異要修的「SHA-256 repo 每次判不了」屬於同一類
引句:「SHA-256 物件格式的 repo 提交編號是 64 碼;列檔快取原本只認 40 碼」

1. 找不到主線時,`_lens_push_base` 回 `_EMPTY_TREE_SHA`,也就是 SHA-1 的空樹 `4b825dc…`;drift check 把它轉成 base=None,`_drift_probe_changes` 再拿 `base or _EMPTY_TREE_SHA` 去跑 `git diff --name-status`。
   file: `scripts/lumos:31971`
   file: `scripts/lumos:26735`
   file: `scripts/lumos:33775`
2. 重現(在 mktemp 的暫存目錄):`git init -q --object-format=sha256 $T/r && git -C $T/r -c user.email=a@a -c user.name=a commit -q --allow-empty -m x && git -C $T/r diff --name-status 4b825dc642cb6eb9a060e54bf8d69288fbee4904 HEAD` → `fatal: ambiguous argument '4b825dc6…': unknown revision`,rc=128。SHA-256 的空樹是 `6ef19b41…`。
3. 結果是 `_drift_probe_prepare` 回「git 算不出這次推送改了哪些檔」,整道變成判不了。所以 SHA-256 repo 在沒有主線時,條件式回頭條件一律判不了;狀態那段 `scripts/lumos:26258` 也是同一種寫法。⚠ 範圍是全庫共用,不是這份差異的責任,列出來只供參考。

## 拿掉 3.12 以前的事先量測(3.14 上的極端輸入)

已看,無 finding。
引句:「c1 = (m._drift_py_names(deep), m._drift_py_names(elifs))」

在 3.14.6 上逐一用子行程跑 `_drift_py_names`,輸入包含:負號、not、~、`**`、三元、lambda、walrus、await、yield 串;屬性、下標、呼叫、加法鏈;elif、except、case、decorator、with 長鏈;巢狀 f-string、生成式、切片、連續指定、拆包。每種都試了 N=1000~300000,沒有一個程序崩潰,都是回 None(接住例外)或正常解析完,最慢約 2 秒(30 萬條 except/case)。深度 3 萬的屬性、下標、呼叫、加法鏈能解析,`ast.walk` 也不會出事。drift 路徑沒有跑在另開的執行緒上,不會碰到比較小的執行緒堆疊。精簡版產物(slim-gen 生成、不拉下限)雖然保留了 `_drift_py_names` 的定義,但沒有任何保留的指令會建 `_DriftProbeTree`,3.9 上也走不到。

## 列檔快取認 64 碼提交編號

已看,無 finding。
引句:「if not (isinstance(where, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", where)):」

`re.fullmatch` 對整個二選一都要求整串符合,40 碼和 64 碼都認得對。`_nodehome_list` 從 ls-tree 拆欄位,不假設長度。r4 的 A1 把規則改回只認 40 碼時確實會翻紅:退回用「版本:路徑」讀,NFD 檔名讀不到,`one` 就回 None 而不是 True。

## _drift_row_unread 對 status 與帶路徑條件的點名、_drift_bad_note 的跳脫

已看,無 finding(不帶路徑那一類見 F1 第 5 點)。
引句:「rel = env.resolve(link_target(v.partition("=")[0].strip())) if env is not None else None」

1. status 的解析和 `_drift_probe_one` 一模一樣。
2. 沒有起點時 benv 和 `trees.get(base)` 是 None,都有防到。
3. 候選階段傳的 envs 是空的,這不會漏點名:`_drift_probe_cond_candidate` 處理 status 時從來不回 None。
4. 帶路徑的條件用 `q == path` 比,和 prefetch、`one` 取路徑的方式相同。
5. `bad = [_esc_clean(q) for q in paths]` 會把控制字元換掉(含 C1),超過 200 字會截斷。

總結:最嚴重 minor,blocking 共 0 條(minor 4 條)。
