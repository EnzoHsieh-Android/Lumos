severity: major

# 代碼審第 4 輪 正確性-opus(主審 r4-delta.patch,d219e935..0f1e68ea)

實驗環境:`git clone --shared` 到自己的臨時目錄 `kcc-r4-work-正確性-opus/repo`(HEAD 0f1e68ea),macOS APFS(暫存資料夾量到 `(不分大小寫, 不分寫法) = (True, True)`)。
基線:`python3 scripts/test_lumos.py -k t_kill_recipe_check` → 98 passed, 0 failed。

## F1 「還原到別的檔」那支 unrestorable 跟真跑 guard kill 對不上:提醒說「會判 error、後面的配方不跑」,實跑兩者都沒發生,真正的後果是後面的配方被誤判 killed
severity: major
blocking: 是
引句:「f"同組後面的配方讀到改壞的內容,改寫成 {_kill_show(rel)}"}」
file: `scripts/lumos:13382`
file: `scripts/lumos:13269`
file: `scripts/test_lumos.py:60314`

1. 第 3 輪新增的分支(`got is not None and rel not in got`)沿用 unrestorable 狀態,但 unrestorable 原本的意思是「還原失敗 → guard kill 判 error、同組後面的配方不跑」(判斷函式 docstring 的對應表、kill-add 提醒的固定字面都這樣寫)。對這個新分支,guard kill 的 `git checkout -- p.py` 是**成功**的,不會判 error,也不會中斷後面的配方。
2. 實跑 kill-add(單條配方,`p.py` 是指向 `prod.py` 的檔案連結,原文恰好一次),同一行裡自相矛盾——前半說「同組後面的配方讀到改壞的內容」,後半說「同組後面的配方不跑」:
   ```
   kill-add rc 0
   stderr: ⚠ 提醒:"p.py" 壞法套得上,但這樣寫路徑還原不到被改的那支檔(經過檔案連結或對到別的檔),改壞的檔會留著、同組後面的配方讀到改壞的內容,改寫成 "prod.py";guard kill 會判 error、同組後面的配方不跑。修法:…
   guard kill rc 1 [('survived', ' whole-suite')]
   ```
3. S5 對應表(條款 S5「判定應跟真跑 guard kill 的結果一一對應」)只在「同組第二條剛好是同一支檔、而且判 drifted」時成立;對照測試的 `_krc_match` 也是為這一格量身放寬的。換成「後面一條是別的檔」或「只有這一條」,對照表自己就判對不上。重現(`exp5.py`:`_krc_cell` 加 `t.py = import prod; assert prod.LIMIT == 5`、`other.py = X = 1`,呼叫測試檔自己的 `_krc_match`):
   ```
   == 單條:p.py 連結
     判斷函式 ['unrestorable']
     guard kill rc=1 [('p.py', 'killed_unattributed')]
     _krc_match(第一條): (False, 'killed_unattributed', …)
   == p.py 連結 + 後面一條別的檔 other.py
     判斷函式 ['unrestorable', 'ok']
     guard kill rc=1 [('p.py', 'killed_unattributed'), ('other.py', 'killed_unattributed')]
     _krc_match(第一條): (False, 'killed_unattributed', …)
   ```
4. 第二組顯示真正的後果:`other.py` 的壞法(`X = 2`)測試根本不看,應該 survived,卻因為 `prod.py` 還留著被改壞的內容而被判 killed——**假的殺傷證據**,而且 guard kill 不會報任何錯。提醒講成「判 error、後面不跑」,使用者照著去 guard kill 對,會看到沒有 error,以為提醒錯了;真正該警告的「後面的配方結果不可信(可能假 killed)」反而沒講。單條或排在最後的情形,工作樹跑完就刪,改壞的檔沒有任何影響,P2 照樣列出,是誤報。
5. 建議:這個分支換一個狀態(或至少換提醒字面與對應表):講清楚「還原的是連結本身、被改的檔留著,同組之後的配方結果不可信(可能假 killed/drifted)」;docstring 的對應表與 `_krc_match` 的放寬條件一起改成照實際行為,並把「後面一條是別的檔」這格加進對照測試。

## F2 new 或 file 夾孤立代理字元:判斷函式判 ok / missing,guard kill 程式出錯(rc 1)
severity: major
blocking: 是
引句:「if "old" not in r or not isinstance(r.get("new"), str):」
file: `scripts/lumos:14012`
file: `scripts/lumos:13994`

1. 第 3 輪把「old/new 沒寫」的檢查改寫成只看「有沒有、是不是字串」,file 的檢查也只看「是不是字串、有沒有 NUL」。筆記裡的配方是 JSON,`"\ud800"` 這種跳脫讀回來是 Python 字串、通過 `isinstance(..., str)`,但 guard kill 寫檔(`open(target, "w", encoding="utf-8")` 寫 `src.replace(r["old"], r["new"], 1)`)或組路徑開檔時編碼失敗、整支崩潰。這跟判斷函式已經處理的「NUL 字元 → malformed」同一類,只處理了一種。
2. 重現 new(`exp2.py`:`_krc_cell()` 後把 `rec["new"] = "\ud800"`,用 `json.dumps` 預設跳脫寫進筆記並提交):
   ```
   讀回的 new: '\ud800'
   判斷函式: {'status': 'ok', 'detail': '', 'plat': 'csharp-xunit', 'file': 'prod.py'}
   guard kill rc= 1 stdout=
   stderr尾= ["UnicodeEncodeError: 'utf-8' codec can't encode character '\\ud800' in position 0: surrogates not allowed"]
   ```
   判斷函式說 ok(P2 不列、kill-add 不提醒),guard kill 程式出錯——S5 對應表裡「程式出錯」對的是 malformed。另外 guard kill 用 `"w"` 開檔時已經把工作樹裡的目標檔清空才在寫入時崩,所幸工作樹在 finally 被移除。
3. 重現 file(`exp3.py`:`rec["file"] = "pro\ud800d.py"`):
   ```
   判斷函式: {'status': 'missing', 'detail': '不存在', …}
   guard kill rc= 1  ["UnicodeEncodeError: 'utf-8' codec can't encode character '\\ud800' in position 83: surrogates not allowed"]
   ```
   判斷 missing(對應 drifted),guard kill 程式出錯。
4. 這兩格不是第 3 輪引進的(第 2 輪的檢查也只看型別),但正落在第 3 輪改寫的那兩條規則上。建議:new 與 file 再加「`x.encode("utf-8")` 會不會失敗」(file 用 `os.fsencode`),失敗判 malformed;對照測試補這兩格。

## F3 只不分大小寫(分寫法)的檔案系統上,比對鍵也把寫法摺掉了,比第 2 輪退步
severity: minor
blocking: 否
引句:「return nfc(unicodedata.normalize("NFD", x).casefold())」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:149`

1. `_kill_fold_key` 在 `ci=True` 時不管 `ni` 是什麼,一律回組合寫法的鍵,等於「不分大小寫就一定也不分寫法」。量到 `(True, False)` 的檔案系統(Windows NTFS 就是:不分大小寫、但拆開與組合的寫法是兩支不同的檔;本工具有 `_IS_WIN` 分支,`_kill_split` 也照 Windows 規則切)上,拆開寫法的 `café.py` 會被對到提交裡組合寫法的 `café.py`。
2. 單元對照(本 HEAD 與第 2 輪 d219e935 各跑一次):
   ```
   r3 (True, False) 'café.py'      ← 現在
   r2 (True, False) None           ← 第 2 輪
   (False, False) None / (False, True) 'café.py' / (True, True) 'café.py'
   ```
   第 2 輪的 `fold` 是「ni 才組合、ci 才轉小寫」各管各的,這種檔案系統判得對;第 3 輪改成標準比對時把兩件事綁在一起。
3. 在 NTFS 上的後果:原文恰好一次時判斷函式走別名讀到 `café.py`、再問 git 對不到 → 判 unrestorable(「壞法套得上」);guard kill 實際開 `café.py` 開不到 → drifted。狀態與說明都錯。
4. 未能重現(真跑):本機 macOS 掛 exFAT、FAT32 映像量到的都是 `(True, True)`,造不出只不分大小寫的檔案系統,所以自降一級。計劃〈實作紀錄〉的「不涵蓋」只列了「暫存資料夾與 repo 不在同一種檔案系統、casefold 跟大小寫表不同的少數字元」,沒有涵蓋這一種。建議:`ci and not ni` 時鍵改成 `unicodedata.normalize("NFD", x).casefold()` 之後**不**組合,或乾脆照第 2 輪各管各的;`t_kill_recipe_check_fs_and_git` 補一列 `((True, False), "café.py", None)`。

## F4 kill-add 驗原文改到寫入之後,兩處 docstring 還寫「寫入前」
severity: minor
blocking: 否
引句:「# 判重之後:這次實際要寫進去的那一條交給呼叫端在鎖外驗原文(只提醒、照舊寫入——「宣告不擋、跑時擋」)」
file: `scripts/lumos:13363`
file: `scripts/lumos:13458`

1. 第 3 輪把驗原文搬到 `with _vault_write_lock(...)` 之後,實際順序變成「寫入 → 印 ✓ 成功行(stdout)→ 印提醒(stderr)」;`_kill_add_warn` 的 docstring 仍寫「kill-add 寫入前」,`cmd_guard_kill_add` 的 docstring 仍寫「寫入前會驗這條配方的原文」。內部不一致。
2. 行為面已核對:rc 非 0(判重擋下、atomic 寫入失敗)都不印,判重擋下不印合 S1;寫入失敗時第 2 輪會先印提醒再印「擋下」、現在只印「擋下」,S1 只要求「照舊寫入時」印,不算退步。只要改 docstring。

## 有查、沒問題的(不列 finding)
- `rel` 與 `git ls-files -z` 輸出:`rel` 只會是 `ls-tree -z` 的鍵(別名也取自提交),兩邊同為 git 原樣位元組經 `os.fsdecode`,同形;`./`、`//`、`sub/../`、子資料夾、萬用字元對到多支(字面檔 `*.py` 在集合裡 → ok,guard kill 也全還原)、`:(icase)` 字面檔(還原到別的檔 → 跟檔案連結同類)、連結指向連結(`a.py→b.py→prod.py`,集合是 `{a.py}` → unrestorable)、precompose 開/關兩種寫法組合,都跟 `git checkout --` 的結果一致(除 F1 的狀態語意)。
- old/new 逐步對照:old 存在但 None → 數原文前判 malformed,guard kill `count(None)` TypeError ✓;old 沒寫、檔非空 → hits/drifted ✓;old 沒寫、空檔 → malformed/KeyError ✓;new 是空字串 → ok,guard kill 照常套 ✓;new 是 None 且原文 0 次 → hits/drifted ✓。
- `_kill_alias` 快取以 repo 頂為鍵、同一 ctx 內 `fold` 固定、不同 ctx 不共用:正確;同一 repo 的不同平台根共用同一份 OK。
- `_kill_fold_key` 在 APFS(不分大小寫)上:`ß/ss`、`ẞ/ß`、`ﬁ/fi`、`İ/i̇`、`Å/å`、`Ω/ω`、`ŉ/ʼn`、`ᾀ/ἀι` 實測跟檔案系統一致。
- file 型別檢查移到分平台、test 白名單之後:跟 guard kill 的順序一致(平台不在設定 → noplat 先於 file 型別)。

最高等級:major
