severity: major

- [major] 只驗白名單內容,擋不住繞過白名單直接刪檔的人。
  引句：「    for rel in _VENDORED_TOOLKIT:」
  位置:`scripts/lumos:10894`
  why: 守衛只看這個迴圈吃到的清單。審計員完全不碰清單,在這行之前自己插一行 `if (root/"LICENSE").exists(): (root/"LICENSE").unlink()`(構造的破壞碼,不是 repo 內容),原測試 6/6 全過,什麼都沒發現。必要非充分。

- [major] 會被複製出去的檔案集合是手寫清單,跟生產邏輯對不齊。
  引句：「targets = ["scripts/test_lumos.py", "scripts/merge-claude-settings.py", "scripts/graph-rename.sh",」
  位置:`scripts/test_lumos.py:25917`
  why: 在 scripts/hooks/ 頂層(不是 claude/ 底下)新增一支沒有 SPDX 的檔,它會被 _vendor_toolchain 的 rglob 真的複製到消費專案,但手寫清單只對 hooks/claude/*.py 做動態 glob,掃不到頂層新檔 → 實測 6/6 全過。

- [major] 「MIT 全文」其實只比對兩句片語。
  引句：「"Permission is hereby granted, free of charge" in main[:4000] and "WITHOUT WARRANTY OF ANY KIND" in main[:4000]」
  位置:`scripts/test_lumos.py:25908`
  why: 把檔頭 MIT 中段(授權範圍、sublicense、須隨附本聲明的附條件、責任免除細節)整段換掉,只留那兩句,實測 6/6 全過。

- [minor] 摘要寫「其餘 12 支」,實際數到 13 支。
  引句：「其餘 12 支被複製的檔至少要有 SPDX 註解行」
  位置:`docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:13`
  why: 少算了一支 hook;靠動態 glob 沒造成漏測,但是「人手清單跟不上真實集合」的早期症狀。

- [minor] 兩條合約綁同一支測試,通過時分不出是哪一條在守。
  引句：「[test:t_license_headers_travel_with_vendored_files]」
  位置:`docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:12`
  why: 萬一其中一半斷言被誤刪,另一條合約的 [test:] 連結會看起來還在守、實際上已經不守。

AUDIT: fail — 兩條都是真合約,但綁定的同一支測試在兩條各自都能被實測繞過,不是推論,是實際跑 -k license_headers 拿到假綠證實的。
