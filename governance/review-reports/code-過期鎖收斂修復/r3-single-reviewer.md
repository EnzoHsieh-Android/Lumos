severity: major

finding: F1 Windows junction 分支會先在不可信目標建立外部目錄，才拒絕暖機
severity: major
blocking: 是
引句:「建立鎖前驗同一私有快取目錄；不可信時不沿路徑建立背景鎖。」
file: `scripts/lumos:33968`
file: `scripts/lumos:33574`
file: `scripts/lumos:33580`
file: `scripts/lumos:18092`
觀察: `_lens_warm_dir_ready` 先呼叫 `_mkdir_trusted_under_home`。該 helper 只以 `is_symlink()` 辨識連結；repo 自己已明載 Windows junction 不會被此方法辨識。無 `getuid` 時又不做 owner／mode 檢查，因此父層 junction 會被當成普通目錄，並在 junction 目標建立 `lumos/dispatch-lens`；之後 `_trusted_private_dir` 雖回 False、沒有建立鎖，外部寫入已發生。
因果: 本修正宣稱不可信快取路徑不會沿路建立暖機鎖，但建鎖前置本身仍會改動外部目標，違反既有「不可信路徑連空資料夾都不准建」邊界；新增測試以 POSIX symlink 模擬無 `getuid`，沒有覆蓋 repo 已知的 Windows junction 差異。
最小重現:
```python
# 在 macOS 以「junction 不被 is_symlink 認出」故障注入模擬 Windows 分支
with mock.patch.object(Path, "home", return_value=home), \
     mock.patch.object(Path, "is_symlink", new=no_junction_detection), \
     mock.patch.object(m, "os", without_uid):
    ok = m._lens_warm_dir_ready(cpath)
print(ok, (victim/"lumos").exists(), (victim/"lumos"/"dispatch-lens").exists())
```
重現結果: `False True True`；信任閘拒絕暖機，但外部兩層目錄已被建立。修正需在逐層建立時辨識 junction／reparse point，或在任何 mkdir 前先用不跟隨 junction 的逐層判準驗證。

合法私有目錄暖機、POSIX 父層／檔案 symlink 拒絕：已讀,無 finding。
Popen 失敗後替代鎖保留、清鎖失敗分流：已讀,無 finding。
期限末最後一次快取讀取與逾時分類：已讀,無 finding。
真背景產快取並自行清鎖整合：已讀,無 finding。
凍結 patch SHA、測試錨點與指定圖譜材料：已讀,無 finding。

總結: major；blocking 1 條
