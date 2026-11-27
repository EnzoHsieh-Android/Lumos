severity: clean

上一輪的修補通過驗收:`units()` 現在先把路徑每段轉小寫,再比對 `.git`。我只讀了 diff 並用 grep 對照,沒有跑測試。

- **修到沒**:`.GIT` 這類大小寫變體現在會被擋下。`".git" in (x.lower() for x in ...)` 的寫法正確。新增的測試案例 `sub/.GIT/y.kt` 會被排除,斷言 `got == ["A"]`。
- **新問題**:沒有。轉小寫只是對少數幾段路徑各做一次,沒有子程序、快取或二次方工作,對資源沒有影響。
- **同類位置**:repo 裡 `.git` 的判法另外有三處,各自的做法如下。
  - `scripts/lumos:14917` 用 `parts[0].lower()`。
  - `scripts/lumos:74324` 用 `sg.lower()`。
  - `scripts/lumos:39792` 比的是 `common.name`,是別的用途。
  - `_kill_merge_apply` 沒有 `.git` 檢查。這點上一輪的 Issue 第 14 條已記為第三段收尾前處理,而且只是不一致,不會讓行為出錯。
- **規格閘 REVISIT**:改成日期型 `REVISIT:2027-03-01`,寫法合規。

總結:最高等級是 clean
