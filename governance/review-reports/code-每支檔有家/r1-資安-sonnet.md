severity: minor

逐類檢視(背景:此 CLI 會被 git hook 在任何人 clone 下來的 repo 裡自動執行;檔名、節點內容、.lumos/config.json、git 設定都可能來自不可信投稿者):

1. 不可信輸入流到危險操作(命令/路徑注入、git 參數、subprocess、fnmatch、正則):已看。所有 git 呼叫走 `_lens_git`/`_nodehome_git`,一律 list 傳參、無 `shell=True`;`--diff`/`base`/`tip` 一律先過 `_lens_full_sha`(附加 `^{commit}` 再以 40/64 hex 正則校驗回傳值)才拿去組下一個 git 指令,leading `-` 的 ref/範圍已被擋。`git show <spec>:<path>` 的 `spec` 恆為已驗證 sha 或空字串,`path` 前面一定有 `:`,不會被當成獨立旗標解析。`.lumos/config.json` 的 `node_home.ignore` 只餵 `fnmatch`,不會被拿去執行。發現兩處路徑讀取沒收斂到同一套防護,見 F1、F2。
2. 登入與權限:已看,無(無登入機制,本次改動未涉權限放寬)。
3. 密鑰與個資:已看,無。治理帳新增的 `nodehome-check` 事件只寫檔案路徑與節點名(`pairs`/`notes`),經 `json.dumps` 正常跳脫,不含節點正文或設定檔內容。
4. 加密與傳輸:已看,無(無網路呼叫)。
5. 執行邊界(執行不可信檔、shell 插值、寫全域設定、路徑穿越/symlink):已看,git 快照讀取路徑(`_nodehome_reader`)明確排掉 `is_symlink()`、`_nodehome_list` 只收 mode 100644/100755(排除 120000 連結檔與 160000 子模組,附測試 `t_nodehome_skips_symlinks_and_submodules` 佐證),寫入全限於 `env.vault` 之下。但有兩處讀檔沒有套用同一套邊界檢查,見 F1、F2。
6. 新依賴:已看,無。只用到 `fnmatch`/`os`/`re`/`json`/`subprocess`,均為既有標準庫引用方式,沒有新增第三方套件或鎖版問題。

### F1 lumos doctor 每次 push 都會跟隨 .lumos/config.json 的 symlink 讀本機任意檔
severity: minor
blocking: 否 — 讀取確有發生,但目前程式只取用經驗證的 `mode`(固定 on/warn/off 三選一),沒有把讀到的原始內容印出或外流,寫不出「攻擊者實際拿到什麼」,屬縱深防禦缺口而非可直接利用的外洩
引句:「p = Path(repo_root) / ".lumos" / "config.json"」
佐證 file: `scripts/lumos:17412-17413`(`_nodehome_config` 的 `from_snapshot=False` 分支);呼叫點 `scripts/lumos:976`(`_nh_mode = _nodehome_config(_vault_repo_root(env))["mode"]`,`run_doctor` 一開頭就跑);`scripts/hooks/pre-push:136` 每次 `git push` 都自動跑 `lumos doctor --ci`
攻擊路徑(推論成分:路會被踩到,但目前找不到把內容印出去的出口):惡意投稿者在分支裡把 `.lumos/config.json` commit 成指向受害者本機某檔的 symlink → 受害者 clone/checkout 後正常 `git push` → pre-push 自動跑 `lumos doctor --ci` → `Path.is_file()`/`read_text()` 跟隨 symlink 讀取該檔 → 目前只被拆成 on/warn/off 三個固定字之一印出,沒有回顯原文,故未觀察到可外流的通道;同一支診斷式在 `_nodehome_ledger`/`cmd_home_check` 用的是走 git 快照、明確擋 symlink 的 `_nodehome_reader`,建議這裡比照統一,否則之後有人在 `cfg["warnings"]` 旁加一行 print 就會變成真的外洩。

### F2 dispatch-lens 的 lands_in 欄位沒驗證就拼路徑讀檔,可跳出圖譜目錄
severity: minor
blocking: 否 — 讀到的只有「檔案存不存在」與 frontmatter 統計數字(份數/行數/布林),不是原文內容,且需要攻擊者預先猜到受害者本機一個真實存在的 `.md` 路徑,拿不到有意義的資料
引句:「p = Path(root) / vault_rel / f"{it}.md"」
佐證 file: `scripts/lumos:22594-22609`(`_nodehome_landing_sizes`,新函式);對照 `scripts/lumos:11099-11113`(`_about_code_path` 對同類 `about_code` 欄位有做 `resolve()+relative_to(root)` 的跳脫檢查,`lands_in` 這裡沒有套用同一防護,也沒有套上同支 diff 自己加的 `_LANDS_IN_ITEM_RE`——那個 regex 只用在 `_disposal_landing_step`,`_nodehome_landing_sizes` 沒有引用)
攻擊路徑:惡意投稿者送一份 Projects/*.md 設計 spec(design-loop 審查用),frontmatter 寫 `lands_in: ["../../../../某處/檔名"]`(跳脫路徑、只需以能被組出 `.md` 結尾）→ 審查流程呼叫 `cmd_dispatch_lens_spec` 讀這份 spec → `_nodehome_landing_sizes` 直接用該字串跟 `root`/`vault_rel` 拼路徑、未做 `relative_to(root)` 校驗 → 若該路徑在受害者機器上剛好是一個真實檔案,會把它的 plan_refs 數/KEY 行數/合約數/about_code 檔案數/是否寫負責範圍印進派工詞摘要 → 攻擊者只拿到這些存在性與計數訊號,拿不到原文。

總結:最高 severity minor,blocking 共 0 條
