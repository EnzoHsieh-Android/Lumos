# r4 修補後改壞驗證(2026-11-03)

每道只改 scripts/lumos 一處、清 __pycache__、跑 `python3.14 scripts/test_lumos.py -k redbase`、還原。上一輪 14 道(M7 換成新措辭的寫法)加這輪 4 道(N1–N4),18 道最後全數翻紅。
N1 就是本輪單審席 C1 點的那一道(留痕還在、檔被刪時不核對 sha256):r3 的改壞清單沒有它,改壞後 141 條照綠;補兩案後翻紅。
第一次跑 M13(標題改回沒辦法比)沒翻紅:這輪把提醒內文改成「改拿哪一版來比」,舊斷言找的「已照」不再出現;斷言改成同時認新措辭後重跑翻紅。

## 第一次跑(18 道)

```
M1 孤兒照樣接進鏈: 紅 ['143 passed, 3 failed'] ["✗ S3 r3 孤兒骨架 + 有留痕的 900:列 900 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable', 'file': 'gov", "✗ S3 r3 孤兒不接進鏈:不出現倒著比的「第 N 份紅燈版」  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/r"]
M2 孤兒不另跟推送版比: 紅 ['142 passed, 4 failed'] ["✗ S3 r3 兩個孤兒(骨架是 SPEC-00000001):照樣列 900 那份 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable',", "✗ S3 r3 兩個孤兒(骨架是 SPEC-ffffffff):照樣列 900 那份 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable',"]
M3 拿掉 --no-renames: 紅 ['143 passed, 3 failed'] ["✗ ★前置★ 骨架那份真的被列成被刪  [{'rule': 'tq/redbase-weakened', 'file': 'app/src/test/java/x/CalcTest", '✗ S4 r3 刪舊加相近的新檔(會被配成改名):刪掉的照樣列  []']
M4 拿掉終點還活著的過濾: 紅 ['145 passed, 1 failed'] ["✗ S4 r3 刪了又加回:不算被刪  [('a99c329434baf3d341ec7f92a496560b651167ed', 'governance/redbase/甲/SP"]
M5 拿掉起點就有的過濾: 紅 ['145 passed, 1 failed'] ["✗ S4 r3 主線就有的紅燈版在分支被刪:不列  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/redbase/甲"]
M6 留痕還在被刪仍另列: 紅 ['143 passed, 3 failed'] ["✗ S4 r3 留痕還在、檔被刪:照刪掉前的內容比出改弱  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/redba", "✗ S3 r4 留痕還在、檔被刪的那一份照行序接在鏈裡:列第一份 → 第 2 份紅燈版  [{'rule': 'tq/redbase-unreadable', 'file': 'g"]
M7 指紋帶提交編號: 紅 ['145 passed, 1 failed'] ["✗ S4 r3 被刪那條的指紋不隨刪掉它的提交編號變  (['9d757324226b0e20'], ['f84376cd20a84b1f'])"]
N1 留痕還在被刪不核對指紋: 紅 ['143 passed, 3 failed'] ["✗ S3 r4 留痕還在、檔被刪的那一份照行序接在鏈裡:列第一份 → 第 2 份紅燈版  [{'rule': 'tq/redbase-unreadable', 'file': 'g", "✗ S4 r4 留痕還在、檔被刪,刪掉前那一版被改過:照留痕核對、列 sha256 對不上  [{'rule': 'tq/redbase-unreadable', 'file': "]
N2 留痕還在被刪改讀頂端: 紅 ['142 passed, 4 failed'] ["✗ S4 r3 留痕還在、檔被刪:同一支只列一條 unreadable  [{'rule': 'tq/redbase-unreadable', 'file': 'governanc", "✗ S4 r3 留痕還在、檔被刪:照刪掉前的內容比出改弱  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/redba"]
N3 被刪提醒改回已照: 紅 ['145 passed, 1 failed'] ["✗ S4 r4 那一版沒拿來比時,訊息不說已經照內容比過  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/redba"]
N4 身分字串不用穩定字: 紅 ['145 passed, 1 failed'] ["✗ S4 r3 被刪那條的指紋不隨刪掉它的提交編號變  (['9d757324226b0e20'], ['f84376cd20a84b1f'])"]
M8 git log 讀不出回空: 紅 ['144 passed, 2 failed'] ['✗ S4 r3 查刪掉紀錄時 git 讀不出:回 None 不回空清單  []', '✗ S4 r3 查刪掉紀錄時 git 讀不出:整段回錯誤  ([], None)']
M9 查大小讀不出回空: 紅 ['145 passed, 1 failed'] ['✗ S4 r3 查刪掉的檔還在不在時 git 讀不出:回 None 不回空清單  []']
M10 只認第一欄的 A: 紅 ['145 passed, 1 failed'] ['✗ S4 r3 git add -N 的紅燈版也算還沒提交  set()']
M11 孤兒只認新增狀態: 紅 ['145 passed, 1 failed'] ['✗ S4 r3 孤兒檔在改動清單裡被配成改名:照樣列成孤兒  []']
M12 loose 一律 False: 紅 ['142 passed, 4 failed'] ["✗ S3 r3 孤兒骨架 + 有留痕的 900:列 900 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable', 'file': 'gov", "✗ S3 r3 孤兒不接進鏈:不出現倒著比的「第 N 份紅燈版」  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/r"]
M13 標題改回沒辦法比: 綠(沒抓到) ['146 passed, 0 failed'] []
M14 被刪偵測讀不出不回錯: 紅 ['145 passed, 1 failed'] ['✗ S4 r3 查刪掉紀錄時 git 讀不出:整段回錯誤  ([], None)']
```

## 改斷言後重跑 M13

```
M13 標題改回沒辦法比: 紅 ['145 passed, 1 failed'] ["✗ S4 r3 訊息不同時說沒辦法比又說拿內容來比 ..."]
```
