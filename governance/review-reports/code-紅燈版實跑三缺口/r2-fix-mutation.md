# r2 修補後改壞驗證(code-紅燈版實跑三缺口)

修補後的工作樹,scratchpad 的 rb_mutate_r2fix.py(由 r1 那份更新:程式改寫過的點換新字串,新增 M3 改寫、P1–P3)逐點改壞 scripts/lumos、清 __pycache__、只跑對應那支測試。30 點 29 點翻紅。

P3(單平台後綴不要求恰好一個)沒翻紅:走不到的防禦。條款指紋相符時,留痕的名字只會是某個條款名字、或「預設平台:某個條款名字」,同時吻合兩個條款名字後綴的情形要條款本身寫 [test:a:x] 這種多平台下會解析失敗的寫法,寫不出留痕;保留「恰好一個」只為了萬一,不另造測試。

```
M1 切參數不帶剝過的文字: 紅 ['9 passed, 8 failed'] ['✗ ★前置★ 含逗號的字串預期值切成兩個參數  (\'assertEquals\', [\'"服務費 $1\', \'235"\', \'label(fee)\'], [])']
M2 不判掃描可不可靠: 紅 ['4 passed, 3 failed'] ['✗ S2 assertEquals("${foo("a,b")}", x):參數跟原文切法逐字相同  ([\'"${foo("a\', \'b")}"\', \'x\'],']
M4 沒收尾不判不可靠: 紅 ['6 passed, 1 failed'] ['✗ S2 assertEquals("""a"""", x):參數跟原文切法逐字相同  ([\'"""a"""", x)\'], [\'"""a""""\', \'x)\'']
M5 留痕不帶平台: 紅 ['6 passed, 3 failed'] ["✗ S3 留痕 tests 帶平台前綴(含預設平台、名字含冒號、懸空的照樣在)  (['fee: rounds up', 'fee_jvm', 'fee_on_"]
M8 同名多平台也補: 紅 ['2 passed, 1 failed'] ["✗ S4 舊留痕:平板那支照條款補成 device、含冒號的照整串比到 jvm、同名兩個平台照預設 jvm  (['device fee_on_device',"]
M9 平台不在設定裡照崩: 紅 ['0 passed, 2 failed'] ["✗ S5 還在做:擋下、講明平台不在設定裡、沒有例外  ('', '\\n    plat, name, _explicit = _split_test_ref_"]
M10 平台不在設定裡已完成也擋: 紅 ['1 passed, 1 failed'] ['✗ S5 已完成且指紋不符:降成提醒不擋、沒有例外  ("[spec-gate 推送前] ✗ — 1 份風險低計劃沒過(風險低不派審,推送閘是它唯一的閘):\\n']
M12 沒接裝置照記逃逸: 紅 ['5 passed, 2 failed'] ['✗ S6 沒過的全是環境沒跑起來:不記逃逸  (0, 1)']
M13 真的紅也不記逃逸: 紅 ['6 passed, 1 failed'] ["✗ S6 另有一支真的紅:照擋、照記逃逸  (0, 0, '[spec-gate 推送前] ✗ — 1 份風險低計劃沒過(風險低不派審,推送閘是它唯一的閘):\\"]
M14 孤兒不問忽略: 紅 ['8 passed, 4 failed'] ["✗ S7 孤兒:一條 unreadable、講治理帳被忽略與蓋到的規則  [{'rule': 'tq/redbase-unreadable', 'file': "]
M15 孤兒身分字用整句: 紅 ['11 passed, 1 failed'] ["✗ S7 兩種措辭的放行指紋相同  ('04ee0f76c462b17b', '18235ef6d8bd4a4d')"]
M16 還沒提交不講忽略: 紅 ['10 passed, 2 failed'] ["✗ S7 還沒提交:以 git add 開頭、講治理帳被忽略  [{'rule': 'tq/redbase-unreadable', 'file': 'gove"]
M18 不用 -q 判否定規則: 紅 ['10 passed, 2 failed'] ["✗ S7 否定規則讓它沒被忽略:照舊措辭  [{'rule': 'tq/redbase-unreadable', 'file': 'governance/red"]
M19 規則不取 -v 來源: 紅 ['0 passed, 9 failed'] ["✗ S8 docs/.gitignore:判被忽略、規則指到那支檔  ('ignored', '(讀不出是哪一條)')"]
M20 規格閘不提醒: 紅 ['3 passed, 1 failed'] ['✗ S9 治理帳被忽略:多印一行(走錯誤輸出,同規格閘其他留痕寫不進帳的提醒)']
M21 doctor 不唸: 紅 ['1 passed, 1 failed'] ['✗ S10 治理帳被忽略:doctor 唸  h-discipline.md 範本,略過 Check D)']
M22 孤兒不要刪放後面: 紅 ['9 passed, 3 failed'] ["✗ S7 孤兒:一條 unreadable、講治理帳被忽略與蓋到的規則  [{'rule': 'tq/redbase-unreadable', 'file': "]
N1 搬家也用保留字串的簽名: 紅 ['15 passed, 2 failed'] ["✗ S1 搬進巢狀類別、本體有多行字串:不列 tq/test-removed  [('tq/test-removed', 'app/src/test/java/"]
N3 還沒提交改回叫人看孤兒那條: 紅 ['11 passed, 1 failed'] ['✗ S7 還沒提交:自帶改法與自查指令,不叫人去看另一條  規格閘紅燈版讀不到、沒提交、被刪、被改過或沒有留痕指到(規格閘紅燈版 ?:git add 這支紅燈版']
N4 剝過那條不跳過括號內部: 紅 ['6 passed, 1 failed'] ["✗ S2 沒有字串時兩條切法相同:'{}[b,,]b(),{}{}a b[]b()'  (['{}[b,,]b()', '{}{}a b[]b()'], ['{"]
N5 angle 也走剝過那條: 紅 ['6 passed, 1 failed'] ["✗ S2 angle=True 時不走剝過文字那條路(配括號表沒有 < >)  ['a<b', 'c>', 'd']"]
N7 規格閘提醒改走標準輸出: 紅 ['3 passed, 1 failed'] ['✗ S9 治理帳被忽略:多印一行(走錯誤輸出,同規格閘其他留痕寫不進帳的提醒)']
M3 只差空白版面一律不判: 紅 ['16 passed, 1 failed'] ['✗ S1 串接逗號空白:只改字串預期值要列 tq/expected-changed  []']
P2 只差空白版面照舊全部重判: 紅 ['16 passed, 1 failed'] ["✗ S1 整檔重新縮排、沒斷言的測試有多行字串:不列 tq/no-assertion  [('tq/no-assertion', 'app/src/test/j"]
M6 舊留痕不補平台: 紅 ['1 passed, 2 failed'] ['✗ S4 舊留痕:平板那支照條款補成 device、含冒號的照整串比到 jvm、同名兩個平台照預設 jvm  ([], "[spec-gate 推送前] ✗ —']
M7 過期也補平台: 紅 ['2 passed, 1 failed'] ["✗ S4 已完成而指紋不符:不補平台,平板那支沒走 device  (['jvm fee_jvm', 'device fee_on_device', 'jvm "]
N2 單平台不認條款名字後綴: 紅 ['8 passed, 1 failed'] ["✗ S3 改回單平台:jvm:fee_jvm 照名字 fee_jvm 跑綠、放行、不記逃逸  (1, [], True, '✓ 逃逸自動入帳:「甲」在 push"]
N6 環境樣式判不出: 紅 ['0 passed, 7 failed'] ['✗ S6 實作前沒接裝置:平板那條判弱證據並寫環境沒跑起來  [spec-gate] 計劃風險: 低(硬訊號都沒命中;四類已排除,「」裡是計劃裡寫的字:金流=「']
P1 拿掉 java-junit 那一項: 紅 ['6 passed, 1 failed'] ['✗ S6 Java 專案沒接裝置:判弱證據並寫環境沒跑起來  [spec-gate] 計劃風險: 低(硬訊號都沒命中;四類已排除,「」裡是計劃裡寫的字:金流=「']
P3 單平台後綴不要求恰好一個: 綠(沒抓到) ['9 passed, 0 failed'] []
```
