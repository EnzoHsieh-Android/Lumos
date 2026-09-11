severity: major

### F1 test-layers 的 errors="replace" 沒有任何 regression test 真的驗到,整段拿掉全套仍 7 passed 0 failed
severity: major
blocking: 是 — 新增的迴歸測試自稱覆蓋六個入口(含 test-layers),但這條路徑的修法可以整行刪掉而測試不翻紅,等於沒有證據
引句:「check(f"{args[0]} 不中斷", "UnicodeDecodeError" not in r.stderr」
file: `scripts/lumos:18367` `cmd_test_layers` 本來就有 `except Exception as e:` 整段包住,且該函式的 git 呼叫(scripts/lumos:18359 起)只帶 `--name-only`,輸出只有檔名、從不含檔案內容,不可能觸發這次要修的解碼錯誤
1. 在 /tmp 複製一份 scripts/lumos + test_lumos.py,只把 `cmd_test_layers` 那一行的 `errors="replace"` 移除(其餘 8 處修法照舊保留),執行 `python3 test_lumos.py -k t_diff_readers_survive_non_utf8_content`。
2. 實測結果:`7 passed, 0 failed`,「✓ test-layers 不中斷」照樣打勾——當場翻紅失敗,證明這條修法在測試裡沒有任何斷言在守。
3. 根因是雙重冗餘:`--name-only` 輸出本就不含檔案內容(非 UTF-8 位元組進不了這支 git 輸出),加上既有 broad except 早已把任何解碼例外吞成 fail-open,errors= 加不加行為一致。

### F2 _delguard_confidence 的 git grep 走同一種文字模式讀取,卻沒跟著這次「查清範圍」的掃法修到
severity: minor
blocking: 否 — 會被 cmd_delguard_check 既有 except Exception 接住降級 rc0,delguard 本來就是「恆 rc0」的 advisory 設計,行為不因此劣化
引句:「照刪除守衛讀差異的先例」
file: `scripts/lumos:17544` `_delguard_confidence` 的 `git grep --cached -n -I -w -F -e ...` 呼叫用 `capture_output=True, text=True, cwd=repo_root, timeout=timeout`,沒有 `errors=`;同一條 delguard 流程裡 `scripts/lumos:17684` 的 `git diff --cached` 已經帶 `errors="replace"`,兩處不一致
1. 在 /tmp 建一個 repo:某追蹤檔含非 UTF-8 位元組(git 的二進位判斷不會攔下,跟本次 PR 描述的觸發條件同型),要刪除的 token 剛好出現在那支檔裡。
2. 執行等價於該行的呼叫:`subprocess.run(["git","-c","core.quotePath=off","grep","--cached","-n","-I","-w","-F","-e","deleteMe","--","."], capture_output=True, text=True, cwd=".")`,當場丟出 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 85: invalid start byte`,與這次 PR 要修的錯誤同一種。
3. 診斷描述聲稱「照刪除守衛讀差異的先例」修了九處,但 delguard 自己流程裡這一處 git grep 沒有被同樣方式修到,只是恰好被外層既有的 broad except 接住而不影響觀測行為。

總結:最高 severity major,blocking 共 1 條
