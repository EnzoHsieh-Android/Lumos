severity: minor

# 架構對齊審查 第 3 輪(只看 r2 之後的修正)

## 問 1 分層與依賴方向:有沒有跨層直呼?

沒有新的跨層直呼。新增的 `_nodehome_cat_sizes` / `_nodehome_cat_blobs_capped` 放在 `_nodehome_cat_blobs` 正上方,只呼叫同區的 `_nodehome_cat_blobs`;角色鏡頭 `_review_roles` 呼叫它,方向與 r2 已採用的一致(`_nodehome_cat_blobs` 本來就被 25759、26393 等 nodehome 以外的區段直呼)。`_dispatch_lens_role_text` 只呼叫 `_lens_range_ok` / `_lens_git` / `_lens_full_sha` / `_review_roles`,與原本內嵌的呼叫集合相同,只是抽出來。掛鉤只多一行 `_debug`,沒有新依賴。
對照:file: `scripts/lumos:23351`(_nodehome_cat_blobs)、file: `scripts/lumos:25759`(nodehome 區外的既有呼叫者)。

## 問 2 命名與錯誤處理:跟鄰居一樣嗎?

命名:`_nodehome_` 前綴給角色鏡頭用的批次讀取變體,函式家在 `_nodehome_cat_blobs` 隔壁,前綴與所在區一致(鄰居 `_json_at_ref` 在 lens 區則不帶前綴);沿用既有 helper 家族,不算不一致。

警告方式:兩處新增 `提醒:…` 印到 stderr,措辭與 `_stack_questions_config` 的警告一致;掛鉤 `_debug` 的用法與同檔其他呼叫(rc、放行等)一致。寬 `except Exception` 附「刻意」註解,與 scripts/lumos 內其他寬接處(例如 1053、1291 行)的「不因這段壞掉而整支中斷」慣例一致。`_json_at_ref` 加 BOM 與 RecursionError,與同輪 `_node_flavor_of` 的處理一致。

以下兩條是不一致:

## F1 新增的批次大小查詢少了鄰居的換行守衛、且整段複製 subprocess 樣板
severity: minor
blocking: 否
引句:「input=("\n".join(specs) + "\n").encode("utf-8", "surrogateescape"),」
說明:`_nodehome_cat_blobs` 先擋 `any("\n" in s_ for s_ in specs)` 回 None(路徑含換行時批次讀取表達不了),`_nodehome_cat_sizes` 沒有這道守衛,直接把 specs 用換行串起來丟給 `cat-file --batch-check`。含換行的路徑會讓輸出行數多於 specs,`heads[i]` 對位錯位,大小就配給錯的檔。同一段 try/except (OSError, TimeoutExpired)、returncode 檢查也是照抄而非共用。對照 file: `scripts/lumos:23351-23360`(換行守衛與同一段 run/except)。結構(批次一個行程)與鄰居同路,故只列 minor。

## F2 `_node_pkg_text` 用空字串當「在但讀不了」的哨兵,和鄰居「沒有/壞→None」的約定不同
severity: minor
blocking: 否
引句:「_NODE_FLAVOR_CACHE[key] = ""」
說明:同族的讀取函式(`_json_at_ref`、`_nodehome_cat_blobs`、`_stack_questions_config` 的讀取)都用 None/預設值加警告表示讀不了;這裡讀取器契約變成「文字/None/空字串」三態,靠下游剛好 `json.loads("")` 失敗來當判不出,且沒有留警告。是刻意且有測試(t_node_flavor_unreadable_nearest_package_json_is_none),但屬於新的約定。對照 file: `scripts/lumos:30850`(_json_at_ref 讀不了→None)、file: `scripts/lumos:20742`(_stack_questions_config 讀不了→預設加 warnings)。

## 問 3 第二種做法:有沒有引入專案裡原本沒有的做法?

沒有。大小上限包在既有 `_nodehome_cat_blobs` 外面(先 batch-check 再批次讀),刪掉了 r2 另起查法的 `_review_role_small_enough`(ls-tree 逐版本),正是收斂回既有批次讀取路徑;`--batch-check` 是同一個 git 內建批次機制,不算新做法。角色計算抽函式、測試改動都沿用既有寫法。

總結:不對齊共 2 條,其中 major 0 條。
