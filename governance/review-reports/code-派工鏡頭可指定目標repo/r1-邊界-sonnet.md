severity: major

「邊界與輸入」席的結論:程式碼有 1 條 major(提交寫法遇到計劃裡反引號內的 NUL 會崩潰)和 1 條 minor(候選數量沒有上限,會把 hook 的 45 秒拖爆)。我跑了實驗,spec-freeze 與 dispatch-lens 的大部分邊界都正確。

severity: major
blocking: 是 — 提交寫法下 dispatch-lens 直接 traceback、不印 lens_fail,hook 只能靜默放空,整段鏡頭丟失,而且工作樹寫法讀同一份計劃是正常的(行為分叉)
引句:「if _spec_ls_tree_one(root, commit, cand) is not None:」
問題:`_lens_spec_code_files` 的反引號正則 `` `((?:scripts|...)/[^`\s]+)` `` 會收進 NUL。工作樹寫法下 `resolve()` 與 `is_file()` 吞掉 ValueError。提交寫法則把候選送進 `_spec_ls_tree_one` 的 `_lens_git`,而 `_lens_git` 只接 OSError 與 TimeoutExpired。子行程參數含 NUL 會丟 `ValueError: embedded null byte`,沒有任何地方接住。同一份補丁裡 `_spec_commit_has` 已經手動擋 NUL,這裡漏了。
具體失敗情境:提交裡的計劃含 ``x `scripts/a<NUL>b.py` y``,執行 `lumos dispatch-lens --spec <40碼>:docs/t-knowledge/Projects/nul.md --json`,結果是 traceback 加 `ValueError`。stdout 沒有 JSON,所以 hook 的 `_last_json` 讀不到 `lens_fail`,`_spec_fail_note` 回空字串,審查員拿不到任何固定席節點,也沒有說明行。同一份計劃用工作樹路徑讀,rc 0、輸出正常。S4 測了含 NUL 的計劃本文,但 NUL 不在程式路徑候選裡,所以沒碰到這條路。
佐證:實測如上;``file: `scripts/lumos:_lens_spec_code_files(補丁新增)` ``;`_lens_git` 的 except 範圍;測試 ``file: `scripts/test_lumos.py:t_dispatch_lens_spec_commit_regular_blob_only`` 沒有 NUL 在路徑候選的案例。

severity: minor
blocking: 否 — 超時時 hook 會附既有的逾時說明,放行不擋
引句:「elif commit and cand not in tried and len(only) < _LENS_SPEC_MAX_FILES:」
問題:`only` 滿 5 筆才停止嘗試。「提交裡也沒有」的候選每個都跑一次 `ls-tree` 子行程,沒有筆數上限也沒有預算檢查。`_lens_spec_linked` 對每個不重複的 `[[連結]]` 跑一次 `cat-file -e`,同樣沒有上限。`_nodehome_landing_sizes` 的 `_spec_commit_has` 也一樣。工作樹寫法只查檔案系統,不會有這個成本。計劃上限是 1MB,所以這條路徑是設計允許的輸入。
具體失敗情境:一份 60KB 的計劃含 2000 個不重複連結與 2000 個不存在的反引號路徑。提交寫法跑了 99 秒,工作樹寫法跑 1 秒,遠超 hook 的 45 秒總帳。只有 4 萬個不重複連結的計劃,40 秒內跑不完。大約 900 個以上的不重複引用就會超時。建議候選與連結各設上限(例如 50 筆),或像 `_LENS_SPEC_BUDGET` 一樣依剩餘時間停止。
引句:「elif not _spec_commit_has(root, commit, f"{vault_rel}{node}.md"):」
佐證:實測如上;``file: `scripts/lumos:_lens_spec_linked(補丁新增)` ``。

已讀,無 finding:
- 編號形狀:大小寫(轉小寫後比對)、7 碼、39 碼、41 碼、冒號前恰好 6 碼(走工作樹路徑)、64 碼對 SHA-1 repo、冒號後空、多個冒號、`./`、`..`、反斜線、`docs/-knowledge`、`T-knowledge` 都回預期代碼。
- 路徑與提交內容:目錄、符號連結、中文檔名、NFD 都回預期。
- spec-freeze 輸入:剛好 1048576 位元組照凍、1048577 拒絕;二進位、中文檔名都能凍;計劃是目錄、符號連結或路徑中間有符號連結目錄時拒絕;無 HEAD 回 `no_head`,`--json` 印 `freeze_fail`。
- spec-freeze 的 `--out`:不存在的父目錄會自動建;已存在而且相同就重寫,不同就拒絕;父層是檔案也拒絕。
- spec-freeze 不留痕跡:`git status` 與 refs 沒被動到,暫存 index 目錄也都刪掉了。
- 測試殺傷力:我在乾淨副本把判斷改壞,下列改動都讓測試翻紅,清過 `__pycache__`:`>` 改 `>=`(1MB 邊界)、拿掉 lstat 的符號連結判斷、`--out` 相同內容比對改成永遠真、拿掉 `core.hooksPath`、拿掉 `--no-filters`。
- 只有拿掉 `O_NOFOLLOW` 沒有測試翻紅。前面的逐段 lstat 已擋住符號連結,所以這是競態防護,不算 finding。
- 暫存清理:我的實驗目錄已刪。但跑 `-k` 子集時,失敗的測試留下 `gctl-run-*` 現場(`bwncdqo8` 已刪,mutation 那四次的現場我沒記下目錄名,無法確認哪些是我的,所以留著)。

最高等級 major,blocking 1 條。
