severity: major

**① 分層與依賴方向**

severity: major
blocking: 是(引入第二種做法:同一件事「這次推的是不是主線」在程式裡已有一套,spec 另寫一套,而且寫成專案已經改掉的那一版)
spec 段落:做法 2。
問題:專案已經有「推主線」的判定,就是 `_note_reread_mainline_names`。它拿兩個固定名 `main`、`master`,加上 `_push_mainlines` 的候選(用 `pushed_ref=None` 呼叫,所以不跳過被推的那條)實際指到的分支名,再看被推 ref 的分支名在不在這個集合裡。
- 這個函式的說明明寫「不看 pre-push 給的遠端名」。原因是代碼審 r4 資安 1:原本綁「`refs/remotes/<--push-remote>/<被推分支>` 是不是候選」,換一個指向同一網址的遠端名、或直接推網址,就整段不核對。
- spec 的判法正是那個被否決的舊形狀。引句如下。

引句:「被推的 ref 對應的那條(`refs/remotes/<--push-remote>/<被推分支>`)等於其中任一 → true。」

- 這個判法有兩個後果:
  - 用別的遠端名或網址推 main,對不到追蹤 ref,會得到 `pushed_mainline: false`,於是推主線被降成 light,全套被跳過。
  - 本機沒有 `refs/remotes/<遠端>/main` 時(例如第一次推主線,或候選被刪),候選清單空,同樣算 false。現有函式靠固定名 `main`/`master` 兜住這兩種情況,spec 沒有。
- spec 還說「`_push_mainlines` 會跳過被推的那條,所以要抽出共用的候選清單給兩邊用」。這個前提不必要:現有函式已經是用不跳過的方式取候選的。應該改成重用或泛化 `_note_reread_mainline_names`,不要再抽出第三份候選清單。
- 失敗方向也要對齊。現有函式「查候選失敗只剩固定名、不擋」,方向是往功能分支走。spec 這裡要的是失敗往主線(全套)走。兩個語意相反,所以不能原樣照搬。要重用就得明寫:固定名永遠算主線,git 失敗時照 spec 的 fail-closed。
佐證:`scripts/lumos:53729-53751`(`_note_reread_mainline_names` 與 r4 說明)、`scripts/lumos:53771-53776`(呼叫端只用分支名比)、`scripts/lumos:65263-65290`(`_push_mainlines` 的跳過邏輯,只在 `pushed_ref` 非 None 時起作用)。

**② 命名與錯誤處理**

severity: minor
blocking: 否(結構對,只是旗標語意沒對齊現有指令)
spec 段落:做法 2、做法 3。
問題:
- spec 說旗標「跟 `lumos push-range`、筆記內容閘同名同義」,但沒寫只給一個旗標時怎麼辦。現有慣例是兩個要一起給,只給一個就印「擋下:--push-remote 與 --pushed-ref 要一起給」並回 2。`push-range` 還明寫「值可以是空字串」。
- 掛鉤該帶 `"$_PP_REMOTE"`,spec 寫的 `"$1"` 是另一個名字。
- 另外,其他呼叫端都用 `pp_q` 做引號,spec 沒提。
佐證:`scripts/lumos:49220-49222`、`scripts/lumos:53490-53491`、`scripts/lumos:57799-57801`、`scripts/lumos:65572-65574`、`scripts/hooks/pre-push:166`、`scripts/hooks/pre-push:698-700`。

severity: minor
blocking: 否
spec 段落:做法 3、驗收條款 S2。
問題:掛鉤現在讀 pitfalls 欄位的方式是對 `pf_json` 做 `grep -q '"suite": *"docs"'`,`affected_keys` 則用 python 解析。spec 寫「`pushed_mainline` 明確是 false」,沒說用哪種讀法。照現有慣例,要寫成 `grep '"pushed_mainline": *false'`。「讀不懂」的邊界要由這個 grep 的字面決定,不要另寫 json 解析。
佐證:`scripts/hooks/pre-push:540-546`、`scripts/hooks/pre-push:572-576`。

**③ 第二種做法**

除了①那一條,其餘沒有:
- 把降級放進掛鉤現有的 light 分支、沿用 `_SUITE_LIGHT` 和 `affected_keys`/`autoloop_full` 的讀法,是沿用現有做法。
- 回退留著 `pushed_mainline` 欄位,不影響其他東西。
- CI 的 `push` 改成所有分支、concurrency 維持「push 以提交編號分組、不取消」,也跟 `ci.yml` 現有的群組慣例一致。標籤仍走 `security_tag`。
已讀,無其他 finding。
佐證:`.github/workflows/ci.yml:5-10`、`.github/workflows/ci.yml:19-21`。

**④ 落點**

severity: minor
blocking: 否
spec 段落:前言 `lands_in`、做法 2。
問題:`lands_in` 只列 `Systems/bound-tests-gate` 與 `Systems/pitfalls-code-loop`。但「推主線判定」這個機制目前記在筆記內容閘(回頭重讀)那邊,`pushed_mainline` 又要重用它。落點應該寫明新判定的家,並互相連結,不然會變成兩篇各說各的「什麼算推主線」。`ci.yml` 目前有多個家(安全證據閘、棧別提問表態閘、存量漂移守衛、筆記內容閘、bound-tests-gate),spec 動它時沒說要寫進哪一篇。
佐證:`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`、`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md`。

不對齊共 3 條,其中 major 1 條。

severity: major

總結:最嚴重等級為 major,會擋的問題共 1 條(做法 2 的主線判法沒有重用專案已經改掉舊形狀的現有判定,另立了一套綁遠端名的做法)。
