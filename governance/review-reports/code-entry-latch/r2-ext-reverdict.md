# code r2 外家複判席

否決不成立
1. A 已鎖住:注錯 _el_related_nodes 後驗 rc、逐鍵 JSON(排除隨機 canary_type)及無 related_nodes;B 亦驗 rc=0、檔案落地與 ✓ new,符合 r1 要求。
2. 未見修正批新引入的致命缺陷;兩條產品路徑皆在副作用前捕捉 advisory 例外,A 保持既有輸出、B 繼續建檔。
3. 唯一小漏:未注錯驗文字模式 A,且不涵蓋 SystemExit;指定的普通內部例外 fail-open 合約已有實質紅釘,不足以續判 major。

severity: minor
