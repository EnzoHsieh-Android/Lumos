severity: minor

審查範圍:`r1-snapshot.patch` 全份(程式、測試、文件)。三類都逐項看過。

**①提示注入:已看,無。**
- 新增的名稱字元(空白、引號、`$`、反引號、分號)只進測試集合和印給人貼的指令,沒有進給 AI 的派工詞或 hook 附加段。
- 換行、行分隔符、雙向控制字元和其他控制字元,都被 `_test_name_ok` 擋掉。

**②讀寫與執行越界。** 名稱走到 shell 的每條路都有引號,已看,無破口。
- `_run_cmd_expand` 對 `{method}` 先 `_name_filter_escape`,再 `shlex.quote`。
- 配方提醒、`guard settle` 補救指令、`guard bind` 建議指令都改走 `_kill_cmd_arg`。
- 以 `-` 開頭的名稱被 `_test_name_ok` 擋掉,不會被當選項。
- 名稱含 `[`、`]`、`,`、換行都不收,寫進筆記的 `[test:…]` 跳不出欄位。
- 正規式跳脫涵蓋 `.*+?^${}()|[]\/`,逐字元處理,反斜線自己也跳。
- 新增的正規式(`_JS_TITLE_LIT`、`_ns_wd_binding_norm`、`_test_name_boundary_re`)沒有注入面。
- 沒看到新增的密鑰、信箱、下載網址,也沒有執行不可信位置的檔。

**③非刻意繞過的守衛。** 有兩條 minor 的發現。

1. 
severity: minor
blocking: 否
引句:「cmd = cmd.replace("{method}", _shlex.quote(_name_filter_escape(method, name_filter)))」
- 攻擊路徑(推論,Windows 限定):
  - 誰:別人 repo 的測試檔作者,或被誘導 clone 該 repo 的使用者。
  - 從哪:測試標題 `x & calc & y`,經掃描收進測試集合後被綁定。
  - 送什麼:`_test_name_ok` 現在放行 `&`、`|`、`"`、`%`。
  - 拿到什麼:`_IS_WIN` 時 `{method}` 仍用 `shlex.quote`(單引號),cmd.exe 不認單引號,`&` 會被當指令分隔,在跑測試時多執行一條指令。
- 舊的識別字白名單原本擋掉這條路,這份 diff 放寬後才打開。
- 只算 minor:`{python}` 同一函式裡已有 Windows 專用的引號分支,`{method}` 沒有。我看到的啟動點是 `Popen(shell=True, start_new_session=True)`,後者是 POSIX 專用,Windows 上整個閘多半本來就不可用,所以我判成縱深防禦。

   ``file: `scripts/lumos:19498` ``

2. 
severity: minor
blocking: 否
引句:「已知限制:JS 的正規表示式字面(`/'/`)會被當成字串開頭。」
- 攻擊路徑(第 1、3 件不用刻意:使用者或 AI 平常改測試檔就會碰到):
  - 誰:照常改測試檔的使用者或 AI。
  - 從哪:測試檔裡先有一個含單引號的正規式字面,例如 `.replace(/'/g, "")`,後面緊接被註解掉的 `// it('舊測試', …)`。
  - 送什麼:`c-style-strings-kept` 單趟剝註解把 `/'` 當成字串開頭。這個字串在註解裡的下一個 `'` 才結束,所以 `//` 落在字串內,註解沒被剝掉,已被註解掉的測試名被收進測試集合。
  - 拿到什麼:`guard bind` 可以綁到不存在的假測試名。
- 影響被收窄:推送前閘還要看到 `N passed` 的跑過證據,真跑會對不到,多半判證不出而不是綠,所以只算 minor。
- 這個限制 diff 自己已承認,但沒有機械守衛。

   ``file: `scripts/lumos:6353` ``

另外有兩點供參考,不算發現:
- `_name_filter_collisions` 只比對掃得到的標題。含半形逗號或方括號、樣板帶 `${`、`test.each` 產生的標題被排除在集合外,撞名檢查看不到它們。
- 若綁定的是被 `skip` / `todo` 的測試,而另一支沒被掃到、名稱包含它的測試剛好通過,`-t` 或 `-g` 的子字串比對會印出 `N passed`,閘可能判綠。
- 兩個前提都要同時成立,我沒找到能直接觸發的一步,所以不單獨列。

最嚴重 severity:minor;blocking 共 0 條。
