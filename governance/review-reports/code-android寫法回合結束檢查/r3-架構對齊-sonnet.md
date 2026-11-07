severity: minor

第二輪架構對齊席 F1–F5 都照方向修了,沒有退回,這輪沒有新的 major。以下 5 條是結構對、細節沒對齊的小項。我只讀了 patch 和 repo 裡對照的程式與測試,沒有重跑任何東西。

## 第二輪 F1–F5 核對

- **F1**(佔位符展開兩份)已修。新的 `_lint_placeholder_words`(`scripts/lumos:41414`)是共用核心,字串版 `_lint_cmd_with_files` 和參數清單版 `_lint_wt_argv` 都呼叫它。相對路徑改寫只剩一份。
- **F2**(`_lint_spawn_argv` 把所有 OSError 吞掉)已修。兩個函式併成 `_lint_spawn`(`scripts/lumos:41125`)。只有 E2BIG 和 argv 版的 ENOENT 等開不了程序的錯會回 None,`open(out_path)` 失敗照舊往外丟。
- **F3**(`_mark_event` 複本漂移)已修。`stop-lint-hook.py` 那份改成逐字複本,並有守衛 `t_hook_r2_mark_event_verbatim`(`scripts/test_lumos.py:132116`)盯著。
- **F4**(`_killpg` 註解寫「一樣」不實)已修。註解改成如實說三種寫法判的是同一件事。
- **F5**(「用不用 shell」開關三種傳法)已修。收成 `wt_argv` / `argv=` 一種傳法,`_lint_spawn` 不再靠 `isinstance` 判型別。

## ① 模組邊界

- **`_git_untrusted_c` 放在主程式站得住。**
  - 鉤子不能匯入主程式,而鉤子層已有自己的 `_hookshared._GIT_UNSAFE_CONFIG`(`scripts/hooks/claude/_hookshared.py:187`)。
  - 那份清單是靠環境變數 `GIT_CONFIG_PARAMETERS` 傳給子行程。
  - 兩份清單的對齊有測試盯著(`scripts/test_lumos.py:131602`)。
  - 主程式側 `_lint_wt_git`、`_spec_freeze_build`、`cmd_spec_freeze`、`_spec_commit_blob` 都走它,舊的 `_SPEC_FREEZE_GIT_C` 與 `_lint_wt_filter_args` 在 repo 裡已查無殘留。這是單一來源。
- **`unchecked_kind` 與 `_hookevent` 合約一致。** 鉤子的 `_unchecked_kind`(`scripts/hooks/claude/stop-lint-hook.py:367`)把 deliberate 記成 ok(回 None)、timeout 記 timeout、其餘一律記 error,三種值都在 `KINDS = ("ok", "timeout", "error")` 裡(`_hookevent.py:37`)。欄位詞彙在兩層各寫一份字面值,鉤子不能匯入主程式,而且有測試盯著(`scripts/test_lumos.py:131746`)。

F1
引句:「kind = kind if kind in (_LINT_WT_DELIBERATE, "timeout", _LINT_WT_FAILED) else _LINT_WT_FAILED」
引句:「out["unchecked_kind"] = _LINT_WT_DELIBERATE   # 宣告的命令沒帶檔案佔位、或檔路徑都含分隔字元被拿掉:宣告形狀不讓跑,照設計判完了」
- 同一個「判定裡沒寫明種類的 rc3」,兩層預設相反。
  - 判定層(`scripts/lumos:40608`)補 deliberate。
  - JSON 層(`_lint_new_wt_json`,`scripts/lumos:40614` 起)的說明寫「寧可記失敗、不記成綠」,補 failed。
  - 判定層先補上之後,JSON 層的 failed 預設對這條路徑永遠走不到。以後有人在判定層新增一條沒標種類的 not-checked 路徑,會被靜默記成 ok。
- 另外 `"timeout"` 在 `scripts/lumos:40606` 和 JSON 層是裸字面值,deliberate 和 failed 卻有常數,命名不一致。
- ⚠ 這比較像錯誤處理的預設值該不該收成一處,我標 minor,是否升級交編排者。
severity: minor
blocking: 否

F2
引句:「sizes = _nodehome_cat_sizes(repo_root, specs, remaining, **({"pre": pre} if pre else {}))」
- `_nodehome_cat_sizes`、`_nodehome_cat_blobs_capped`、`_nodehome_cat_blobs` 加了 `pre` 參數,但往下傳時寫成「空的就不傳」的條件式關鍵字參數。
- 註解說是為了讓「既有替身照舊接得住」,也就是為了測試替身多開了一種呼叫形狀。
- 結構沒有跨層,但同一個參數在這三個函式裡有「傳」和「不傳」兩種呼叫形狀。
- 對照:`scripts/lumos:47138`。
severity: minor
blocking: 否

## ② 命名與錯誤處理

- 命名沿用既有前綴:`_git_untrusted_c`、`_GIT_UNTRUSTED_FIXED` 對應 `_lens_git` 一帶的 `_git_` 命名,`_lint_wt_*` 沿用工作樹區的前綴。
- 鉤子的 `_onsigterm` 收 SIGINT、SIGHUP 是同一支處理器,訊號清單用 `getattr(signal, ..., None)` 兼顧沒有該訊號的平台,與 `_killpg` 的平台判斷同一風格。
- `_hookevent` 記事件的方式沒變:逾時記 timeout、失敗記 error。
- 錯誤處理的不一致就是上面的 F1。

F3
引句:「_GIT_UNTRUSTED_FIXED = ("core.fsmonitor=false", "core.hooksPath=/dev/null", "diff.external=")」
- 註解寫「對齊鉤子 `_hookshared._GIT_UNSAFE_CONFIG`」,但同一類設定現在是兩份清單。
  - 鉤子那份是 `core.fsmonitor`、`diff.external` 兩項,值用空字串。
  - 主程式這份多了 `core.hooksPath`,而且 fsmonitor 的值用 `false`。
- 兩份值不同,是各自的取捨:一個走環境變數,一個走命令列。
- 有守衛只驗「鉤子清單上的每一項主程式都關掉」(`scripts/test_lumos.py:131602`),方向是單向的,所以這項還算守住。
- 但鉤子那份沒有 `core.hooksPath`。鉤子層若自己以後也開 git 去動暫存 index,清單會再漂。目前鉤子不開,所以不構成現在的缺口。
- 對照:`scripts/hooks/claude/_hookshared.py:187`。
severity: minor
blocking: 否

## ③ 第二種做法

- **大小上限**:`_lint_wt_blobs` 改走既有的 `_nodehome_cat_sizes` 加 `_nodehome_cat_blobs_capped`,沒有另起讀法,對得上。
- **暫存清掃**:SARIF 暫存檔的清掃併進既有的 `_lint_new_clean_stale`(`scripts/lumos:41851`),和 `lintbase-*` 殘骸共用同一個時限常數,沒有另起一套。
- **改檔前推播取新內容**:`new_only` 參數拿掉。
  - 要新內容的路徑只剩 `extract_delta_texts`(`scripts/hooks/claude/impact-hook.py:452`)。
  - 非 kt 檔仍呼叫只回整份的 `extract_delta_text`(`impact-hook.py:1078`)。
  - 兩支都建在同一個 `_delta_parts` 上,取新內容沒有第二條路。

F4
引句:「def _lint_wt_head_oversize(fp, cfg):」
引句:「n = 1」
- 「超過行數或位元組上限」這條規則現在有兩份。
  - 一份是既有的 `_lint_new_oversize`(`scripts/lumos:41884`),用 `raw.count(b"\n") + 1` 比 `max_file_lines` 和 `max_file_bytes`。
  - 另一份是新的 `_lint_wt_head_oversize`(`scripts/lumos:40396`),用逐塊數換行,算法和門檻一致。
- 分出來的理由站得住:不能把整份讀進記憶體再判。
- 但門檻判斷本身沒有抽成共用的一處,也沒有守衛盯兩份等價。
- 第二輪 F1 是同類(宣告過唯一實作又多一份)被標成 major。這條我標 minor,理由是新函式只決定「要不要讀 HEAD 版基準」,最後的擋與放行判斷仍由 `_lint_new_oversize` 做。
- ⚠ 若編排者要與第二輪 F1 同等對待,可升 major,判定權交編排者。
severity: minor
blocking: 否

F5
引句:「data = _nodehome_cat_blobs_capped(repo_root, specs, cap, sizes=sizes, pre=pre)」
- 派工詞說工作樹模式所有 git 呼叫都走 `_git_untrusted_c`,實際是兩條路都帶它,但呼叫方式不同。
  - 主路徑 `_lint_wt_git` 走 `_lens_git`,帶 `GIT_OPTIONAL_LOCKS=0`、`quote=True`、`binary=True`、`timeout=60`。
  - `_lint_wt_blobs` 讀 HEAD 內容時繞到 `_nodehome_cat_*`,直接用 `subprocess.run(["git", "-C", ...])`,沒有 `GIT_OPTIONAL_LOCKS=0`。
- `cat-file` 不寫索引也不拿選用鎖,所以現在無害。
- 但「工作樹模式的 git 呼叫一律不拿選用鎖」這條不變量,在 `_lint_wt_git` 的說明裡是宣稱,實際有一條旁路不受它管。
- 對照:`scripts/lumos:40112`(`_lint_wt_git`)、`scripts/lumos:47138`(`_nodehome_cat_sizes`)。
severity: minor
blocking: 否

不對齊共 5 條,其中會擋的 0 條
