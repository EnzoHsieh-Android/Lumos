severity: clean

**1. 分層與依賴方向**

這份修補沒有新增跨層呼叫。`.git` 的判斷仍留在 `_KillCompile.units()` 內,只用到 `os`、`Path`,沒有新引入依賴。測試改動也留在原來的 `t_choice_compile_units_guards`,透過同一個 `_ckcc_unit` 建構,沒有另開入口。對照 `scripts/lumos:14917` 與 `scripts/lumos:74324`:這兩處都是在呼叫處內聯做小寫比對,沒有抽成共用函式,所以這裡也內聯,層次一致。

**2. 命名與錯誤處理**

判法對齊了。`scripts/lumos:14917` 用 `parts[0].lower() == ".git"`,`scripts/lumos:74324` 用 `any(sg.lower() == ".git" for sg in segs)`,新寫法是路徑每一段先轉小寫再比對 `.git`,語意相同。錯誤處理沒有變:命中就 `continue` 略過,與兩處鄰居(回 `None`)的「拒收」語意同向。行尾註解說明「不分大小寫的檔案系統」,跟周圍的行尾註解風格一致。

日期型 REVISIT 的格式為 `REVISIT:YYYY-MM-DD 一句要做什麼`,與同層 `Systems/` 的 `REVISIT:2027-05-15 …`(`規格閘.md:81`)、`REVISIT:2027-01-15 …`(`規格閘.md:82`)、`測試執行器.md:25`、`每輪修補差異派工.md:21` 一致。已拿掉 `[when-symbol:…][by:…]` 括號,沒有殘留混合形狀。

**3. 第二種做法**

沒有引入第二種做法。`".git" in (x.lower() for x in …)` 與 `any(sg.lower() == ".git" for sg in segs)` 寫法略不同,但都是「逐段小寫後比對」同一套判法,屬純風格,不列。

審材外另有一處需讓第三段收尾時知道:`scripts/lumos:80252` 的 `s not in _CHOICE_COV_SRC_SKIP`(集合含 `.git`)仍是區分大小寫的精確比對。這是既有寫法,不在這次 diff 內,所以不算本輪新引入的不一致。Issue 第 14 條仍寫著「擋 .git 沒進共用路徑判法」,這次修補沒有宣稱已統一,所以筆記沒有說謊。

不對齊共 0 條,其中 major 0 條
