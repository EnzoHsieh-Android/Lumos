severity: minor

背景跑的 `-k choice_layer` 已跑完,62 支全過,補上上一則沒驗到的那一項。結論不變:沒有 blocking 級問題。

severity: minor
blocking: 否
`scripts/lumos` 的 `_choice_layer_not_body`:整個標題就是 `〈審計修正紀錄〉` 時,拿掉交叉引用後標題變空字串,被判成計劃正文,審計紀錄會進第 2 層的引用範圍。
重現:`_choice_layer_not_body("〈審計修正紀錄〉")` 回 `False`。
repo 裡目前沒有這種真標題,只是極端輸入沒蓋到。
引句:「「審計修正紀錄外篇」也排除是明文取捨:審計紀錄混進正文會讓第 2 層引審計句子,反過來漏掉一節正文代價較小。」

severity: minor
blocking: 否
`scripts/lumos` 的 `_CHOICE_LAYER_XREF_RE`:沒閉合的 `〈` 排在後面另一組 `〈x〉` 之前時,第一個 `〈` 會一路吃到後面的 `〉`,把中間的「審計修正紀錄」一起拿掉。
重現:`_choice_layer_not_body("〈審計修正紀錄 〈x〉")` 回 `False`,按規則①應該是 `True`。
引句:「_CHOICE_LAYER_XREF_RE = re.compile(r"〈[^〉]*〉")」

總結:最高等級是 minor
