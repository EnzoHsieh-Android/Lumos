severity: major

絕對路徑或遞迴路徑可繞過家目錄限制
severity: major
引句: 「cur = cur / seg」
blocking: 是
原因: `pathlib.Path` 的 `/` 運算子若遇到絕對路徑（如 `"/etc"`）會直接重置路徑。這使得 `_mkdir_trusted_under_home` 可以被誘導去檢查或建立家目錄以外的任意路徑，完全失去「Under Home」的守衛意義。

武裝目錄的葉節點在檢查前就被修改權限
severity: major
引句: 「d.mkdir(parents=True, exist_ok=True)」
blocking: 是
原因: 在 `cmd_dispatch_lens_arm` 中，`_mkdir_trusted_under_home` 只檢查到 `d.parent`。隨後的 `d.mkdir` 與 `os.chmod(d, 0o700)` 直接作用於葉節點。若葉節點 `d` 事先被換成指向敏感檔案的連結，`chmod` 會在最後一關 `_lens_arm_dir_ok(d)` 攔截前就先改掉目標權限。

對合法符號連結的相容性破碎
severity: major
引句: 「if cur.is_symlink() or not cur.is_dir():」
blocking: 是
原因: 許多 Linux 使用者會將