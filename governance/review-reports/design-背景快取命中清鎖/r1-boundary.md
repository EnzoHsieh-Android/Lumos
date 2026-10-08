severity: major

## 問題與邊界

severity: major
blocking: yes
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:26`
引句:「當背景程序持有本次 `.warming` 鎖且進場命中快取時，`_dispatch_lens_graph` 應回快取並清掉自己的鎖」
現碼佐證 file: `scripts/lumos:33135`
現碼佐證 file: `scripts/lumos:33140`
現碼佐證 file: `scripts/lumos:34077`
finding: 原生 Windows 沒有 `os.getuid`，背景程序在 `_lens_cache_read()` 便拋 `AttributeError`，到不了快取命中返回，也到不了計劃中的 `finally` 清鎖；因此 S1、S2 在 repo 已宣告支援的 Windows 平台無法成立，且目前驗收沒有 Windows 分支或手動驗證。
最小重現: 在 Python 3.14 載入 `scripts/lumos`，建立合法 JSON 快取後，以 `del os.getuid` 模擬 Windows 的 `os` API，再呼叫 `m._lens_cache_read(cache)`；實際輸出為 `AttributeError: module 'os' has no attribute 'getuid'`。現碼同檔 `_trusted_private_dir` 已採 `hasattr(os, "getuid")` 的跨平台判準，可直接對照。
建議: 本案同時把 `_lens_cache_read` 的 UID／mode 檢查改成與 `_trusted_private_dir` 相同的跨平台分支，並新增模擬 `os.getuid` 不存在的快取命中測試；由於 repo 明載「無 Windows CI」，驗證紀錄還須把真 Windows 檔案系統行為列為手動重驗，不能只用 POSIX 暫存檔宣稱 Windows 已驗。

## 驗收條款

已讀，除上述 S1／S2 的 Windows 不可執行性外無 finding。

## PRIOR-ART 與 RETIRE-IF

已讀，無 finding。

## 實務隱患

已讀，無 finding。

## 回退

已讀，無 finding。

## 驗證順序

已讀，除上述缺少 Windows 驗證出口外無 finding。

總結: major，blocking 1 條。
