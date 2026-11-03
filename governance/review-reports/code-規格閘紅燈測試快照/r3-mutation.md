# r3 修補後改壞驗證(2026-11-03)

每道只改 scripts/lumos 一處、清 __pycache__、跑 `python3.14 scripts/test_lumos.py -k redbase`、還原。14 道最後全數翻紅。
第一次跑有兩道沒翻紅,補測試後重跑翻紅:
- M9(查刪掉的檔還在不在時讀不出回空):原本沒有案例走到這條路;補一個把批次查大小換成讀不出的案例(附前置斷言:那個 repo 真的有分支刪掉的紅燈版)。
- M11(孤兒檔只認新增狀態):原本的情境不成立——改動清單是起點對終點比,舊檔不在起點時新檔只會是新增、配不成改名;改成主線就有的舊紅燈版被刪、同時加相近的孤兒檔,並加前置斷言確認新檔在改動清單裡是改名。

## 第一次跑(全部 14 道)

```
M1 孤兒照樣接進鏈: 紅 ['135 passed, 3 failed'] ["✗ S3 r3 孤兒骨架 + 有留痕的 900:列 900 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable', 'file': 'gov", "✗ S3 r3 孤兒不接進鏈:不出現倒著比的「第 N 份紅燈版」  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/r"]
M2 孤兒不另跟推送版比: 紅 ['134 passed, 4 failed'] ["✗ S3 r3 兩個孤兒(骨架是 SPEC-00000001):照樣列 900 那份 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable',", "✗ S3 r3 兩個孤兒(骨架是 SPEC-ffffffff):照樣列 900 那份 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable',"]
M3 拿掉 --no-renames: 紅 ['136 passed, 2 failed'] ["✗ ★前置★ 骨架那份真的被列成被刪  [{'rule': 'tq/redbase-weakened', 'file': 'app/src/test/java/x/CalcTest", '✗ S4 r3 刪舊加相近的新檔(會被配成改名):刪掉的照樣列  []']
M4 拿掉終點還活著的過濾: 紅 ['137 passed, 1 failed'] ["✗ S4 r3 刪了又加回:不算被刪  [('25685287e260a60d3abdc6a112f82f2abf26f32a', 'governance/redbase/甲/SP"]
M5 拿掉起點就有的過濾: 紅 ['137 passed, 1 failed'] ["✗ S4 r3 主線就有的紅燈版在分支被刪:不列  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/redbase/甲"]
M6 留痕還在被刪仍另列: 紅 ['137 passed, 1 failed'] ["✗ S4 r3 留痕還在、檔被刪:照刪掉前的內容比出改弱  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/redba"]
M7 指紋帶提交編號: 紅 ['137 passed, 1 failed'] ["✗ S4 r3 被刪那條的指紋不隨刪掉它的提交編號變  (['0a9ab6d3436af04f'], ['acceef46fdc70ddf'])"]
M8 git log 讀不出回空: 紅 ['136 passed, 2 failed'] ['✗ S4 r3 查刪掉紀錄時 git 讀不出:回 None 不回空清單  []', '✗ S4 r3 查刪掉紀錄時 git 讀不出:整段回錯誤  ([], None)']
M9 查大小讀不出回空: 綠(沒抓到) ['138 passed, 0 failed'] []
M10 只認第一欄的 A: 紅 ['137 passed, 1 failed'] ['✗ S4 r3 git add -N 的紅燈版也算還沒提交  set()']
M11 孤兒只認新增狀態: 綠(沒抓到) ['138 passed, 0 failed'] []
M12 loose 一律 False: 紅 ['134 passed, 4 failed'] ["✗ S3 r3 孤兒骨架 + 有留痕的 900:列 900 → 推送版的預期值被改  [{'rule': 'tq/redbase-unreadable', 'file': 'gov", "✗ S3 r3 孤兒不接進鏈:不出現倒著比的「第 N 份紅燈版」  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/r"]
M13 標題改回沒辦法比: 紅 ['137 passed, 1 failed'] ["✗ S4 r3 訊息不同時說沒辦法比又說已照內容比  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/redbase/"]
M14 被刪偵測讀不出不回錯: 紅 ['137 passed, 1 failed'] ['✗ S4 r3 查刪掉紀錄時 git 讀不出:整段回錯誤  ([], None)']
```

## 補測試後重跑 M9、M11

```
M9 查大小讀不出回空: 紅 ['140 passed, 1 failed'] ['✗ S4 r3 查刪掉的檔還在不在時 git 讀不出:回 None 不回空清單  []']
M11 孤兒只認新增狀態: 紅 ['140 passed, 1 failed'] ['✗ S4 r3 孤兒檔在改動清單裡被配成改名:照樣列成孤兒  []']
```
