severity: minor

審查在修後固定版本 40f871bf、修前 a4d42fea 上做完,兩個 clone 都在 `/tmp/lumos-seat-work/code-舊句兩道轉擋/正確性4-sonnet/`。原工作目錄沒動過。修補本身(讀端路徑守衛、兄弟閘接 RecursionError、`_sh_quote`、補強測試、筆記說法)都成立,沒有 major。另外有三條 minor:兩條是同族但沒掃到的原有漏查,一條是測試沒守到的分支。

## F1 同族的 note-verdicts 工作目錄讀端沒有資料夾守衛(原有漏查)
severity: minor
blocking: 否

引句:「資料夾從 repo 根往下任一層(含上層的 governance)是符號連結」

- **位置**:`scripts/lumos:33667-33683`(`_note_audit_load_verdicts`,`where is None` 那一支)。它只寫 `if not d.is_dir()`,完全不看資料夾是不是符號連結,也不看是不是指到 repo 外;單檔才有 `is_symlink()`。
- **失敗場景**:`governance/note-verdicts` 本身是指到 repo 外的連結,外面放一份合法判定檔。工作目錄讀端會把它當成已判定。`note-audit prepare`(`scripts/lumos:34155`)會因此回「沒有待審的筆記行」,跳過派判定者。
- **影響有限**:`check` 只認已提交的樹,最後仍會擋。所以是流程誤導,不是閘被繞過。
- **歸因:有證據的原有漏查。**
  - 命令:`python3.14 scr/nlink.py <clone>`,各跑修前、修後。
  - 結果:兩版都讀到 `['20261009T000000Z-0123…json']`。同一情境下 `_note_reread_wt_verdicts` 修前讀到、修後讀到 `[]`。
  - 該函式不在修補差異內。

## F2 巢狀太深的判定檔讓 note-audit check 噴堆疊(原有漏查)
severity: minor
blocking: 否

引句:「兄弟閘各只有一處解析,照專案多處的 except (ValueError, RecursionError)」

- **位置**:`scripts/lumos:33650-33656`(`_note_audit_parse_verdict`)只接 `(ValueError, UnicodeDecodeError)`。
- **重現**:`governance/note-verdicts/` 放一份 13 萬層陣列的合法判定檔並提交,跑 `lumos note-audit check --diff <起點>..HEAD`,印出 `RecursionError: Stack overflow` 的堆疊(rc1)。預期是「判定檔壞掉了,當作不存在」那句提醒。腳本是 `scr/deepverdict.py`。
- **不影響推送**:這道閘沒接線。`scripts/hooks/pre-push` 與 `.github/workflows/ci.yml` 只呼叫 `reread-check`。`doctor` 外層有 `except Exception`,不會崩。所以只影響手動跑。
- **歸因:有證據的原有漏查。** 該函式不在修補差異內,修前修後同樣崩。

## F3 工作目錄紀錄讀端的 OSError 退路沒有測試守(原有漏查)
severity: minor
blocking: 否

引句:「ok = _repo_path_unsafe(root, _NOTE_REREAD_VERDICT_DIR, dirs=True) is None and d.is_dir()」

- **產品行為對**:把紀錄資料夾 `chmod 000` 後,`_note_reread_uncommitted` 回 `{}`、`_drift_ack_reread_verdicts` 回 `[]`,修前修後一致(`scr/chmod.py`)。
- **缺口**:修補把 `_repo_path_unsafe` 放進 `try` 後,「丟 OSError 就當沒有」這條沒有測試。把外層 `except OSError` 改成 `except ZeroDivisionError`,`-k reread_wt_records_guarded` 28 條全綠,`-k reread_block_layer1` 12 條全綠(實驗 M14)。
- **歸因**:修前版做同樣的改壞也 17 條全綠,所以是原有漏查。

## 改壞實驗總表
每次在 clone 改壞,清 `__pycache__`,跑對應 `-k`,再用 `git checkout` 還原。每次都有確認錨點只比中一處。

| # | 改壞處 | 跑的 -k | 結果 |
|---|---|---|---|
| M1 | `_note_reread_wt_verdicts` 改回 `d.is_dir() and not d.is_symlink()` | reread_wt_records_guarded | 紅 2(上層連結的 ① 與 ②b) |
| M1b | 改成只剩 `d.is_dir()` | 同上 | 紅 5 |
| M2 | `_note_audit_config` 拿掉 RecursionError | note_audit_and_drift_config_deep_nesting | 紅 2(str 與 bytes) |
| M3 | `_drift_config_text_parts` 拿掉 RecursionError | 同上 | 紅 2 |
| M4 | `_note_reread_add_cmd` 改回 `shlex.quote` | reread_cmd_quote_shared | 紅 1 |
| M5 / 5b / 5c / 5d | `_note_reread_cmdline` 三個參數全改、或各自單改一個 | 同上 | 各紅 1 |
| M9 | `_note_reread_json` 拿掉 RecursionError | reread_wt_records_guarded、reread_deep_json_config_and_report | 紅 4 與紅 2 |
| M10a / b / c / d | `_note_reread_ledger` 的 param 與 skipped、undecidable、none、covered 各拿掉 `head_sha` | reread_ledger_head_sha_all_kinds | 各紅 2 / 2 / 2 / 1 |
| M11a | 測試總檔清除改成寫死三個名字 | runner_drops_inherited_skip_env | 紅 1(整族那條) |
| M12a / b | 來源欄寫死 `ci` 或寫死 `hook` | reread_block_hook_and_ci_wiring | 紅 1 / 紅 2 |
| M12c | `_in_ci` 只看 `CI` | 同上 | 紅 2 |
| M13a / b | 拿掉單檔符號連結判斷、拿掉大小上限 | reread_wt_records_guarded | 各紅 3 |
| M13c | 內層 `except (OSError, ValueError)` 拿掉 OSError | 同上 | 綠(原有缺口,同 F3) |
| M14 | 外層 `except OSError` 不接 | reread_wt_records_guarded、reread_block_layer1 | 綠(F3) |

- **還原與清理**:替換 `json.loads` 的測試用 `try/finally` 還原,已用 M9 驗過。替換 `_sh_quote` 的測試也在 `finally` 還原。暫存目錄靠 `_isolate_environment` 掃除,整族探針的子行程把根建在父行程的暫存根底下,不會碰到別的會談。
- **弱斷言**:`parent-link` 那組的 CLI 斷言 ②,接受「沒有判定」或「governance 是符號連結」任一句。真正釘住讀端的是 ②b,M1 實驗證明 ②b 會紅。

## 三問回答

**① 原問題的修復效果**
- **上層連結(repair)**
  - claim:`governance` 是指到 repo 外的連結時,工作目錄紀錄不被讀。
  - input:`scr/plink.py`,連結目標放合法紀錄。
  - expected:`[]`。
  - case_source:新增案例,不在作者的配對表內。
  - before:`['01234567']`。after:`[]`。
  - 歸因:有證據的修復。M1 把舊判斷還原後,新測試的 ① 與 ②b 轉紅。
- **深層設定(repair)**
  - claim:13 萬層 `.lumos/config.json` 不再讓兄弟閘崩潰。
  - input:`scr/deepcfg.py`,範圍 `base..HEAD`。
  - before:`drift check` 與 `note-audit check` 都噴堆疊。
  - after:`drift check` rc0,印三句「讀不成 JSON,照預設 block」;`note-audit check` 印同一句後照預設 block、不噴堆疊(rc1 是因為該筆記行確實沒判定)。
  - 歸因:有證據的修復。
  - 退路是 block,沒有變放行。
- **指令引號(repair)**
  - 案例:範圍或 ref 含空白、`"`、`'`、`$(…)`、反引號、`;`、中文、換行、非 ASCII。
  - 做法:`scr/quote.py` 把印出的指令丟給 `bash` 逐參數還原。
  - 結果:修前修後 8 例全部原樣還原,`/tmp/PWNED_q` 沒被建。
  - 歸因:`_sh_quote` 內容就是 `shlex.quote`,輸出本來就一致,所以這是 preserve,不是 repair。

**② 修補處的正常、錯誤與相鄰路徑**
- **正常路徑仍成立**
  - 正常紀錄資料夾、repo 根在符號連結底下(macOS 的 /tmp)、`governance` 是檔案、資料夾不存在、紀錄資料夾是檔案,修後結果都符合預期。
  - 資料夾本身是連結、單檔連結、FIFO、太大、形狀壞,仍照舊略過。
  - 子集全綠:`reread_wt_records_guarded`(28)、`reread_deep_json_config_and_report`(2)、`note_audit_and_drift_config_deep_nesting`(5)、`reread_cmd_quote_shared`(4)、`reread_ledger_head_sha_all_kinds`(7)、`runner_drops_inherited_skip_env`(4)、`reread_block_layer1`(12)、`drift_ack_reread_kind`(8)、`note_audit`(353)。
- **語意收窄**:上層 `governance` 若是指向 repo 內的連結,修後也不再讀,修前會讀。這和寫端 `_note_audit_safe_dir` 一致(寫端本來就拒寫),我認為是合理收窄,不算 finding。
- **未驗範圍**
  - Windows junction 沒有環境可驗。只能從程式推斷:`is_symlink()` 認不出 junction,是靠解析後是否在 repo 內擋住指到 repo 外的 junction。
  - 沒跑全套。
  - `pre-push` 的 `doctor`、`code-loop` 等閘只驗了深層設定檔不噴堆疊,沒驗別的。

**③ 新發現在修前修後各是什麼結果**
- F1:修前、修後都讀到外部判定檔(結果相同)。
- F2:修前、修後都噴堆疊(結果相同)。
- F3:修前、修後改壞都綠(結果相同)。
- 三條都是原有漏查,不是修補引入。

## 角色鏡頭與固定席筆記

**be-api-compat**
- 對外輸出沒變:`_sh_quote` 等於 `shlex.quote`,印出的指令逐字相同。
- 帳的欄位在這次修補沒改,`head_sha` 的測試是補在既有欄位上。
- 唯一行為差別是深層設定檔從堆疊變成「讀不成 JSON,照預設 block」的提醒,這是預期方向。
- 沒有對上題號的發現。

**be-authz**
- 這題對應「repo 外的紀錄能不能替人作保」。修補已讓上層連結的外部紀錄不被算作判定。
- 寫端守衛(`_note_audit_safe_dir`、`_drift_ledger_path_err`)沒動。
- 同族缺口只剩 F1 的 `note-verdicts` 讀端,影響有限。
- F1 沒有對上題號。

**固定席筆記**
- 判「不影響」,因為本次修補只動回頭重讀與兩個設定讀端,以及測試和筆記。
  - 事故 Issue `code-loop守衛main-direct盲區`:`pre-push` 沒動。
  - 存量漂移守衛:只是設定讀端多接一個例外,退路仍是 block。
  - `reversibility-governance-ledger`、`pitfalls-code-loop`、`筆記內容閘`、`loop-convergence-recording`:帳的欄位沒改,只補測試。
  - 其餘列名但未展開的節點:未讀,沒有牽連的檔案。
- 判「不影響」,另跑過測試佐證:
  - `guard-kill` 的兩條 ★INVARIANT★:`guard_kill_rc_precedence` 4 綠、`guard_kill_json_purity` 6 綠,程式與測試都沒碰。
  - `lumos-cli-read`:程式與測試都沒碰,未另跑測試。
  - `lumos-cli-lifecycle` 的 re-inject 合約:`reinject_preserves_outside` 3 綠。

## 文件
- 六篇筆記的新說法與真碼逐項對得上:
  - 帳的欄位與裁剪順序、`rows` 與 `layer1_fps`、判不了時 block 記 blocked / warn 記 skipped、來源欄。
  - 讀端守衛走 `_repo_path_unsafe(dirs=True)`。
  - 巢狀太深的四個呼叫端都經 `_note_reread_json`(`scripts/lumos:34731、34858、34912、35194`)。
  - 提交指令列具體檔名,與 skill 手冊 `06-代碼審與推送.md:98` 一致。
- 沒有發現矛盾。

最高等級:minor
