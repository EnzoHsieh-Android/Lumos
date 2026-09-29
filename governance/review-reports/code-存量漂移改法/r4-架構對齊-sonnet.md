severity: major

## 一問 分層與依賴方向
對齊。`_sh_quote` 從檔中(原 codeloop 區段)搬到檔頭 `file: `scripts/lumos:401``,在 `_drift_sh`(`scripts/lumos:27619`)、`_codeloop_print_dirty_bookkeeping` 之前定義,依賴方向由下往上,沒有新增跨層直呼。`_plan_for_loop` 改呼 `_nfc_child`(`scripts/lumos:391`)是把手刻的 iterdir+NFC 字典換成既有 helper,是往既有做法收斂。drift 區呼叫 `_nodehome_git`/`_nodehome_split_z`(`scripts/lumos:23610`、`:23623`)與既有 `_guard_raw_git_path`(`scripts/lumos:12192`)同層取用,方向一致。唯一分層疑點在第三問 F1。

## 二問 命名與錯誤處理
大致對齊:`_drift_git_*` 沿用 drift 區的 `_drift_` 前綴;c4 對 `_yaml_quote` 的 ValueError 轉成 `(None, str(ex))` 回傳,與 drift fix 其他步驟「回 (結果, 錯誤字串)」的慣例一致。不對齊處見 F2(引號策略)、F3(./ 處理)。

## 三問 第二種做法
- c4 寫整項:沿用既有 `_yaml_quote`(`scripts/lumos:14677`),不是自造引號;但略過既有「先問 `_yaml_plain_ok`,可裸寫才裸寫」的入口,見 F2。
- `_drift_git_paths` 與 `_guard_raw_git_path` 確為同一件事的第二份實作,見 F1。
- `Env.find` 剝 ./ 與 `_drift_fix_target` 各剝一次,見 F3。

## F1 新增 _drift_git_paths,與既有 _guard_raw_git_path 是同一查詢的第二份實作
severity: major
blocking: 是
引句:「raw = _nodehome_git(root, "ls-files", "-z")」
file: `scripts/lumos:12192`(既有 `_guard_raw_git_path`:同樣 `_nodehome_git(root,"ls-files","-z")`、`nfc(x)==nfc(repo_rel)`、回原樣路徑,失敗回 None)
file: `scripts/lumos:28151`(新 `_drift_git_paths`,逐行相同的取得與比對,只差「回全部命中」而不是「回第一個」)
1. 重現:`grep -n '"ls-files", "-z"' scripts/lumos` 在 12192 附近與 28151 附近各出一份「列 ls-files、NFC 比對、回原樣路徑」。
2. 新函式把「取第一個」改成「回清單」以偵測兩種 Unicode 拼法並存,需求正當,但做法是複製一份而非擴充既有函式;`_guard_raw_git_path` 仍被 `_guard_pass_commit_date`(`scripts/lumos:12209`)使用,現在同一專案有兩支「repo 相對路徑 → git 原樣路徑」,將來規則(例如失敗語意)只改一支就會分岔。
3. 順帶:兩支失敗語意不同(既有:找不到與 git 失敗都是 None;新:git 失敗 None、找不到 `[]`),呼叫端 `if not ps` 把兩者併成同一句錯誤,`_drift_git_cmd` 又在 `[]` 時退回 repo_rel,同檔兩支對「找不到」的回傳不一致。
4. 較貼近既有做法:把 `_guard_raw_git_path` 改成 `_drift_git_paths` 的薄包裝(或反過來抽共用的 `_git_raw_paths`),而非並存。⚠ 若 Enzo 認為 guard 區不宜被 drift 區依賴,則應把共用函式放到 `_nodehome_*` 那一層。

## F2 c4 一律加引號,沒走既有 fmt_list_item 的「能裸寫就裸寫」判斷
severity: minor
blocking: 否
引句:「quoted = _yaml_quote(new, "--new")          # 既有的安全寫法」
file: `scripts/lumos:14700`(既有 `fmt_list_item`:`v if _yaml_plain_ok(v) else _yaml_quote(v, "清單項")`;`fmt_scalar` `:14698`、決策內容 `:15589` 同一寫法)
1. 既有三處寫開頭欄位都先問 `_yaml_plain_ok`,可裸寫的值不加引號;c4 直接呼叫底層 `_yaml_quote`,新值恆被包成 `"..."`。
2. 場景:`lumos drift fix … --kind c4 --old X --new 已提交` 寫進去是 `  - "已提交"`,而同一欄位用 `lumos append` 寫同一個值會是 `  - 已提交`,同一 valid_under 內會混出兩種外觀,且指紋/差異預覽因此多出引號。
3. 結構上是沿用 `_yaml_quote` 而非新造,所以不算第二種做法;但更接近既有的是呼叫 `fmt_list_item(new)`(它已含 `_yaml_quote` 與 ValueError,且 what 參數是「清單項」)。⚠ 若刻意恆加引號是為了讓讀回值恆等於 --new(程式後面有 `after[diff[0]] != new` 檢查),則要在註解說明為何不走 `fmt_list_item`。

## F3 「./ 開頭是明確路徑」在兩處各實作一次,語意不同
severity: minor
blocking: 否
引句:「a = a[2:] if a.startswith("./") else a」
file: `scripts/lumos:700`(`Env.find`:剝掉 ./ 後仍會落到 `by_stem` 以檔名猜、取第一個)
file: `scripts/lumos:27738`(`_drift_fix_target`:./ 開頭只認那一條路徑、不退回檔名猜)
1. 兩處都在處理同一個由 `_drift_sh(node=True)` 印出的 `./-x` 形式,但 `Env.find("./-x")` 找不到路徑時會拿 `-x` 當 stem 猜,`_drift_fix_target` 則明確不猜;同一個前綴在同一支檔裡有兩種解讀。
2. 影響有限(drift fix 走自己的 target,不呼叫 find),所以只列 minor;但這是「同一約定兩份剝法」,計劃/家節點只寫「一般查找都把 ./ 開頭當明確路徑」,而 `Env.find` 實際並沒有「只認路徑」。⚠ 家節點的敘述與 `Env.find` 行為不完全相符,我未能構造出實際損害的輸入。

## 結論
不對齊共 3 條,其中 major 1 條
最高等級:major
