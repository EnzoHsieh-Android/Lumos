severity: minor

## F1 _strip_inline_markup 對原文含 NUL 的行跟舊版不等價
severity: minor
blocking: 否

引句:「    return mask.replace("\0", ""), cut」
佐證:`_inline_mask` 用 \0 當遮罩字元,導出 `_strip_inline_markup` 時整串 replace 把原文本來就有的 \0 也刪掉;舊版保留。
1. 輸入 `[test:a\0b]`(原文含 NUL,無反引號)。
2. 舊版回 `('[test:a\x00b]', False)`;新版走 `mask.replace("\0","")` 回 `('[test:ab]', False)`。
3. 守衛拿看得見的文字比對 `[test:ab]` 這類標籤時,舊版認不得、新版認得,判定改變。要求「跟舊版完全一樣」在含 NUL 的輸入上不成立。
實務上筆記裡有 NUL 極少見,所以只列 minor。
最小重現:/tmp/count3-work/eq.py 的 old()/new() 對 "[test:a\0b]"。其餘輸入(不含 NUL):字母表 {`, ``, a, b, 空白, \n} 長度 0–6 窮舉、長度 7–8 各 20 萬隨機、字母表 {`,``,a,換行,空白} 長度 8–20 共 100 萬隨機,新舊 0 筆不同。雙反引號「遮罩 vs 刪除」造成的相鄰湊 span 沒找到反例(`.+?` 與 `[^`\n]*` 都不跨換行、遮罩字元不是反引號,結果一致)。

## F2 _count_changed 的「綁定看名稱出現」抓不到星號 import
severity: minor
blocking: 否

引句:「        elif isinstance(nd, ast.alias):」
佐證:`from m import *` 的 alias 名稱是 "*",不等於任何名稱,所以不算一次綁定;但它可以把定義後的 X 蓋掉。docstring 宣稱「整支檔裡這個名稱的每一次出現」都算,這是名稱不出現卻綁定的漏洞;天花板節沒列。
1. 檔案 `X=(1,2)\nfrom m import *\n`,m 內也定義 X。
2. `_count_changed` 走完 ast.walk,seen=1,不觸發任何方法/下標規則,回 False。
3. `_count_eval` 回 (2, None),實際執行後 X 可能是 m 的值,數錯。
重現:/tmp/count3-work/star.py,輸出 `(2, None)`。同類(globals().update、exec)屬「不模擬」的接受限制,星號 import 是唯一一個語法上可偵測卻漏掉的,可補成 alias.name == "*" 就判不了。

## 已走過沒問題的輸入(寫在這裡供機器收貨者知道範圍)
- _count_changed 對 50 種常見寫法跑 `_count_eval`(/tmp/count3-work/h.py):字串型別註記、`__all__`、`TypeVar("X")`、docstring、f-string `{X}`、global/del 別的名稱、比較、關鍵字參數 `f(X=1)`、屬性 `os.X`、`from X import y`、`case C(X=1)`、`case a.X`、`*X` 展開、裝飾器、`except X`、元類 `metaclass=X`、`X.copy()`、`X[0]` 讀取都仍判得出;函式參數同名、for/with/海象/match 捕捉/except as/type 別名/型別參數/nonlocal/import as/`import X.sub`/lambda 參數/推導式目標/增量指派/`X.append` 都判不了。沒有大面積誤判不了。
- 漏的識別字欄位:alias、Global/Nonlocal.names、ExceptHandler.name、MatchAs/MatchStar.name、MatchMapping.rest、arg.arg、FunctionDef/ClassDef.name、TypeVar 系列 name 都被「欄位等於名稱」涵蓋;keyword.arg、Attribute.attr、ImportFrom.module、kwd_attrs 是正確略過的非綁定。
- _count_rewrite:標籤範圍含遮罩字元就擋;`[^\]]*` 跨過含 `]` 的行內程式碼時匹配含 \0 也被擋;left 從原行取位置與遮罩等長,沒找到錯位。
- 測試:`-k count_tag` 50 passed、`-k inline_visible` 1 passed。注意 t_inline_visible_single_source 的比對是 `mask.replace("\0","") == vis`,字母表不含 \0,所以測不到 F1;它也不是跟舊版公式比,只是兩個導出品互比。

圖譜判定:
- Systems/存量漂移守衛.md 的 WHY 行:未發現與程式不一致處(不含 F2 這個未列入天花板的星號 import)。
- design-loop 處置閘第五步 INVARIANT 依賴的 _strip_inline_markup:對不含 NUL 的輸入行為與舊版逐字相同(上列隨機/窮舉 0 筆差異),重構不會改變其判定;只有 F1 的 NUL 輸入例外。
- 測試假綠形態:t_inline_visible_single_source 的前置斷言沒有檢查隨機輸入真的含雙反引號與未閉合反引號的樣本數(只靠機率),翻紅釘無法證明還原時真的紅;非 finding,僅供參考。

總結:最高等級 minor
