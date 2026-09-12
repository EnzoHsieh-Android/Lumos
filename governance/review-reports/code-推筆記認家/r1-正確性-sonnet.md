severity: blocker

# 代碼審——正確性鏡頭:推筆記認家(r1)

## finding 1:regen-no-home 提交前擋沒有比對 home-status,planned 節點也會被誤擋

`_nodehome_evaluate` 裡新加的 S11 判定完全沒檢查 `n["status"] in _NODEHOME_HOME_STATUSES`(該常數只有 `doing/done/stale` 三種)。用最小重現構造一個 status=`planned` 的既有節點(不是 home status,resp 早已合格、文字這次完全沒改),這次改動只是補上 `regen` 欄位——會被判成 `regen-no-home` 擋下,即使它本來就不算「家」、也早就交代過負責範圍。同一支函式裡緊鄰的 `becomes_home`/`new-node-resp` 規則都有比對 home-status,doctor 側對應的健檢版本(`_nodehome_ledger`)也明確先過濾 `n["status"] in _NODEHOME_HOME_STATUSES` 才判定同一件事——只有這條提交前擋漏了。
最小重現(在 repo 內跑,直接呼叫 `_nodehome_evaluate`,不需要真的 git 操作):建構 B/N 兩邊各一個 status=planned、resp="這篇只整理跨模組脈絡,不管任何程式檔"(未變動)的節點,N 版多蓋一個 `regen` 欄位,`_nodehome_evaluate` 回傳 `blocks: [('regen-no-home', 'Systems/foo.md')]`——本來不該被擋的提交被擋下。
引句:「if n["regen"] and not (b and b.get("regen")) and cnt_now == 0 and not resp_missing:」
file: `scripts/lumos:18369`
file: `scripts/lumos:17729`(`_NODEHOME_HOME_STATUSES = ("doing", "done", "stale")`)
file: `scripts/lumos:18639`(doctor 側同一件事有 `if n["status"] in _NODEHOME_HOME_STATUSES:` 把關,提交前這條沒有)
severity: blocker
blocking: 是

## finding 2:節點同時是事故又是家時,派工鏡頭把「事故」標籤蓋掉

`_lens_kind_of` 只要 `v.get("home")` 為真就直接回「家」,完全不管原本 `kind` 是不是 `"incident"`。`cmd_dispatch_lens` 用這個函式決定 `listed[].kind`,而 `_lens_render_listed` 印出的那一行只靠這個欄位標記(`[事故]`/`[家]`),沒有第二個欄位保留事故資訊。整個工具鏈其他地方(`cmd_impact`/`cmd_impact_diff` 的排序 key)都堅持「事故永遠最前」是最高優先級的安全訊號,這裡卻讓「家」的顯示標籤直接蓋掉「事故」,審查員讀到派工鏡頭時會看到 `[家]` 而看不到這篇曾出過事故。
最小重現:直接呼叫 `_lens_kind_of({"kind": "incident", "home": True, ...})`,回傳 `"家"`(`_LENS_KIND["home"]`),不是 `"事故"`(`_LENS_KIND["incident"]`)。
引句:「return _LENS_KIND["home"]」
file: `scripts/lumos:22403`(`def _lens_kind_of(v):`)
file: `scripts/lumos:21908`(`results.append({"node": x["node"], "kind": "incident", ...})`——incident 節點本來就會混進同一個 `results`/`pins` 池,跟家標記共用同一顆物件)
severity: major
blocking: 是

## finding 3:全文完整路徑掃描用 ASCII 字元類,CJK/特殊字元路徑的「正文寫出完整路徑」永遠判不確認

新增的 `_node_code_ref_tokens_all` 為了認「反引號外、正文直接寫出完整路徑」多掃一次全文,但 `_PATH_IN_TEXT_RE` 的字元類只有 `[A-Za-z0-9_.@+\-]`,不含中日韓字元、空白或其他常見檔名字元。設計文件與同一批新增的測試都只驗證過 ASCII 路徑(`src/cart.py`),沒有覆蓋消費專案裡常見的 CJK 檔名。若目標程式檔路徑含非 ASCII 字元(這套工具鏈本身就服務大量 CJK 專案),正文用白話寫出完整路徑也抓不到,`_home_confirmed` 會回 False,跟文件承諾的「正文(沒有反引號)寫出完整路徑 → 確認」矛盾。
最小重現:`top_dirs={'scripts'}`、`all_paths=['scripts/腳本.py']`、正文「這篇的正文完整寫出 scripts/腳本.py 這個路徑,沒有用反引號。」,呼叫 `_home_confirmed(text, 'scripts/腳本.py', top_dirs, all_paths)` 回傳 `False`。
引句:「_PATH_IN_TEXT_RE = re.compile(r"[A-Za-z0-9_.@+\-]+(?:/[A-Za-z0-9_.@+\-]+)+")」
file: `scripts/lumos:21472`
severity: major
blocking: 是

## finding 4:S15「管了卻沒提到檔名」提醒沒過濾節點類型與 home-status,project 型計劃筆記也會誤觸發

`_nodehome_evaluate` 尾端新增的 S15 迴圈(針對這次新掛進 about_code 卻沒提到檔名的節點)是 `for rel in sorted(ownN):`,`ownN` 來自 `_home_map_from_notes` 的 `own` 字典,對每一種 type 都會建(不限 `system`)。這段完全沒有比對 `N.notes[rel]["type"] == "system"` 或 home-status,跟同一批 diff 裡 doctor 端的等價判定(先過濾 `type != "system"` 再過濾 `status in _NODEHOME_HOME_STATUSES`)不一致。結果是:一篇 `type: project` 的計劃筆記(這種筆記從定義上永遠不會被算進 `homes`、永遠不會被「推筆記認家」推出去)這次多掛了一個 about_code、正文沒提到檔名,一樣會被判定成 `home-unmentioned`,印出「改這支檔的時候會把這篇推到看的人眼前」——但這句話對 project 型筆記是假的,它從機制上就不會被推。
最小重現:B/N 各一個 `type: project, status: doing` 的節點,N 版 about_code 多了 `src/pay.py`、正文完全沒提到這個檔名,`_nodehome_evaluate` 回傳 `reminders: [('home-unmentioned', ('Projects/plan.md', 'src/pay.py'))]`。
引句:「gained = ownN[rel] - ownB.get(route_src.get(rel, rel), set())」
file: `scripts/lumos:18451`(迴圈起點,無 type/status 過濾)
file: `scripts/lumos:18636`(doctor 側同一件事先 `if n["type"] != "system": continue` 再 `if n["status"] in _NODEHOME_HOME_STATUSES:`)
severity: minor
blocking: 否
