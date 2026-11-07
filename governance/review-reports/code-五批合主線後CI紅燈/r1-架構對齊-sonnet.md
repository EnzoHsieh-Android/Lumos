severity: minor

我只看 `r1-snapshot.patch` 與 repo 內相關程式碼,沒有重跑測試。沒有第二種做法,也沒有跨層直呼,兩條重點都沒有 major。

**1. 兩處改呼叫 `_under_root`:符合,不是問題。**
- 兩處原本都是「`is_absolute()` 判斷後接 `Path(repo_root)`」的手寫拼法,正好是 `_under_root` 說明禁止散落的形狀。說明裡寫著 `t_nogo_shared_helpers_used` 會用語法樹把這種寫法限制在 `_under_root` 內。
- 傳參的用法跟其他呼叫端一致。
- 行為等價:這兩處的 `repo_root` 都不是 None,`_under_root` 的 None 分支不會被走到。
- file: `scripts/lumos:16759`(定義)、`scripts/lumos:40541`、`scripts/lumos:41165`。

**2. 測試允許名單加 `_lint_placeholder_words`:符合,但註解少了出處。**
- `_lint_placeholder_words` 確實存在(`scripts/lumos:42491`),且被 `_lint_cmd_with_files` 與參數清單版呼叫(`scripts/lumos:42486`、`scripts/lumos:41286`)。它只算詞、不做替換,放進名單的理由成立,不是第二條替換路徑。
- 缺口:同一名單的其他項,註解都帶日期與 `[[Projects/…]]` 連結。新項只寫了「回合結束檢查代碼審 r2 架構對齊 F1」,沒日期也沒計劃連結。
- 引句:「_lint_placeholder_words」那行註解 `佔位符 → 詞的共用核心(回合結束檢查代碼審 r2 架構對齊 F1`
severity: minor
- blocking: 否
- file: `scripts/test_lumos.py:17143`(`ALLOWED` 那一帶)

**3. 拆測試:大致照專案慣例。**
- 三支新名字 `t_prepush_newbranch_merged_tip`、`t_prepush_newbranch_tip_on_main`、`t_prepush_newbranch_range_fallback` 互不為前綴。
- 它們與原名 `t_prepush_new_branch_block_range` 也不互為前綴(一個是 `new_branch_`,一個是 `newbranch_`)。
- docstring 都有 `[新分支首推 Sx]` 與「翻紅釘」。
- 計劃條款:S1、S2 留在原測試;S3 到 S6 改綁新測試;`存量漂移守衛` 那條 WHY 也補上新名字。
- 缺口:原名用 `new_branch`、新名用 `newbranch`,同一族兩種拼法,只能靠 `-k` 子字串各別挑,不能一次挑整族。
- 引句:「t_prepush_newbranch_range_fallback」
severity: minor
- blocking: 否
- file: `scripts/test_lumos.py:30096`、`scripts/test_lumos.py:30121`

這份 diff 沒有第二種做法或跨層直呼,只有 2 條 minor:名單註解缺日期與計劃連結,拆出的測試名拼法跟原名不一致。
