severity: minor

**總判**:〈做法〉每一點與 [S1]–[S6] 我逐條對過,沒有縮水,也沒有未實作。只有一條「規格內部不一致」的發現,下面第 1 條。

我用 4e87b682 的掛鉤檔載入 `bypass_reasons` 跑了約 55 條輸入,對照 spec 逐條判。實驗檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/`(`t.py`、`t2.py`)。注意不是每條都有跑過。

## 〈做法〉逐點裁定

| 項目 | 裁定 | 佐證 |
|---|---|---|
| 讀輸入與預篩(guard 外) | 已實作 | `entry`/`prefilter`:先解 JSON 取 `command`,`_PRE_WORDS` 三字樣加 `git`+`commit`+含 n 短旗標;預篩例外直接 return 0;`_guard(..., swallow=True)`;事件名 `pretooluse-bypass-ask-hook`;`decide` 內例外 `mark("error")` |
| 逾時預算 | 已實作 | `_outer_budget`、`_inner_budget` 逐字複本;`entry` 一進場就先叫一次 `_inner_budget()`;`MAX_GIT_CALLS=4`;`_GIT_STATE` 快取在 `bypass_reasons` 開頭重置 |
| 長度上限 | 已實作 | `len(command) > MAX_LEN` 走 `_literal`。實測 `git commit -m` 加 10 萬字單詞,耗時 0.001 秒,結果 `[]`(沒有三字樣,放行) |
| 一趟前處理 | 已實作 | `_Normalizer` 涵蓋:詞首 `#` 才算註解、`$(` 重開引號層、引號遮罩、ANSI 引號佔位、heredoc(`<<<` 與 `$((` 不算、多個 heredoc 依序配對、`<<-`、找不到結束字就停止剝) |
| 切詞與切段 | 已實作 | `_join_continuations`、`_replace_cmdsubs`、`_tokens`(shlex 加 `punctuation_chars`,換行當標點)、`_Sep` |
| 找 git 指令 | 已實作 | `_command` 取段裡第一個檔名是 `git` 的詞,`_parse_git` 跳全域選項;黏著的 `--git-dir=X` 不多吃;`--no-veri` 縮寫判法與 spec 一致 |
| 命中規則 | 已實作 | 實測:`--no-verif`、`-qn`、`-m x -n`、`--config-env`、`GIT_CONFIG_KEY_0=`、`config --unset`、`config set`、`export LUMOS_SKIP`、`env`/`timeout`/`sudo` 前綴下的 lumos,全部命中。`-mnote`、`-m -n`、`-F -n`、`--no-verified`、`--get`、只給鍵、`HUSKY=0`、`LUMOS_SKIP` 接 pytest、`lumos search LUMOS_SKIP_X=1` 全部放行 |
| 拋棄式判定 | 已實作 | 實測:`mktemp` 加 `$S/w` 放行;`mkdir`+`git init` 放行;`git -C /tmp` 放行;不存在的目錄、`--git-dir`、子殼層 `cd`、`&` 背景 `cd`、`pushd`、`cd /tmp/../Users`、`git -C ..` 全部照問;`remote add` 本機路徑放行,網址照問;`-c core.hooksPath` 接 rebase 照問;暫存目錄裡的 `LUMOS_SKIP` 接 lumos 照問;`_exempt` 分 sub 處理 |
| 字面判 | 已實作(見第 1 條) | 引號不成對時回 `["literal"]` |
| 命中輸出 | 已實作 | `_reason_text` 為三段式固定文字,不嵌入指令內容 |
| `decide`/`bypass_reasons`/`main` 分工 | 已實作 | 與 spec 一致 |
| `merge-claude-settings.py` | 已實作 | Bash matcher 加 `HOOK_BUDGET` 5,`_codex_entries` 對 `Bash` 的 PreToolUse 直接跳過 |
| `scripts/lumos` | 已實作 | `_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列、`_VENDORED_TREE_FILES`、`ANCHOR_FILES` 都加了。repo 的 `governance/anchor-baseline.json` 有簽(grep 命中 1 筆) |
| Systems 節點與 lifecycle 註記 | 已實作 | 在文件註冊組 patch 裡,我沒逐行核,只確認檔存在 |

## 條款 S1–S6

- **S1**:已實作。上表命中形狀都有實測。
- **S2**:已實作,只有一處需要說明。`git commit -m '--no-verify'`(引號裡的值剛好整串是 `--no-verify`)會命中。spec 對 `--no-verify` 沒有像 `-n` 那樣的吃值旗標排除,而且 shlex 切完詞後引號就不見了,所以符合 spec 字面。
- **S3**:已實作。放行與照問兩邊的形狀,抽測的都符合。
- **S4**:已實作,但字面判條件有內部不一致(第 1 條)。10 萬字單詞的耗時有量。其餘幾項我沒測:大量分段、大量未閉合 `<<EOF`、大量 `$(`、幾百段都要查 git、`--budget 5`。
- **S5**:已實作。patch 內容符合,但「列數 25」的測試與 `t_bypass_ask_registered` 不在 patch 裡,我沒驗。
- **S6**:屬人工條款,實作層無對應,不判。

## 發現

1. S4 的字面判條件與〈做法〉「字面判」不一致,實作照〈做法〉。
severity: minor
   blocking: 否
   引句:「當指令引號不成對或超過 2 萬字時,含 git、push 或 commit、`--no-veri` 三者 應問人,其他 應放行」
   - S4 要求同時有 git、push 或 commit、`--no-veri` 三者才問。
   - 〈做法〉寫的是「含 `git` 或 `lumos`,而且有 `--no-veri`、`hookspath`、`lumos_skip_` 任一個、或有 `commit` 加含 `n` 的短旗標」。實作 `_literal` 跟這句。
   - 實測:`git push --no-verify 'unclosed` 回 `['literal']`,兩種寫法都問。`git config core.hooksPath 'x` 這類寫法,只有〈做法〉會問。
   - 歸類:多做(相對 S4 字面),但有〈做法〉的 spec 對應,算 spec 內部矛盾。S4 應改成與〈做法〉同句。⚠ 請編排者裁定以哪句為準。

縮水+未實作共 0 條
