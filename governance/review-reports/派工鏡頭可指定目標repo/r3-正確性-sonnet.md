severity: major

## 已讀,無 finding 的節

- 做法 1 的 `<提交>:<路徑>` 判定和工作樹路徑不會撞名。相對路徑要以 7 碼以上的純十六進位目錄名開頭、後面緊接冒號,才會被誤判成提交寫法,docs 底下實務上不會有。
- 路徑檢查擋掉 `..` 就夠了。實測 `rev:docs/x-knowledge/./Projects/p.md` 與 `rev:docs//...` 都找不到;`rev:./docs/...` 找得到,但 `-C` 的目錄就是 repo 根,所以等同 `docs/...`。符號連結目錄不會被穿過,子模組路徑 `show` 也只回找不到。
- `rev-parse`、`cat-file`、`show` 用 `rev:path` 寫法不讀 index。實測我在 `.gitattributes` 設了 `diff=evil`,`.git/config` 設了 textconv 會 `touch` 檔,`git show <sha>:<path>` 沒有執行它。計劃「不跑過濾器」的說法成立。
- 子模組(160000)用 `cat-file -e` 判是不存在(rc=1),`cat-file -s` 報錯,會落到 `spec_missing`。

## Findings

severity: major
blocking: 是 — 計劃自己的 S1 主情境(新模組計劃)照字面實作會得到零個固定席節點,輸出還寫「找得到」,審查席被誤導
引句:「計劃提到的程式檔「存不存在」改用 `cat-file -e <提交>:<檔>` 判(檔在那個提交裡存在才算),impact 照現在在會談 repo 的主線算。」
問題:存在判斷用提交,牽連計算卻用會談 repo 現況,兩邊對不上。計劃寫在分支上,常常就是為了新增或改名檔案。那種檔在提交裡存在,`cat-file -e` 通過,就被列進 `code_files`。但 `impact --file` 對會談 repo 沒有這支檔、也沒有任何筆記 `about_code` 認領它的情形,只會回空結果。反方向:檔在會談 HEAD 還在、提交裡已刪或改名,會被 `cat-file -e` 丟掉,主線上有的家和事故節點反而沒附。
失敗情境:計劃寫「新增 `scripts/foo_new.py`」,提交 C 含此檔。派工詞寫 `LUMOS-SPEC: C:docs/x-knowledge/Projects/p.md`,存在判斷通過,輸出「計劃提到並找得到的程式檔:scripts/foo_new.py」。我實測 `lumos impact --file scripts/nonexist_new.py --repo <repo> --json` 回 `{"direct":[],"indirect":[],"incidents":[]}`,rc=0,所以沒有任何節點。審查席以為「已查過、沒牽連」,實際是根本沒算。
佐證:file: `scripts/lumos:49040-49076`(`code_files` 以 `p.is_file()` 判,impact 子行程以 `--repo root` 跑)

severity: minor
blocking: 否 — 跟現在行為無關,只是可能讀錯東西或誤判
引句:「再 `show <提交>:<路徑>` 讀計劃內容(`cat-file -s` 先查大小,超過 1MB 不讀」
問題:路徑只做字串檢查,沒要求結果是檔案(blob)。實測:
- 路徑指到目錄時 `git show` 會印 tree 清單,`cat-file -s` 回 67,`cat-file -e <提交>:scripts/hooks` rc=0。tree 清單會被當成計劃文字掃描。
- 路徑指到符號連結物件(120000)時,`show` 印的是連結目標字串 `../../../../etc/hosts`,不會跟隨。工作樹那條路會拒絕這類連結,提交那條路卻把目標字串當計劃內容。
- 程式檔那邊同理:計劃文字提到 `scripts/hooks`(沒有副檔名的目錄),`cat-file -e` 為真,目錄被當程式檔列出,也被丟去跑 `impact --file`。工作樹那條路用 `is_file()`,不會有這個差別。
- 超過 1MB 沒有對應失敗代碼(四個代碼都不貼切)。
修法:先 `rev-parse <提交>:<路徑>` 取 oid,再用 `ls-tree` 看 mode 是 100644/100755,或 `cat-file -t` 要求 blob,最後 `cat-file blob <oid>`。同時補一個「過大」代碼,或明講併入 `spec_missing`。
佐證:file: `scripts/lumos:49040-49048`(工作樹那條用 `is_file()` 與 `resolve()` 擋連結)

severity: minor
blocking: 否 — 單人威脅模型下影響小,但「提交編號」這個名字不保證指到那個提交
引句:「(`<提交>` 是 7–40 碼十六進位,冒號後是 repo 根起算的相對路徑、不以 `/` 開頭)」
問題:
- 短編號會被同名的分支或標籤搶走。實測我對提交 C1 的前 7 碼建了同名分支,`rev-parse --verify --quiet <7碼>^{commit}` 回的是 C2。改成同名標籤也一樣。git 對不足 40 碼的字串先當 ref 名解析,所以派工詞寫的短編號可以被導到另一個提交,計劃的 `rev-parse` 通過、內容卻是別份。
- 正規式只收小寫。我測過大寫十六進位 git 也認(rc=0),但這個寫法會被當成工作樹路徑,得到 `spec_missing` 加上「先提交、改寫提交編號」的繞法,而使用者其實已經寫了提交編號。
- 短編號在大 repo 容易撞到兩個提交,git 會報 ambiguous。計劃沒說這種情況歸哪個代碼,照字面會被標成 `spec_rev_missing`。
- 41–64 碼(SHA-256 repo 的完整編號)不在 7–40 之內。
- `_lens_git` 逾時回傳 None,計劃也沒指定這種情況對應哪個代碼,容易被併成 `spec_rev_missing`。
修法:取到完整 sha 後要求它以輸入字串為前綴,不是就拒絕;正規式用不分大小寫並收到 64 碼;ambiguous 與逾時各自給代碼或併入既有代碼並寫明。
佐證:file: `scripts/lumos:47386`(`_lens_git` 逾時回 None)

severity: minor
blocking: 否 — 成立,但標示或內容可能與實際不符
引句:「只在那個分支上新開、主線還沒有的節點,列名並標「主線還沒有這篇」,不當成錯誤。」
問題:
- 現有 `linked` 只收 `(root/vault/…).is_file()` 的節點,不存在的會被靜默丟掉。改成「不存在也列名」之後,錯字連結(`[[Systems/打錯]]`)也會被標成「主線還沒有這篇」。要區分「分支新開」和「連結寫錯」,得拿提交去查那個節點是否存在,計劃沒寫。
- 這個「主線」其實是會談工作樹,不是主線。會談在舊分支或別的分支時標籤會說錯。
- 節點內容讀自會談工作樹,不是計劃所在的提交,所以在計劃提交裡已被改過的 Systems 節點,審查席看到的是舊版。
- `_nodehome_landing_sizes` 同樣讀工作樹,`lands_in` 新開的節點會顯示「還不存在(要新開)」。這句對新節點是對的,但分支上已經存在的節點會被誤說成「要新開」。
- 計劃要求「路徑要在 `docs/*-knowledge/` 底下」,但現有程式 `vault_rel` 取的是工作樹 `slugs[0]`。多個 `*-knowledge` 或提交裡的 slug 不同時,連結節點、落點、架構段會全用錯 vault。路徑檢查應該是「等於 `vault_rel`」。
- 計劃還說這些檢查「跟工作樹那條路相同」,實際工作樹那條路只檢查在 repo 內,沒有 `docs/*-knowledge/` 限制,也沒有 1MB 上限(`read_text` 無上限)。照字面可能讓人去改工作樹路徑的行為,違反 S3 的「與現在相同」。
佐證:file: `scripts/lumos:49049-49056`(`linked` 與 `vault_rel` 取法)、`scripts/lumos:48958-48980`

severity: minor
blocking: 否 — 不影響已有路徑,但計劃自己的主情境下繞法不會出現
引句:「計劃在會談目錄找不到(`spec_missing`)而值不是提交編號寫法時,說明行加一條繞法」
問題:使用者最自然的寫法,是把另一個工作樹裡的計劃寫成絕對路徑。這在現有程式會走 `sp.resolve().relative_to(root.resolve())` 失敗,印「不在這個 repo 裡」,對應的是 `spec_outside_repo`,不是 `spec_missing`。照計劃字面,繞法只掛在 `spec_missing` 上,所以最常見的情況反而看不到「先提交、改寫提交編號」。
另外,`FAIL_NOTE` 的文字是「範圍 {what} 在會談專案…」,`_SAFE_RANGE_RE` 對計劃路徑一定不符,會顯示成 `<範圍>`,整句都是代碼審範圍的措辭。計劃只說拿掉條件,沒說另寫一句計劃版,這次(r3)又沒了 r2 的計劃版措辭。
失敗代碼讓工作樹路徑也印之後,舊行為不會壞:舊 stdout 為空才觸發的「拿掉選配旗標重叫」不會誤觸,`lock_status` 解析也只在 `spawn_error` 或 `lock_error` 為真時才有作用。這部分我讀程式確認過。
佐證:file: `scripts/hooks/claude/dispatch-lens-hook.py:250-262`(`_fail_note` 只在 `rng` 為真時回說明、`what` 用範圍專用正規式)、`scripts/lumos:49018-49025`

severity: minor
blocking: 否 — 設計自相矛盾,實作時會出現兩份判斷
引句:「掛鉤不改標記的找法(`find_spec_marker` 照舊),只把值原樣交給 lumos;掛鉤自己不解析、不跑 git。」
問題:做法 5 與 S6 要求掛鉤事件 note 記「用了提交編號寫法」以及 `spec_rev <失敗代碼>`。掛鉤要知道值是不是提交編號寫法,得自己解析一次,或讓 lumos 在 JSON 多回一個欄位。計劃兩者都沒寫。照字面實作會在掛鉤複寫一份十六進位正規式,和 lumos 那份漂開(例如大小寫、7–40 碼的範圍不一致)。建議由 lumos 在 JSON 回 `spec_rev: true` 之類的欄位,掛鉤只讀不判。
佐證:file: `scripts/hooks/claude/dispatch-lens-hook.py:27`(`SPEC_RE` 只切 `\S+`)

## 總結

最高等級 major,共 6 條,其中 blocking 1 條(程式檔存在用提交判、牽連計算卻用主線算,新增檔會得到零節點卻寫成「找得到」)。

臨時目錄 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/lr-r3-正確性/` 還在,下一步我會刪掉。
