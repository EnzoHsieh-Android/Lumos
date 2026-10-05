# code-過期鎖收斂修復 r3 收貨與阻擋

審材：`r3-snapshot.patch` 是 r1/r2 修補後相對 `80b13355` 的完整程式差異，440 行，SHA256 `06ebc82c09d6ccdb46002704a09a264cbe361c6ffb452e3aec50d96e1beca9b7`。兩席收齊後才處置；架構席 clean，正確性席一條 major blocking。原始報告 `r3-architecture.md`、`r3-single-reviewer.md`；正確性席的 `report-normalize`、`quote-check`、`refcheck` 通過，`seat-check` 僅有未逐字點名材料的提醒，無越界引句。

| ID | 編排者獨立重現 | 去向 |
|---|---|---|
| F1 | HIT。macOS 隔離 Python 中模擬「junction 不是 symlink」與無 `getuid`：`_lens_warm_dir_ready` 最終回 False，但外部目標多出 `lumos/dispatch-lens`，實測 `trusted=False, external_lumos=True, external_cache=True`。本 repo 另一段 Windows 代碼也明載 junction 不被 `is_symlink()` 認出；[Python 3.14 pathlib 文件](https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.is_junction) 將 `Path.is_junction()` 列為獨立判斷。尚未在真 Windows 主機實跑。 | 未折入、未接受；major blocking。三輪上限已到，停止本迴圈程式修補與推送，另開 [[Issues/Windows_junction_派工快取建到外部目錄]]。 |

本地多組相關測試仍綠，但它們沒有 junction 前置；不能用綠燈覆蓋這個觀察。前案實際安裝 S6 仍 pending。本輪未建立放行 verdict，也不記 `code-loop pass`。
