---
type: issue
status: open
created: 2026-10-05
updated: 2026-10-05
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/platform
summary: |-
  FLAG:TECHNICAL
  DECISION:代碼審第三輪上限仍有重大缺陷；使用者裁決暫緩 Windows 問題，允許以跳過留痕推送分支，Issue 保持 open。
  KEY:模擬 Windows junction 且無 getuid 時，逐層建目錄會先在外部目標留下兩層空目錄，信任檢查才拒絕暖機。
---
# Windows_junction_派工快取建到外部目錄


## 症狀

整段分支 `code-過期鎖收斂修復` 第三輪正確性席發現：模擬 Windows junction 指向外部目錄，呼叫暖機前目錄檢查最後回 False，但外部目標已多出 `lumos/dispatch-lens`。編排者在 Python 3.14 的隔離 clone 以無 `getuid` 與「junction 不被 `is_symlink()` 認出」故障注入獨立重現 `trusted=False, external_lumos=True, external_cache=True`。此為 Windows 行為模擬，尚未在真 Windows 主機實跑；原報告及凍結 patch 見 `governance/review-reports/code-過期鎖收斂修復/r3-single-reviewer.md`。

## 根因

逐層建立私有目錄的 helper 在每層 `mkdir` 後用 `is_symlink()` 擋連結，並在最後才由路徑解析比對拒絕不可信目錄。Python 將 junction 與 symbolic link 分成兩種判斷；[Python 3.14 pathlib 文件](https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.is_junction) 提供 `Path.is_junction()`。本 repo 另一段 Windows junction 處置也已註明 `is_symlink()` 認不出 junction。新建鎖前入口呼叫這個逐層建立 helper，使「拒絕寫入」的結果來得太晚。

## 現在怎麼繞

使用者於 2026-10-05 明說「先不管windows問題」；這只放行本分支推送，不代表第三輪審查通過，也不代表 Windows 安裝可用。若隔離環境需取派工結果，可用既有 `LUMOS_DISPATCH_LENS_NO_CACHE=1` 走同步計算；`t_lens_no_cache_bypasses_warmer` 驗了不建新暖機鎖與零背景程序。既有外部目錄或鎖的處置仍要先查實際擁有者，不能按路徑或鎖齡擅刪。

## 修好條件

另開修復循環，先用故障注入測試釘住「無 `getuid`、父層 junction、外部目標連空目錄都不新增」，再讓逐層建立在任何 `mkdir` 前辨識 junction／reparse point 或改用不跟隨的逐層開啟；同時驗合法私有路徑仍能建鎖、背景快取完成後會清鎖、hook 錯誤分類不退化。有 Windows 環境時須補真 junction 實跑；沒有時明示模擬證據的限制。新差異要另開代碼審編號，不能把第三輪未折重大發現記成已放行。


## 2026-10-05 裁決範圍與回頭入口

使用者已在第三輪重大發現與處置閘 FAIL 呈報後，裁決先不處理 Windows 問題。推送時應用 `lumos code-loop skip` 明記未修缺陷，不能改記 pass。此裁決僅限此分支的推送；Issue 保持 open。若要在 Windows 啟用派工暖快取、或後續有真 Windows junction 重現，先回本 Issue 的「修好條件」完成修復與新審查，不能沿用本次跳過紀錄。
