severity: major

我在 repo 裡把 `_choice_layer_split` 用假的 render 跑過,下面第一條可以重現。其餘資源問題看過,沒有發現新洞。

severity: major
blocking: 是
`scripts/lumos:81392` 一帶的 `_choice_layer_one_part`:判斷「共用的計劃材料本身就超過」時,用的是 `render(chunk[:1], False)`。這份材料裡還包含第一個存活自己的「包住那一行的宣告」原文,所以只要第一個存活自己的宣告就超過 200KB,就會被誤判成計劃材料太大。結果整個 chunk(最多 20 個存活)不再減半,每個存活的大宣告都帶進同一份。上一輪的舊寫法會把這種情況減到 1 個存活一份。
重現:假的 render 讓每個存活佔 250KB、計劃材料幾乎為零,再呼叫 `_choice_layer_split([(None, list(range(20)))], render)`。結果是 20 個存活合成一份、約 5.1MB,原因欄位還標成「涉及計劃的條款與預期值表本身就超過上限」。位元組上限 `_CHOICE_LAYER_PART_BYTES` 因此完全擋不住,判讀代理拿到的材料會被截斷。
引句:「if _choice_layer_over(render(chunk[:1], False)):   # 共用的計劃材料本身就超過:減半也縮不下來」
修法方向:判斷共用計劃材料時,改用不含任何存活的 render(空清單)。

其餘我檢查過的位置,沒有發現會做出錯行為的問題:
- `_choice_compile_suspects` 把每批單獨確認限在 8 個,所以編譯次數有上限。被擠掉的嫌疑不記無效、照舊交給測試階段。
- `_choice_layer_write` 的預檢沒有二次方。每份判讀檔在預檢前只組一次,`_note_audit_write_verdict` 之後會再序列化一次,是線性的兩倍,而且用同樣的 `indent=1`、`sort_keys=True`,大小判斷一致。
- 旁檔用計劃路徑雜湊命名、各份共用(`sides` 集合只寫一次),`_choice_layer_prune` 照一般檔清理,所以不會長出無限多檔,也不會留下清不掉的檔。
- `_choice_layer_template` 的 render 次數是份數乘上一個固定倍數,沒有二次方。

總結:最高等級是 major
