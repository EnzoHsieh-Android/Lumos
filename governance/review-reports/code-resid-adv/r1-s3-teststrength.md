# code r1 s3 testgreen-sonnet 摘錄(6 組突變實驗)
①clean: 反轉兩條斷言經全還原突變 5 條翻紅=有鑑別力;橫幅字面單獨突變→「不含枯竭」單獨翻紅;Chao1 公式突變→「6.00」數值斷言單獨翻紅。
②clean: 「枯竭 not in」非恆真(PASS 橫幅實印+rc0 前置)。
③clean(更強): 「3/3 not in」獨立守「警告有印但資料仍污染統計」——雙突變區分實證。
④major: 型別守衛只鋪 canary-stats 一處,panel/K2/cluster/CLI 四呼叫端裸奔(真實 repo 非突變重現假 0.00+警語假背書);新測試零覆蓋此面。
⑤info: cmd_loop_capture_counts 仍印「枯竭→收斂側/續跑側」二元措辭,與降級動機矛盾;測試 9196 釘舊語意;範圍刀漏項。
