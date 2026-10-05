severity: minor

## 1. 分層依賴

符合既有「薄 hook／核心在 lumos」分層，無跨層直呼。

- hook 僅執行 `lumos dispatch-lens`、解析 JSON 並組提示：[scripts/hooks/claude/dispatch-lens-hook.py:321](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/hooks/claude/dispatch-lens-hook.py:321>)、[scripts/hooks/claude/dispatch-lens-hook.py:354](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/hooks/claude/dispatch-lens-hook.py:354>)。
- 鎖、背景暖機及狀態判定均留在核心：[scripts/lumos:33839](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33839>)、[scripts/lumos:33883](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33883>)、[scripts/lumos:33906](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33906>)。
- 背景程序使用參數陣列而非 shell 字串，符合 Python 慣例：[scripts/lumos:33909](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33909>)、[/Users/enzo/.agents/skills/python-idioms/SKILL.md:202](/Users/enzo/.agents/skills/python-idioms/SKILL.md:202)。

無 finding。

## 2. 命名、錯誤、事件留帳

錯誤與事件處理大致一致：

- `_excl_lock_try` 將「已存在」回為 `False`，其他建立／寫入錯誤向外傳：[scripts/lumos:33848](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33848>)。
- 筆記庫邊界轉成 `RuntimeError` 時保留原始原因，符合 R7：[scripts/lumos:15063](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:15063>)、[/Users/enzo/.agents/skills/python-idioms/SKILL.md:110](/Users/enzo/.agents/skills/python-idioms/SKILL.md:110)。
- 鏡頭核心將建鎖錯誤映射成 rc 2／`lock_error`，hook 吞下後使用既有 `_hookevent.mark("error", …)`，沒有假記成功：[scripts/lumos:33950](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33950>)、[scripts/hooks/claude/dispatch-lens-hook.py:363](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/hooks/claude/dispatch-lens-hook.py:363>)、[scripts/hooks/claude/_hookevent.py:111](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/hooks/claude/_hookevent.py:111>)。

A1  
severity: minor  
blocking: false  
file: `scripts/test_lumos.py:54550`  
引句:「+    """S3: 殘留鎖不能讓筆記庫無限等待，也要說出可查核的位置。"""」  
說明：驗收編號命名漂移。計劃把筆記庫案例定為 S4、派工鏡頭定為 S5：[過期鎖安全接手_計劃.md:34](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/docs/lumos-toolchain-knowledge/Projects/過期鎖安全接手_計劃.md:34>)、[過期鎖安全接手_計劃.md:35](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/docs/lumos-toolchain-knowledge/Projects/過期鎖安全接手_計劃.md:35>)；但測試 docstring／前三個斷言將筆記庫寫成 S3，[scripts/test_lumos.py:54580](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/test_lumos.py:54580>)，鏡頭 docstring 又寫成 S4，[scripts/test_lumos.py:54604](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/test_lumos.py:54604>)。功能綁定仍靠正確測試函式名，不構成阻擋，但會使失敗輸出與驗收條款對不上。

## 3. 第二套鎖／背景工作／帳本

沒有新增第二套機制。

- 筆記庫與鏡頭仍共同呼叫 `_excl_lock_try`：[scripts/lumos:15064](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:15064>)、[scripts/lumos:33948](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33948>)；patch 未加入 `flock`、`msvcrt` 或另一套租約鎖。
- `_lens_spawn_warmer` 是原有 `Popen` 暖機段的同層抽取，仍由 `_lens_wait_or_warm` 單一路徑呼叫：[scripts/lumos:33906](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33906>)、[scripts/lumos:33960](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/lumos:33960>)。
- hook 失敗留帳沿用 `_hookevent`；實際帳仍是既有 `governance/runtime/hook-events.jsonl`：[scripts/hooks/claude/_hookevent.py:35](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/hooks/claude/_hookevent.py:35>)、[scripts/hooks/claude/_hookevent.py:49](</var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-lock-takeover-XXXXXX.RCOcSHLJKy/repo/scripts/hooks/claude/_hookevent.py:49>)。

無 finding。

最重等級：minor