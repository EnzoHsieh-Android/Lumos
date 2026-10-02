severity: clean

核對範圍:r3-delta.patch 全部三處(`_fix_load_record` 逐字串檢查、`linked` 改 `is_symlink`、設定警告帶路徑)與對應測試,在 clone 用 Python 3.14.6 實跑。

## F1 核對結果(無問題)
severity: clean
blocking: 否
引句:「stack.extend(x.keys()); stack.extend(x.values())」
佐證行:file: `scripts/lumos:11676`

1. 逐字串檢查走迭代堆疊、不遞迴,鍵與值都推進去。實跑結果:鍵含孤立代理字元、鍵含 \u0000、900 層巢狀裡藏孤立代理字元,三者都回 (None, 錯誤訊息),沒當掉。
2. 規模:50000 層巢狀 JSON 可解析(3.14 的 C 解析器),走訪 0.01s;20 萬個字串 0.03s;6 萬個鍵 0.03s。檔案有 1MB 上限,沒有變慢或爆掉的形狀。
3. 其他形狀:原始位元組裡的孤立代理(\xed\xa0\x80)在 read_text 就回「讀不懂(UnicodeDecodeError)」;原始 NUL 由 json 回「Invalid control character」;5000 位整數回 ValueError。都被原本的 except 接住,都是 rc 2 路徑。
4. 順序:字串檢查在形狀檢查之後、groups 上限檢查之前。非法形狀先回形狀錯誤,不影響正確性。
引句:「linked = any((tree / rel / dep).is_symlink() for rel in _dep_roots for dep in _LINT_DEP_DIRS)」
佐證行:file: `scripts/lumos:24323`

5. is_symlink:`_lint_link_deps` 只在 `src.is_dir() and not link.exists()` 時建連結。依賴資料夾進版控時樹裡本來就有實體資料夾,不建連結,is_symlink 為 False,不印警告,符合意圖。建連結失敗(例如 Windows 無權限)時 OSError 被吞,is_symlink 同樣為 False,警告也不印,這是正確的。
6. 變異驗證:把這行換回 `(rr / rel / dep).is_dir()`,t_fix_check_tree_setup 的 ④e 轉紅(9 passed, 1 failed);還原後 10 passed。
7. 測試:t_fix_check_bad_input 21 passed、t_fix_check_tree_setup 10 passed。⑥b(字面 \u0000 不誤擋)與孤立代理字元的新斷言都在其中。
8. 殘餘極小情形(不報為問題):版控裡若追蹤了一個懸空 symlink 叫 venv,is_symlink 為 True,會多印一句警告,只是提示、不影響判定。

最高等級:clean,blocking 共 0 條
