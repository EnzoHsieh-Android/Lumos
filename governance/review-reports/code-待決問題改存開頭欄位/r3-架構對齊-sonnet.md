severity: major

**問 1 分層與依賴方向**

不對齊 1:裝飾器成了鎖的第二種寫法。
- 專案原本的做法是 `cmd_*` 自己 `with _vault_write_lock(...)`,再叫 `_*_locked`。對照處有 `scripts/lumos:20119`(`cmd_set`)、`scripts/lumos:20414`(`cmd_append`)、`scripts/lumos:15500`(`cmd_guard_plan`)、`scripts/lumos:17349`。
- 修前的 `scripts/lumos` 沒有任何頂格裝飾器,這是第一個。
- 這輪還把本來符合慣例的 `_decision_cmd_locked` 拿掉,改成裝飾器。
- 結果同一個檔裡兩套並存:`cmd_set`、`cmd_append`、`cmd_guard_plan` 走舊寫法,決策四支、`cmd_guard_bind`、`cmd_guard_audit` 與 question 兩支走新寫法。
severity: major
blocking: 是
引句:「def _vault_locked(fn):」
對照:`scripts/lumos:20119`

不對齊 2:新寫了一支改名解析 `_pq_renames`,專案已有共用的。
- 它跑非 `-z` 的 `git diff --name-status`,再用 tab 手切。
- 共用的有 `_nodehome_changes`(`scripts/lumos:30233`,回傳 `(狀態, 舊, 新)`)、`_nodehome_name_status`(`scripts/lumos:30263`,回傳新→舊對照)和 `_fix_git_z`(`scripts/lumos:13235`,用在 `scripts/lumos:13712`)。這些都用 `-z`,路徑含 tab 或換行也不會切錯。
- 這跟上輪要收掉的 cat-file 手寫解析是同一類問題。cat-file 收掉了,改名解析卻又手寫一份。
severity: major
blocking: 是
引句:「def _pq_renames(rr, base, head):」
對照:`scripts/lumos:30233`

不對齊 3:`atomic_write_verify` 直接讀鎖層的私有狀態。
- 它自己 `any(_VAULT_LOCK_HELD.values())`,而 `_VAULT_LOCK_HELD`(`scripts/lumos:19943`)到目前只有 `_vault_write_lock` 本身讀寫(`scripts/lumos:20013`、`scripts/lumos:20036`)。
- 它也不比對是哪個筆記庫的鎖,拿著任何一把都放行。
- 依賴方向沒有倒過來(同檔、晚綁定),所以只列 minor。
severity: minor
blocking: 否
引句:「if not any(_VAULT_LOCK_HELD.values()):」
對照:`scripts/lumos:20013`

**問 2 命名與錯誤處理**

不對齊 4:`_vault_locked` 的語意跟鄰居相反,而且放的位置也不同。
- 鄰居 `_cmd_set_locked`(`scripts/lumos:20234`)、`_guard_plan_locked`(`scripts/lumos:15511`)、`_guard_kill_add_locked`(`scripts/lumos:17169`)的 `_locked` 都是「已經在鎖裡才被叫」。這裡的 `_vault_locked` 是「會去拿鎖」,讀的人容易以為被裝飾的函式不用再管鎖,或反過來。
- 同一個檔裡 `_locked` 後綴因此有兩個意思。
- 鎖相關的東西都在 `scripts/lumos:19993` 一帶,這個裝飾器卻放在 `scripts/lumos:602` 的 `Note` 類別旁。
- 錯誤處理這邊對得上:拿鎖逾時丟的 `RuntimeError`,在 `scripts/lumos:52798`、`scripts/lumos:52875` 和決策分派那段都有 `except (ValueError, RuntimeError...)` 接住。`atomic_write_verify` 的 `RuntimeError` 也跟同函式裡其他錯誤同型。
severity: minor
blocking: 否
引句:「讀—改—寫開頭欄位的指令都包這一層(第一個參數是 env):整段在同一個筆記庫的寫入鎖裡(可重入)。」
對照:`scripts/lumos:20234`

不對齊 5:決策連結的路徑索引是臨時的做法。
- 它把整庫路徑索引塞進節點快取 `cache["\0paths"]`,用一個魔術鍵跟「節點→決策」快取混在同一個 dict。
- 專案現有的是 `build_index` 和 `make_resolver`(`scripts/lumos:674`、`scripts/lumos:681`),結構是獨立的索引。
- 不分大小寫的整條路徑比對確實沒有現成的,所以只列 minor。短名那半已改用共用的 `by_stem`。
severity: minor
blocking: 否
引句:「cache["\0paths"] = idx」
對照:`scripts/lumos:681`

**問 3 第二種做法與上輪四項**

第二種做法就是上面的不對齊 1(裝飾器與 `with` 加 `_locked` 並存)和不對齊 2(改名解析另寫一份)。

上輪說要收掉的四項:
- **cat-file 解析**:收掉了。`_pq_git_read_many` 刪了,改用共用的 `_nodehome_cat_blobs`(`scripts/lumos:30384`)。
- **合併基準**:收掉了。改用共用的 `_range_base`(`scripts/lumos:42930`)。不過 `head` 是在 `_pq_push_remind` 裡用 `split("..",1)[1].lstrip(".")` 自己切的,別的 `_range_base` 呼叫端沒有這種做法,但這段很小,我沒另列一條。
- **決策連結解析**:只收掉一半。短名走共用 `by_stem`,帶路徑那半是新建的索引(不對齊 5)。
- **字元類別**:收掉了。`_pq_bad_char` 改用 `_PATH_SPECIAL_CATS`,寫法跟 `scripts/lumos:16531`、`scripts/lumos:14021`、`scripts/lumos:26148` 的現有用法一致。

不對齊共 5 條,其中 major 2 條
