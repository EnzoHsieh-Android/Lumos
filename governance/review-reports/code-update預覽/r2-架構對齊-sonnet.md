severity: minor

## 問1 分層與依賴方向
對齊。改動都留在原函式內(_reinject_compute、_update_rule_plan、_preview_vendored、_update_preview),沒有新增函式、沒有跨層呼叫;預覽層呼叫共用工具 `_sh_quote`,方向與 scripts/lumos:42783、34279 對 `_sh_quote` 的使用一致。
引句:「q = _sh_quote(str(Path(src).resolve()))」
佐證:file: /home/user/Lumos/scripts/lumos:20947(呼叫);/home/user/Lumos/scripts/lumos:438(定義)

## 問2 命名與錯誤處理
標籤 `root:` 與 cmd_deinit 預覽一致(scripts/lumos:20022 對 20956)。窄接 `(UnicodeDecodeError, OSError)` 與 deinit 內多處寬接 Exception(19990、20151)不同,但 19903 附近有「不要放寬成 except Exception」的既有註解先例,且 diff 加了理由註解,屬刻意分歧,不算不一致。唯一小處:新註解是行尾長註解、中文標點與「;」夾在同一行,比鄰居行尾註解(如 scripts/lumos:20951 一帶的簡短註解)長,但風格不列。
引句:「print(f"  root: {root}")」
佐證:file: /home/user/Lumos/scripts/lumos:20022(deinit 預覽標籤);/home/user/Lumos/scripts/lumos:19990(deinit 寬接 Exception)

## 問3 第二種做法
修正反而消除了第二種做法:刪掉區域 `import shlex as _shlex` 改用既有 `_sh_quote`,沒有自創工具函式。difflib.unified_diff 本處沿用原呼叫(fromfile/tofile 形式),另一處用法在 scripts/lumos:8783(lineterm="" 搭配 splitlines()),兩者輸入換行處理本就不同,不構成新做法。測試改成 `r.stdout.splitlines()` 逐行比對,與 test_lumos.py:2928、2994、3389 的逐行比對寫法同類。
引句:「lines = [ln.strip() for ln in r.stdout.splitlines()]」
佐證:file: /home/user/Lumos/scripts/test_lumos.py:2928;/home/user/Lumos/scripts/lumos:8783

## F1 窄接例外註解把一行拉得很長
severity: minor
blocking: 否
引句:「except (UnicodeDecodeError, OSError) as e:   # 只接「這支檔讀不了」;不學 deinit 寬接 Exception,程式錯誤照樣往外丟,不被藏成讀不了」
佐證:file: /home/user/Lumos/scripts/lumos:20897
說明:鄰居(如 scripts/lumos:19990 的 except Exception)的行尾註解多為短句,或把理由放在上方獨立註解行(19903 一帶);此處把完整理由塞進行尾。結構與做法一致,僅註解位置與鄰居略有出入,可選擇改成上方獨立註解行。判不準是否值得動,標 ⚠。

不對齊共 1 條,其中重大 0 條
