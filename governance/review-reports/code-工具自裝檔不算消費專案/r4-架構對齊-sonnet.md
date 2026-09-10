severity: major

### F36 cmd_new 的 --plan 回掛路徑,F30 的修法沒對稱套用
severity: minor
blocking: 否 — 只影響錯誤訊息呈現(筆記其實已建好卻顯示成整個指令失敗),不影響資料正確性
引句:「幫你回掛到計劃 {rel} 的 plan_refs 沒寫成功: {e}」
同一支 `cmd_new` 裡,`verified_by`(`--systems`)那條路的 `except OSError as e:` 已改成 `except (OSError, ValueError, RuntimeError) as e:`(r3 整合席修法),但往上 8 行 `plan_refs`(`--plan`)那條路仍只接 `except OSError as e:`,一字未動。我在 /tmp 用 in-process monkeypatch 讓 `plan_refs` 的 `cmd_append` 丟出 `RuntimeError("等了 60 秒還輪不到寫入…")`(這正是 `_vault_write_lock` 逾時會丟的例外,對兩條路徑一視同仁),重現結果:`cmd_new` 整個未捕例外向外拋(被 main() 頂層 `except (ValueError, RuntimeError)` 接住印「擋下: …」),stdout 完全沒有「✓ new …」或「提醒:筆記建好了…」,但檔案確實已寫到磁碟(`note exists on disk: True`)——跟 F30 原始症狀一模一樣,只是換了 `--plan` 這條路徑觸發。

### F37 _vault_write_lock 是專案裡第二種鎖機制
severity: major
blocking: 是 — 引入本檔案原本沒有的第二種鎖(flock 阻塞輪詢),不是既有 O_EXCL 建鎖檔手法的延伸
引句:「fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)」
`fcntl`/`msvcrt` 在整份 `scripts/lumos` 裡只有這一處出現(grep 確認),語意也不同:既有的 `_take_lock`(dispatch-lens,file: `scripts/lumos:21320`)與另一處鎖(file: `scripts/lumos:21332`,`os.open(..., os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)`)都是「搶不到就直接回覆已經有人在做、靠檔案改名做原子接手判斷過期」的非阻塞語意;新寫的 `_vault_write_lock` 是「搶不到就睡 0.05 秒重試,最多等 60 秒」的阻塞輪詢語意。兩者解決的問題類似(同一份資源不要被兩個程序同時寫),做法是本檔案裡互不相干的兩套。

### F38 _git_show_many 是專案裡第二種讀 git 版本內容的做法
severity: major
blocking: 是 — 引入本檔案原本沒有的第二種讀 git 物件手法(cat-file --batch 二進位協定),跟既有到處用的 git show 不同源
引句:「一次讀出 ref 版本裡多支檔的內容(git cat-file --batch)」
既有每一處要讀「某個 ref 版本的檔案內容」都是逐檔呼叫 `git show <ref>:<path>`:`cmd_about_code_migrate_stamp`(file: `scripts/lumos:11296`,`git show {spec}`)、`_json_at_ref`(file: `scripts/lumos:20766`,`_lens_git(repo_root, "show", f"{ref}:{rel_path}")`)都是這樣。新寫的 `_git_show_many` 改用 `git cat-file --batch`,自己拼 `ref:path\n` 的請求、自己解析 `<sha> <type> <size>\n<content>\n` 的批次輸出格式——是整份檔案唯一一處手刻這個協定的地方(grep `_git_show_many(` 只有定義處和一個呼叫點)。

### F39 .lumos/vendored.json 跟既有的身分證機制(anchor-baseline)各自獨立設計
severity: minor
blocking: 否 — 核心技術手法相同(路徑→sha256 指紋清單),只是流程/schema 沒沿用既有慣例,結構本身沒問題
引句:「.lumos/vendored.json"   # 安裝/更新時記下每支工具檔的內容指紋」
本檔案已有同類機制:`cmd_anchor_approve`(file: `scripts/lumos:15891-15923`)寫 `governance/anchor-baseline.json`,格式是 `{"version": 1, "anchors": {路徑: sha256}, "approved_at": ..., "note": <必填理由>}`,只能靠使用者明確執行 `lumos anchor approve --note "理由"` 才能改,而且每次改動都寫 governance-log 留痕。新的 `.lumos/vendored.json` 是同一種「路徑→sha256 指紋清單」概念,但沒有 version 欄位、沒有核可指令、不需要理由,由 `_vendor_toolchain` 在每次 install/update 時自動覆寫(`_vendored_manifest_write`,不呼叫 `_append_governance_log`)。兩者目的不同(一個防竄改需要留痕、一個只是分類過濾且失敗方向本來就是「多掃不少掃」),所以沒有沿用既有 schema/流程未必是錯,但確實是第二份獨立設計的身分證,不是複用既有那份。

## 鏡頭三問

1. 分層與依賴方向:三處都不是同一種做法,見 F37(鎖)、F38(git 讀取)、F39(安裝清單身分證)。
2. 命名與錯誤處理:鎖逾時丟 `RuntimeError`(file: `scripts/lumos:10920`)跟本檔既有「重試/等待用盡」的慣例一致(對照 file: `scripts/lumos:11654`,cascade 編號連續撞名 99 次同樣丟 `RuntimeError`);指紋清單讀不懂/不存在時回空集合、不跳過(寧可多掃),跟 F12 已驗證過的既有方向一致;`_git_show_many` 讀失敗回 `None`,跟 `_json_at_ref`(file: `scripts/lumos:20764`)「沒有/壞→None」的既有慣例一致。這三處的命名與錯誤處理方向本身沒有不對齊,問題出在「引入第二種做法」而不是「同一種做法但寫法不一致」。
3. 第二種做法:第二套鎖(有,F37)、第二套讀 git 物件(有,F38)、第二套安裝清單身分證(有,F39,minor)。第四項「第二套什麼算一個連結」——沒有:這一輪反而是把讀側 `parse_frontmatter` 的 lint 判斷跟寫側 `_list_scalar_value` 的判斷收斂成共用的 `_multi_link_value`/`_SINGLE_WIKILINK_RE`(引句已見 F19 驗收),是修掉一個既有的不對齊,不是新增。

不對齊共 3 條,其中 major 2 條。

## 第三輪修法驗收

F19:修到 — 讀側 lint 與寫側 `_list_scalar_value` 共用 `_multi_link_value`,`t_multi_link_list_value_one_rule` 驗兩側同判準
F20:修到 — `_SEV_SUMMARY_LINE_RE` 限定行首、零條豁免只剝「等級字+0條」這種計數,`t_report_normalize_cmd` 新增多條覆蓋「0 台/0day/0/1/行首限定」
F21:修到 — `_about_code_path` 先 `replace("\\","/")` 再判斷,測試⑭ `src\a.ts` 存成 `src/a.ts`
F22:修到 — `_about_code_key` 用磁碟真實大小寫當比對鍵,append/remove 都靠它去重,測試⑮驗大小寫錯字項不疊、能刪
F23:修到 — `_disk_spelling` 目錄讀不到回 `(None, 目錄)`,`_about_code_path` 據此擋下,測試⑯(chmod 111)驗
F24:修到 — `_vendored_state` 比內容指紋(sha256,LF 正規化)不只比檔名,測試③b「改過的工具檔照樣要掃」驗
F25:修到 — `_write_lf` 改 mkstemp 隨機檔名 + `_vault_write_lock`(flock)序列化讀改寫,`t_concurrent_append_same_note` 驗 8 併發全成功且項目不丟
F26:修到 — `_about_code_key` 對存在的檔用 `.resolve()` 解 symlink,測試⑮驗別名不疊、能用別名刪
F27:修到 — `_list_scalar_value` 擋下訊息改掉「看不懂逗號」的說法,測試⑨驗 `tags: [a]` 訊息不含「逗號」
F28:修到 — `_about_code_key` 與 `_stack_changed_ok`/`_pitfall_diff_collect` 都改用共用的 `_posix_norm`
F29:修到 — `_impact_about_counts`/`_impact_mark_about` 都改用 `_posix_norm`(能解 `..`),`t_impact_about_hit` ⑮驗 `src/../src/svc.py`
F30:沒修到 — 只修了 `verified_by` 那條路,對稱的 `plan_refs` 路徑仍只接 `OSError`,同一類「筆記建好了被蓋掉」缺陷原樣留著,見 F36
F31:修到 — `_list_key_scalar_to_list` 保留原始加引號寫法、不重新加引號,append/remove 自我檢查都補「原本每一項還在」,測試⑨c 監控被動手腳時會擋下
F32:修到 — `_list_scalar_value` 先 `strip()` 再判斷開頭、單一連結要求 fullmatch,測試⑨b 的 QG/QH 兩種繞法都擋下
F33:修到 — remove 對 about_code 收集所有同鍵拼法逐一 `edit_fm_remove`,測試⑫(p12c 兩種寫法)一次拿掉兩筆
F34:修到 — `t_vendored_file_list_matches_what_install_ships` 開頭改用 `_need_src` 只在工具鏈本體跑
F35:修到 — `_vendor_toolchain` 的 toolkit 清單改成 `_VENDORED_TOOLKIT + _VENDORED_TREE_FILES` 精確清單,不再 rglob 整個目錄;`t_update_resyncs_claude` 新增未登記來源檔不會被裝進消費專案的驗證

## 風險掃描清單

- scripts/lumos:10902(`open(` 資源類):誤報 — 是 `_vault_write_lock` 裡開鎖檔,雖未用 `with`,但外層 `try/finally: fh.close()` 涵蓋所有路徑,確定會關閉
- scripts/lumos:17884(`open(` 資源類):誤報 — 命中的是 `_stack_changed_ok` docstring 裡描述性文字「命中 open(...)」,不是真的函式呼叫

總結:最高 severity major,blocking 共 2 條
