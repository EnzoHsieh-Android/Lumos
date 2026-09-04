preflight-4: ran

# r1 收貨紀錄(code-codex-s0,standard 循序:單reviewer+架構對齊+外家 Codex)

## 前掃
- 代碼迴圈無四類前掃;機械面=pitfalls --diff manifest 0 條、patch 1557 行(<1800)、refcheck 三席行號全對(15/22/13)。

## 外家否決(Codex)6 條(4 major 2 minor,引句 6/6 錨定)
- #1 CODEX_HOME 被忽略 HIT:重現 `HOME=/tmp/h CODEX_HOME=/tmp/c merge --target codex` → hooks.json 落 ~/.codex。折入:`_codex_home()` 單一 helper(lumos)+合併器讀 CODEX_HOME,命令列用絕對路徑。
- #2 使用者同名 symlink 被換 HIT:折入 `_link_or_copy_shared` 對指向 lumos 以外的 symlink 跳過+warn。
- #3 先注入 AGENTS.md 後加 override → teardown 漏剝 HIT:折入 strip 掃三個候選檔。
- #4 merge-failed 仍 rc 0 HIT:折入 cmd_install 任一家 merge-failed → rc 2。
- #5 預算訊息暗示整鏈 HIT(minor):訊息改「只算 repo 根這一層;全域與子目錄另計」。
- #6 --target 值錯靜默退 claude HIT(minor):折入值域檢查 rc 2。
## 架構對齊 4 條(1 major 3 minor)+1 ⚠(引句正規化後 8/8 錨定)
- major「本機有沒有 Codex」兩套判準(dir OR PATH vs dir only)HIT:折入單一判準=家目錄在不在(`_codex_present`),三處共用;訊息改「還沒用過 codex」。
- minor:`_GLOBAL_HOOKS` 死別名→改為 sync/teardown 實際引用;docstring 補 registered-trust-unknown;Codex 列名改 `codex-<Claude 同名列>` 文法。⚠(結構是否必須一致)=編排者裁:改成同文法。
## 單reviewer 7 條(1 blocker 3 major 3 minor;引句 7/7、行號 15/15)
- F1 blocker `~/.codex` 是檔案 → NotADirectoryError HIT(席已在乾淨 worktree 重現):折入 sync 回 `home-not-dir` 態+訊息、teardown 跳過並警告;測試 t_codex_r1_reviewer_fixes。
- F2=外家 #4(同題,已折)。F3 `{"hooks": null}` 合併器炸 HIT:折入 schema 防護(hooks 非物件→空物件重建並警告;事件值非陣列/項目非物件/hooks 非陣列皆跳過),四種壞形態測試。
- F4 我方測試 `and False` 永真 HIT:改成釘具體數字+突變(把 trust-unknown 改 inactive 分母要多 1)。
- F5 Windows junction 誤判外方 HIT(minor,本機不能測 junction):折入 realpath==src 即我方,直接重建;Unix 以「重跑不印跳過」測。
- F6=外家 #6(已折)。F7 .bak 不清 HIT:折入 teardown 收 settings.json.bak / hooks.json.bak。
- 固定席鏡頭:派工詞尾端有「lumos 自動附加」段,席逐條判不影響(slim-install/uninstall 合約走另一機制 LUMOS-SLIM,grep 驗)。
