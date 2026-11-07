severity: minor

審查摘要:這份 diff 照計劃〈範圍〉1–4 都做到了,沒有改到擋停。我沒找到會讓行為出錯或擋推送的問題,只有 5 條文件措辭與綁定上的小問題。

- **範圍逐條對:** 範圍 1 是新增 `rules-unwired/` 與只載它的 `sgconfig-unwired.yml`,8 條規則拆過去。拆完提示級剩 42 條、`rules-unwired/` 有 8 條,我用 `grep -c "^id:"` 數過,跟計劃一致。範圍 2 是 `CONFIGS`、`_DIR_SEVERITY`、`r.get("dir")` 缺鍵照不在 unwired 算,以及好例已知誤報的 `review_ids` 擴充,都有。範圍 3 的 SARIF 自檢有做,探針的壞例樣本目錄也都在。範圍 4 的文字同步,計劃列出的檔案都改了。
- **擋停沒動:** 範本沒新增宣告,`Systems/linter精選目錄` 只剩 `sgconfig-hints.yml` 那一行,diff 沒碰收工白名單、新增告警閘和分級。
- **我跑的測試:** `-k kt_rulepack_unwired` 8 條全綠,`-k kotlin_catalog` 59 條全綠,`check.py --catalog-only` 回報型錄問題 0 個。本機沒有 ast-grep,所以 SARIF 實掃和 `rulepack` 全組沒有重跑。
- **誤動 HEAD 已還原:** 我查看時手滑下了一次 `git checkout -q --detach`,HEAD 脫離了分支。我已用 `git symbolic-ref HEAD refs/heads/EnzoHsieh-Android/rulepack-review-blind-judge` 接回,HEAD 仍是 f8c89efff,沒有改任何檔案內容。

## F1 新增的 sgconfig-unwired.yml 沒有家
severity: minor
blocking: 否
引文:`引句:「`configs/ast-grep/kotlin-android/sgconfig-unwired.yml`:不接閘的規則(`rules-unwired/`,任何等級)」`
佐證: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:11` 的 `about_code` 列了 `sgconfig-hints.yml` 和 `sgconfig-review.yml`,沒有 `sgconfig-unwired.yml`。diff 對這份 frontmatter 只動了 `updated`。`lumos impact --file configs/ast-grep/kotlin-android/sgconfig-unwired.yml` 顯示它只靠 body-inline-code 關聯到這篇。
失敗場景:專案 CLAUDE.md 鐵則 5 要求每支程式檔有一篇 Systems 節點的 `about_code` 列它。這支檔沒有家,卻被別人在正文用反引號寫了。S8/S9 一類的提醒日後可能點名它,改它時系統也不會把這篇推到眼前。

## F2 型錄與 note 仍留著「靠盲判排除」的舊說法
severity: minor
blocking: 否
引文:`引句:「是這級規則已知會誤報、要靠盲判排除的寫法,自我檢查不算好例誤報」`
佐證: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:62` 保留了這句。同一份 diff 的 `check.py` 已把 `REVIEW_FP_PREFIX` 的註解改成「已知會誤報、改規則形狀時拿來對照」。
失敗場景:盲判機制這一版整組不做(計劃〈不做〉),note 卻寫 review-fp 樣本是「靠盲判排除」。下一個讀者會以為有盲判流程在接手。另外 `規則包語意覆核級命中走盲判_計劃.md:46` 與 `:139` 仍寫「出處不全只准提示級」、「不替出處不全的提示級規則補出處」。計劃的文字同步清單沒列這篇,但它還是現行文字。

## F3 [S2] 條款綁的測試沒驗「放在 rules-unwired/」這句
severity: minor
blocking: 否
引文:`引句:「引用(出處不全)列的規則 應 放在不接閘的 rules-unwired/;id 應 唯一」`
佐證: `scripts/test_lumos.py` 的 `t_kotlin_rulepack_messages_cite_catalog` 在 diff 裡只改了 docstring。它剩下的相關斷言仍是 `check("★改壞★ 非 hint 規則引用出處不全的列要被抓到"`,用的是沒有 `dir` 鍵的假規則。真正驗「放在 rules-unwired/」的是 `t_kt_rulepack_unwired_dir`,它沒綁在 [S2] 上。
失敗場景:有 `dir` 鍵的假規則(例如放在 `rules-hints/`)出了問題,這條斷言不會單獨抓到,條款綁定與它描述的行為對不上。這條斷言的名稱還停在「非 hint 規則」的舊說法。條款同時寫 severity「應 屬於 error/warning/hint」,程式實際接受四種等級(含 info),這是舊有落差。

## F4 WHY 換綁測試後,前半句失去綁定
severity: minor
blocking: 否
引文:`引句:「[test:t_kt_rulepack_unwired_dir]」`
佐證: Systems/kotlin規則包的 WHY「每列要有真的打開讀過的官方出處;查不到的列標(出處不全)」,原本綁 `t_kotlin_catalog_rows_wired`(驗 S3 型錄格式、來源與網址)。diff 把 `[test:]` 整個換成只驗「放對目錄」的 `t_kt_rulepack_unwired_dir`。這是計劃明文要求的換法。
失敗場景:WHY 前半句「每列要有官方出處」現在沒有測試綁定。日後型錄來源欄檢查被拿掉,WHY 的綁定測試仍全綠。

## F5 計劃寫「不改任何擋停」,但宣告了提示級設定的消費專案會少擋 8 條
severity: minor
blocking: 否
引文:`引句:「引用型錄出處不全列的規則(2026-11-08 從 `rules-hints/` 拆來 8 條)」`
佐證: 計劃〈實務隱患〉自己寫「`sgconfig-hints.yml` 從 50 條變 42 條,宣告了提示級的消費專案少擋 8 條」,同一篇〈不做〉卻寫「不改任何擋停」。`Systems/linter精選目錄.md:198` 說新增告警閘「不分等級、接了就擋」。diff 沒補這個行為差異的說明。
失敗場景:某個專案自己加宣告指向 `sgconfig-hints.yml`,這些規則(例:`kt-mutex-reentrant`、`kt-whilesubscribed-no-timeout`)升級後不再擋推送,而文件宣稱沒有擋停變動。這屬放寬方向、計劃已揭露,所以只算措辭不一致。

## pitfalls manifest
分級被內建風險型樣「共享狀態有沒有鎖保護」命中 `rules-unwired/coroutines.yml` 第 11 行,原因是規則文字裡有 Mutex。併發類題目在這個 repo 判範圍外,標為誤報,不計 finding。

## 固定席判定
- **Systems/kotlin規則包(無合約):** 無合約被破壞。WHY、RULE 的文字與 `check.py` 行為一致:出處不全的規則只准放 `rules-unwired/`,而且改 RULE 時同步重新 `[confirmed:2026-11-08]`。問題見 F1、F2、F4。
- **Systems/測試假綠形態 ★INVARIANT★(前置斷言證明現場成立):** 新測試 `t_kt_rulepack_unwired_dir` 有 `★前置★ 型錄有出處不全的列` 的前置斷言,翻紅釘 ①④⑤⑥ 的現場都由造的假規則成立,不違反。SARIF 兩個改壞(空結果、讀不懂)各自要求 `len(hit)==2` 且含「樣本」。這兩條必須有真的 ast-grep 才能前置驗證現場,我這邊沒有,只能靠 CI,判定為未能在本機重現。

總結:最高等級為 minor,blocking 共 0 條
