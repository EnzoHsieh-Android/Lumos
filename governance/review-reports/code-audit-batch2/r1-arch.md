severity: major

- [major] 同源三份清單的第三份 post-commit 沒跟,而它自己的檔頭明寫兩邊要完全對齊,否則會出現幽靈 bypass。
  位置:`scripts/hooks/pre-commit:140`
  引句：「docs/*|governance/*|*/node_modules/*|*/bin/*|*/obj/*|*/.git/*|*/dist/*|*/build/*|*/__pycache__/*) return 0;;」
  why: post-commit 檔頭寫「判定邏輯與 pre-commit 完全對齊…兩邊認定不一致會產生幽靈 bypass 或漏記」,而它的 should_exclude 仍是舊版沒有 governance/*。既有漂移守衛只拿 delguard 的清單去比對 pre-commit,完全沒碰 post-commit,所以這個漏同步沒有任何測試會紅。

- [major] doctor 收尾行新增的子句,符號與指令擺法都跟該檔既有輸出慣例、以及「工具輸出白話三段式」的長期標準不一致。
  位置:`scripts/lumos:1943`
  引句：「另有 {cnt}提醒沒算進 issues——它們不影響這行的判定,」
  why: 該檔既有行首符號只有 ✓、⚠、—,「·」是全檔第一次出現。更關鍵的是「指令獨立一行」——既有做法是 warn/warn_soft 的 advice 各自印成獨立一行,這裡把指令用分號接在句尾。長期標準明寫「發生什麼→為何在意→指令獨立一行」,兩點都分岔。

- [minor] 子行程注入用 argv 傳逗號串,比嵌字面量更繞也更脆。
  位置:`scripts/test_lumos.py:368`
  引句：「patch = ("m._RETIRED_STUB_CLAUDE_HOOKS = tuple(sys.argv[3].split(','));" if stub_names else "")」
  why: 同檔既有兩種先例(in-process 直接賦值配 try/finally 還原;組合碼字串丟 subprocess -c)。這裡屬後者的延伸,不算新機制;但用 split(',') 傳清單假設檔名不含逗號,比直接嵌 tuple 字面量脆。

其餘 clean:治理事件 note 加 soft= 欄位與既有 key=value 慣例一致,查過所有解析點沒有嚴格結尾比對;兩階段撤除照既有慣例(2026-08-22 進 STUB、2026-09-06 移 DELETE,間隔約兩週),留空 tuple 型別不變、下一支要撤的照樣加得進去;圖譜節點結案格式(status 改 superseded + 篇尾結案散文段)跟既有被結案節點一致,decisions 維持 valid 合理(結案理由是評估對象消失,不是設計決策被推翻),vault 內沒有殘留懸空引用,方法論文件也同步標了已撤除。
