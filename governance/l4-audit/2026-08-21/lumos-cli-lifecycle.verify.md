C1 [❌] install/uninstall 確為純機器層,但 bootstrap 並非「只動 ~/.local/bin+~/.claude」——它明確會寫本 repo 專案層(git config core.hooksPath、docs/vault、CLAUDE.md) | 證據: scripts/lumos:9153-9176(cmd_bootstrap step3 呼叫 `_install_hooks_py(root)`、`cmd_init(force=False, no_pull=True)`,root 為當前 repo);scripts/lumos:8821-8875(_vendor_toolchain 寫 docs/<slug>-knowledge、CLAUDE.md、git config,cmd_init/update 共用同一函式)

C2 [✅] install 在 Unix 用 symlink、Windows 用 lumos.cmd shim,連帶裝 skills,並檢查 PATH | 證據: scripts/lumos:8171-8203(symlink 分支 8183、_install_skills() 呼叫 8195、PATH 檢查 8201)

C3 [✅] uninstall 對稱移除全域指令與 skills;junction/連結移除用 os.rmdir 只移連結本身,失敗才 fallback rmtree(非遞迴刪 target) | 證據: scripts/lumos:8210-8240(os.rmdir(d) 於 8230,OSError 才 shutil.rmtree fallback)

C4 [✅] bootstrap 支援 --lumos-url/--lumos-home/--pull/--init 旗標;--pull 為 store_true(預設 False),預設不 pull 既有 clone | 證據: scripts/lumos:14516-14523(argparse 定義);scripts/lumos:9119-9125(cmd_bootstrap: `if pull: ... else: print("...已在...")`,無 --pull 不執行 _pull_source_or_abort)

C5 [✅] 四分流邏輯與 _confirm_tty/--init 行為皆符合:①vault+vendored→接 hooks ②中間態只提示不動作 ③無 vault 經 _confirm_tty(印完整路徑、預設N)確認,--init 跳過確認並一律 force=False,no_pull=True 呼叫 cmd_init ④非 git repo 只跑機器層 | 證據: scripts/lumos:9151-9180(四分流);_vault_in 名稱判斷見 scripts/lumos:9282-9294;cmd_init 呼叫參數見 scripts/lumos:9176

C6 [✅] init 建 vault(6 資料夾+.gitignore+MOC/index.md+CLAUDE.md 注入)+ vendor 工具組 + 裝 hooks;_INIT_SUBDIRS_FULL 恰為 6 個資料夾 | 證據: scripts/lumos:8952(`_INIT_SUBDIRS_FULL = ("Systems","Verification","Projects","Issues","Sessions","MOC")`);scripts/lumos:9202-9280(cmd_init 全流程,_scaffold_project 呼叫於 9271)

C7 [✅] update 只刷新本專案 vendored 工具組,vault 受 _scaffold_project 的 kg.exists() skip 保護不動 | 證據: scripts/lumos:8876-8894(cmd_update);scripts/lumos:8955-8958(_scaffold_project 內 `if kg.exists(): print("✓ vault 已存在,跳過 scaffold(保護資料)"); return`)

C8 [✅] ★INVARIANT★ reinject 只覆寫 sentinel 之間 body,之外內容 byte-equal 保留;有實測測試通過驗證前後綴逐 byte 相同 | 證據: scripts/lumos:8537-8608(_reinject_claude_block,splice 僅動 span.body_start:span.body_end);scripts/test_lumos.py:9758(t_reinject_preserves_outside)——實跑:`python3 scripts/test_lumos.py -k t_reinject_preserves_outside` → 3 passed 0 failed(前綴/後綴 byte-equal 斷言皆過)

C9 [✅] _confirm_tty 三階確認機制、嚴格 y/yes、預設 N、LUMOS_TTY/LUMOS_TTY_TIMEOUT 測試接縫皆與碼相符 | 證據: scripts/lumos:9035-9070(①isatty+input()+EOFError 續下階 9045-9049 ②os.open(tty,O_RDWR)+os.write+select timeout+os.read 9050-9066 ③皆不可回 None;_norm 嚴格 y/yes 9044)

C10 [✅] teardown 三步固定順序(全域hook清理→deinit keep_graph=True→uninstall)、圖譜永遠保留,順序理由(deinit 會刪 merge-claude-settings.py,_teardown_global_claude 需要它)於 docstring 明確寫出 | 證據: scripts/lumos:8270-8332(cmd_teardown 三步呼叫於 8320/8322/8324);scripts/lumos:9001(_teardown_global_claude docstring:「須在 deinit 刪掉 vendored merge-claude-settings.py 之前跑」)

C11 [✅] _selfdelete_risk 僅 Windows(含 LUMOS_SIMULATE_WINDOWS 測試接縫,不動全域 _IS_WIN)生效,路徑比對用 parts 前綴而非 is_relative_to(3.8 相容),except 為窄範圍 OSError,--dry-run 豁免 | 證據: scripts/lumos:8241-8267(完整函式;parts 前綴比對於 8266-8267,`except OSError`於 8263);scripts/lumos:8355(`if not dry_run and _selfdelete_risk(root)`,dry-run 豁免);實跑:`python3 scripts/test_lumos.py -k t_selfdelete_risk_python38_compatible_and_dryrun_exempt` → 5 passed 0 failed

C12 [✅] slug 決定順序 --name > 既有 vault 名稱 > repo basename,②先於③避免 --force 在既有 vault 上誤用 basename | 證據: scripts/lumos:9214-9221(`if name: ... elif existing is not None and existing.name.endswith("-knowledge"): ... else: slug = _slugify_vault(root.name)`);實跑:`python3 scripts/test_lumos.py -k t_init_force_uses_existing_vault_slug` → 4 passed 0 failed

C13 [❌] deinit 確實在 root==_lumos_src() 時 rc=2 拒絕,但 update 並非拒絕執行——它改走「reinject-only」分支,只刷新 CLAUDE.md 且通常回傳 rc=0(成功),不是中止 | 證據: scripts/lumos:8346-8349(cmd_deinit:「當前就是 Lumos 來源本身,deinit 拒絕執行」,return 2);對照 scripts/lumos:8887-8892(cmd_update:root==src 時執行 `_reinject_claude_block(root, slug)` 並 `return 0 if ri.status in (...) else 2`,不是無條件 rc2 拒絕)

C14 [✅] _VENDORED_TOOLKIT 固定 5 檔 + hooks/templates 兩夾,_vendor_toolchain 與 _deinit_remove_vendored 共用同一常數 | 證據: scripts/lumos:8783-8785(常數定義,5 檔);scripts/lumos:8848-8850(_vendor_toolchain 內 `toolkit = list(_VENDORED_TOOLKIT)` + hooks/templates rglob);scripts/lumos:8638(_deinit_remove_vendored 內 `for rel in _VENDORED_TOOLKIT:`)

C15 [✅] _pull_source_or_abort fail-closed 政策:有 remote 拉不到即中止(寫檔前);無 remote 不算失敗;update/init/bootstrap 三指令皆有 --allow-stale 逃生門 | 證據: scripts/lumos:8788-8819(函式本體,無 remote 分支 8804-8806、拉失敗中止 8814-8819);argparse --allow-stale 見 scripts/lumos:14514-14515(update)、14527-14528(init)、14521-14522(bootstrap);實跑四測試:`t_vendor_pull_failure_aborts`/`t_vendor_no_remote_skips_pull`/`t_vendor_allow_stale_overrides_pull_failure`/`t_bootstrap_pull_failure_aborts` 皆 passed(共 9 passed 0 failed)

C16 [✅] 本 repo 現行 git remote 僅一個「Lumos」指向 EnzoHsieh-Android/Lumos.git,無 Full 鏡像 remote,亦搜不到任何推送鏡像的腳本(僅一處註解提及 Citrus_Lumos_Full 作為「鏡像自足」情境說明);鏡像自身 get.sh/README 是否已改指向自身屬外部 repo,不在本 repo 可查範圍 | 證據: `git remote -v` 輸出僅 `Lumos https://github.com/EnzoHsieh-Android/Lumos.git`;`grep -rn "Citrus_Lumos_Full"` 全 repo 僅命中 scripts/lumos:9079(註解,非推送腳本)

C17 [✅] slim/ 目錄存在 FROZEN.md 告示,明載「本目錄留在 repo 裡只有兩個用途:①測試還在跑(scripts/test_lumos.py 約 370 處引用)②歷史紀錄」「沒有自動發布…分家後這條路已停」,與主張一致 | 證據: slim/FROZEN.md(全文可讀,「⛔ 本目錄已凍結(2026-08-20)」起)

C18 [✅] _deinit_unbar_gate 只在 core.hooksPath 指向本 repo scripts/hooks 時才 unset,否則保留並印警告;cmd_uninstall 只移除 is_symlink() 為真的 ~/.local/bin/lumos,一般檔案存在時只印警告不刪 | 證據: scripts/lumos:8418-8441(_deinit_unbar_gate,比對於 8430-8436,不同則 `return 0` 不 unset);scripts/lumos:8210-8221(cmd_uninstall,8183 `if dst.is_symlink()...` / 8185-8190 `elif dst.exists(): print(... 是一般檔... 保留不動)`,無 unlink)

✅15 ❌3 ❓0 ⏭0
