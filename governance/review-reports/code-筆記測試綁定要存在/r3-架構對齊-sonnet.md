severity: minor

## 問一:分層與依賴方向
對齊。_ns_tr_collect 抽成模組層函式,放在 _ns_test_refs_collected 之前,只吃 touched 與 judge,不跨層;_ns_tr_extra_merged 仍由 _ns_skip_slot_extra、_note_shape_report 兩個呼叫端使用,方向跟 _ns_slot_extra 同(scripts/lumos:28412)。_submodule_hit 只動 self.st,跟 _out_of_time(scripts/lumos:28834-28841)同一個狀態面。

## 問二:命名與錯誤處理
對齊。_ns_tr_extra_merged 回新 dict、不改傳入值,跟 _ns_slot_extra 回新 dict 同款(28412);舊名 _ns_tr_add_extra 已全部換掉(grep 只剩 28151、29231 兩處新名)。子模組清單逾時改成設 st["out"]=True 加一句 notes,跟 _judge 的 TimeoutExpired 分支(28893-28896)一致,只是句子不帶名稱(此處不在單一名稱內),合理。

## 問三:第二種做法
有一處輕微:整字比對與冒號正規化。
- 整字比對本身:新寫的 (?<![\w])…(?![\w]) 跟全檔 31651、31738 的寫法一字不差,也近似 8962 的 (?<!\w)…(?!\w),屬既有主流;但 _keys_mentioned(35819)的 docstring 自稱「整字比對的唯一定義」且用 ASCII 邊界,所以全檔其實已有兩套邊界。這次是沿用 \w 那套,沒有新增第三套,但也沒抽共用。
- 冒號正規化:_ns_tr_is_new 內嵌 re.sub(r"\s*[:：]\s*", ":"),是在整行文字上做,而 _test_names_of(28643)是靠 _NS_TR_PREFIX_RE 只對前綴做。同一個「全形冒號、冒號後空白」規矩有兩份實作,且新的作用在整行(會連行內其他冒號一起改),不是只動前綴。結構是對的,但是另寫一套。

## F1 冒號正規化另寫一套、沒重用 _NS_TR_PREFIX_RE
severity: minor
blocking: 否
引句:「原文的全形冒號與冒號後空白先照 _test_names_of 的規矩正規化」
佐證行 ``file: `scripts/lumos:28643` `` (_test_names_of 用 _NS_TR_PREFIX_RE 只正規化前綴)
1. 被審處 scripts/lumos:28788-28791 自帶內嵌 re.sub,註解說「照 _test_names_of 的規矩」卻沒呼叫同一個常數或函式;日後前綴規則改了兩處會漂。
2. 建議抽小函式或直接重用 _NS_TR_PREFIX_RE。

## F2 整字邊界又手寫一份(⚠ 判不準是否算第二種做法)
severity: minor
blocking: 否
引句:「pat = re.compile(r"(?<![\w])" + re.escape(nm) + r"(?![\w])") if nm else None」
佐證行 ``file: `scripts/lumos:31651` `` (同寫法的既有處;另 35819 _keys_mentioned 自稱唯一定義、用 ASCII 邊界)
1. 寫法與 31651、31738 一致,故不算 major;但全檔整字比對已有 \w 與 ASCII 兩派,這次是再多一個內嵌點。
2. ⚠ 因 _keys_mentioned 的邊界(ASCII)對 CJK 名稱不同語意,沿用 \w 是否刻意要在註解說一句。

不對齊共 2 條,其中 major 0 條
