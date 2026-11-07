severity: minor

第四輪架構對齊席 F1 到 F4 都修好了,沒有新的 major。本席只讀了 `r5-repair.patch` 和 r4 報告,並用 `git grep` 對照 `adf857791` 的 repo。沒有重跑任何東西,也沒有改 repo。下面三條是結構對、細節沒對齊的小項。

## 第四輪 F1 到 F4 核對

- **F1(兩條路各寫一份整形)已修。**
  - 整形收成 `_impact_hunk_query`、`_impact_wants_head`、`_impact_mode_entry` 三個共用函式。
  - `cmd_impact_diff` 的 git diff 那條已改呼叫 `_impact_hunk_query`。
  - `_impact_diff_modes` 也改呼叫另外兩個。
  - 兩條路現在共用同一套整形。
- **F2(`_git_untrusted_c` 兩種呼叫形狀)已修。** 改成不收參數。`git grep` 在 `adf857791` 的 `scripts/lumos` 看到 7 處,全是無參呼叫:
  - `scripts/lumos:40231`
  - `scripts/lumos:40512`
  - `scripts/lumos:67373`
  - `scripts/lumos:70995`
  - `scripts/lumos:71073`
  - `scripts/lumos:71099`
  - `scripts/lumos:71139`
- **F3(種類註解不實)已改實。** 註解現在逐項列出各出口。
- **F4(兩份不信任清單)已修。** 註解不再寫「對齊」,守衛 `t_r4note_untrusted_two_lists` 改成雙向。

## ① 模組邊界

`_git_untrusted_c` 留在主程式,鉤子層不跟著用,結構是對的。鉤子層用自己的 `_hookshared._GIT_UNSAFE_CONFIG`(`scripts/hooks/claude/_hookshared.py:187`),主程式的註解和守衛也把這個差異寫清楚了。五支鉤子 `_trusted_lumos` 的 `_ok` 開頭拒相對路徑,是逐字複本加守衛,符合 `Systems/hook信任邊界` 的既有分流規則。

`unchecked_kind` 這輪沒動。`_hookevent.KINDS = ("ok", "timeout", "error")`(`scripts/hooks/claude/_hookevent.py:37`)的合約不受影響。

F1
引句:「def _lint_wt_toplevel(repo_root):」
引句:「t = _lint_wt_git(repo_root, "rev-parse", "--show-toplevel")」
- 「取 repo 根」現在在 lint-new 與影響分析各寫一份。
  - 一份是新的 `_lint_wt_toplevel`。
  - 另一份是 `_impact_wt_nofilter` 自己再呼叫 `rev-parse --show-toplevel`,並自己處理結尾換行,見 `scripts/lumos:67362`。
  - `_wt_changed_nofilter` 內部還有第三份,但那份因為是鉤子逐字複本,不能匯入,屬於既有慣例。
- `_impact_wt_nofilter` 沒用 `_lint_wt_toplevel`。
  - 兩者的失敗語意不同:前者失敗回 None,後者失敗退回原路徑。
  - 日後改其中一邊,另一邊不會跟著改。
- 對照:`scripts/lumos:40239`。
- 結構沒有跨層,所以只標小項。
severity: minor
blocking: 否

## ② 命名與錯誤處理

- 沿用既有前綴:`_impact_*`、`_lint_wt_*`、`_IMPACT_WT_READ_TOTAL`。
- 失敗路徑也一致:`None` 表示沒能算,`query_path_only` 表示退回只用路徑。

F2
引句:「return given("-C", top, *a, data=data)」
- `_wt_changed_nofilter` 把參數 `run` 在函式中途用巢狀 `def run` 重綁,舊的存成 `given`。
- 函式內的 `ok` 是閉包,取用名字 `run` 時看到的是當下綁定:
  - 前兩次 `rev-parse` 走呼叫端原本的 `run`。
  - 之後所有呼叫走加了 `-C <根>` 的 `run`。
- 同一個名字前後指向兩種函式,錯誤處理的行為取決於呼叫順序。
- 在 `scripts/lumos` 與 `check-graph-sync.py` 兩份逐字複本裡都是這樣。
- 這不是結構問題,是命名與可讀性。換個名字(例如 `in_top`)就沒有這個陷阱。
- 對照:`scripts/hooks/claude/check-graph-sync.py:344` 一帶。
severity: minor
blocking: 否

## ③ 第二種做法

- **大小上限**:
  - 兩處都重用既有的 `_nodehome_cat_sizes` 與 `_nodehome_cat_blobs_capped`,單支上限用 `_CODELOOP_BOOKKEEPING_HEAD_CAP`,沒另起讀法。
  - 讀取方式沒有第二套,下面 F3 只談總量記帳。
- **暫存清掃**:這輪沒有新增,沒有另起一套。
- **改檔前推播的入口**:這輪沒碰,`_impact_missing` 仍是唯一入口。

F3
引句:「_IMPACT_WT_READ_TOTAL = 8 * 1024 * 1024」
引句:「head_mode[os.fsdecode(path)] = fl[0].decode("ascii", "replace")」
- **總量記帳有兩種做法並存。**
  - 既有 `_nodehome_cat_blobs_capped` 已有 `max_total_bytes` 參數。
  - 同一個函式裡,「補看首行」那段用它(傳 `max_total_bytes=cap`)。
  - 主讀取那段改成自己用 `used + add` 累計,另起新常數 `_IMPACT_WT_READ_TOTAL`。
  - 自記帳有理由:要把工作樹那一版的大小也算進去,既有參數只算 HEAD 側宣告大小。
  - 但這等於同一個函式內有兩種總量上限寫法,且沒有說明為什麼不擴充既有參數。
- **HEAD 模式表自己再解析一次。**
  - 為了刪除檔取 HEAD 模式,`_impact_wt_nofilter` 另跑 `ls-tree -r -z --full-tree HEAD` 並自己拆欄位。
  - `_wt_changed_nofilter` 內部已經解析過同一份輸出(`head` 字典),只是沒回傳。
  - 主程式裡已有的 `ls-tree` 解析點:`scripts/lumos:25692`、`scripts/lumos:46928`。
- 對照:`scripts/lumos:67382`。
- 兩處都是在既有結構內多一份寫法,不是跨層,所以標小項。
severity: minor
blocking: 否

不對齊共 3 條,其中會擋的 0 條
