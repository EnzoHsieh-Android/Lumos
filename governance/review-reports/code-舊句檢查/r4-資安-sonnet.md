severity: clean

# 第 4 輪 資安-sonnet(只看第 3 輪修正,73d55192)

無 finding。逐項站攻擊者一邊試過:

1. 超長行藏舊句(把名稱拆開、同形字):不能。正常掃描用的是整字正則直接比原始字串,超長行的判準是 `n in ln`(逐字子字串),比正則寬。名稱被拆開、換成同形字或零寬字元插入,兩條路都命中不了,所以收窄沒有讓攻擊者多出一條原本抓得到、現在放掉的路。名稱只要原樣出現在超長行就算 long_lines(判不了),照舊要算。逐一 `in` 也有 `_drift_m1_ticker` 看截止時間。
2. 不印照貼指令的判準漏字元類別:實跑 `_drift_fix_hint("m1", …)`。NBSP、U+3000、`$(id)`、`'; rm -rf ~ #` 這類帶引號,shlex.quote 包好,shell 不會執行。零寬 U+200B、U+2028、U+0085、私用區 U+E000、非 UTF-8 替身 U+DC80 全都轉成不印指令。剩下沒轉的只有 U+034F(Mn)這類看不見的組合字元,照貼時位元組原樣保留,會貼對,只是外觀相同,不會寫到別篇。非 UTF-8 用 U+D800(不是 surrogateescape 產生的)會讓 `_drift_c4_show_name` 拋 UnicodeEncodeError,但 git 路徑解碼只會產出 U+DC80 到 U+DCFF,走不到,不報。終端輸出 `_drift_m1_term` 實測把 U+202E 寫成看得見的跳脫、ESC 換成空白。
3. 收權限失敗不當錯之後讓別人可寫目錄被信任:不會。`_mkdir_private_layer` 只在自己剛 mkdir(mode 0700,只會被 umask 或 ACL 縮小)成功後才吞 chmod 失敗;`_mkdir_trusted_under_home` 之後仍逐層檢查非連結、是目錄、擁有者是自己、群組與其他人不可寫,`_trusted_private_dir` 也一樣,所以權限真的是別人可寫的目錄還是被擋(關閉式失敗)。
4. 留痕短寫檢查:`os.write` 回傳長度不符就回 False,跟 `_ledger_append` 同一套。無新洞。

佐證:
file: `scripts/lumos:35039`(_chmod_no_follow)
file: `scripts/lumos:28861`(_drift_m1_name_rx 整字正則,子字串必然涵蓋)

## 圖譜鏡頭逐條判定
- lumos-cli-read、bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、lumos-cli-lifecycle、design-loop 的 INVARIANT:diff 只動 drift m1 提示、doctor 行、私有目錄建立與治理帳追加,不碰 search 濾網、綁定測試閘 rc、guard kill、授權白名單、re-inject、處置閘,判不影響。
- pitfalls-code-loop(RISK):不牽涉風險分級計算,不影響。
- 其餘只列名的節點:未見這次改動接觸其行為。

最高等級:clean
