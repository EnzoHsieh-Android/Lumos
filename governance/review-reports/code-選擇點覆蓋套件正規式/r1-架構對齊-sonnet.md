severity: major

**1. 分層與依賴方向**
改動只在 `_choice_cov_req` 裡把一條行內正規式換掉,沒有新增依賴,也沒有跨層呼叫。但同一個檔裡已有一支共用的預編譯常數 `_CHOICE_COV_PKG_RE`(`scripts/lumos:79799`),專門讀同一類資料:Kotlin 和 Java 的 package 宣告。它處理了 BOM(`\ufeff`)和反引號。`_choice_cov_src_pkgs` 就用它(`scripts/lumos:79833`)。這份 diff 另外手寫一條不能處理 BOM 和反引號的行內版本,造成選擇點覆蓋這條路徑內部有兩種讀 package 的做法。同一條路徑上,`_choice_cov_src_pkgs`(用平台主程式全部 package 判覆蓋可信)與 `_choice_cov_req`(給壞法行指定要看的 package)讀出的 package 字串,對帶 BOM 或反引號的檔可能不一致。

引句:「+    m = re.search(r"^[ \t]*package[ \t]+([\w.]+)", text, re.M)」
severity: major
blocking: 是

**2. 命名與錯誤處理**
- 命名:沒有新增識別名,沒有不一致。
- 錯誤處理:`m` 為 None 時退成空字串的寫法,跟 `_choice_cov_src_pkgs` 的 `if m else ""` 一致(`scripts/lumos:79834`)。
- 輸入來源:`_choice_cov_req` 讀的是整份 `text`,`_choice_cov_src_pkgs` 讀的是限長的檔頭 `head`。這是來源不同,不算不一致。
- 反引號:`_choice_cov_src_pkgs` 讀出後會 `.replace("`", "")`,`_choice_cov_req` 沒有。這是第 1 問那件事的後果,不另列。

**3. 第二種做法**
這條就是第二種做法,而且不只一種。

- 鄰居 `_rg_package`(`scripts/lumos:53970`)寫成 `^[ \t]*package\s+([\w.]+)`,用 `\s+`;這份 diff 改成 `[ \t]+`,同一個專案裡出現兩種空白寫法。
- 專案裡最接近的做法是共用常數 `_CHOICE_COV_PKG_RE`,這份 diff 沒用它,又寫了一條行內版本。
- 這份 diff 附的 PITFALL 筆記說「改成鄰居同款」。實際上沒有一個鄰居同款:一個是 `\s+` 行內,一個是含 BOM 與反引號的預編譯常數,這份 diff 是第三種。筆記的描述跟實際對照結果不符。
- 守衛測試 `t_no_multiline_caret_whitespace_star`(`scripts/test_lumos.py:115119`)只擋 `^\s*` 加多行旗標。直接改用 `_CHOICE_COV_PKG_RE.search(text)` 一樣能過守衛。

引句:「[根因:\s* 搭多行旗標會吞換行(全檔守衛禁止),寫的時候沒照鄰居 package 讀法] [修法:改成鄰居同款 ^[ \t]*package[ \t]+ 加 re.M]」
severity: major
blocking: 是

不對齊共 2 條,其中 major 2 條
