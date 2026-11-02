# 代碼審通過後、推送前全套測試抓到的問題(2026-11-02)

第九輪處置閘通過、留痕之後,推送前的全套測試紅了 6 支。6 支在基準版本(047031883)上全綠,都是這次改動造成的。依根因分四組,都照專案既有做法修,沒有新增機制。

| 組 | 紅的測試 | 根因 | 修法 |
|---|---|---|---|
| 舊版 Python 載入 | t_lumos_module_level_regex_loads_on_old_python、t_lumos_old_python_reexec_or_explain、t_hook_event_timestamp_roundtrips_on_old_python | 字串常值與常數兩條正規式在模組層用佔有式量詞編譯,3.11 以前的直譯器一載入就崩 | 照 _C_STRIP_PAT 的做法只存樣式字串,用時才經 _lazy_re 編譯(_TG_LIT_PAT、_TG_CONST_PAT) |
| 多行旗標配 ^\s* | t_no_multiline_caret_whitespace_star | 認斷言訊息位置的 import 樣式寫成 ^\s* 搭 re.M,\s 會吃換行,大段空行二次方回溯 | 改成 ^[ \t]* |
| 名字撞名 | t_slim_gen | 健康檢查新加的迴圈變數 _say 跟代碼審的內部函式同名,精簡產物產生器只按名字收閉包,把代碼審整條路徑收進產物 | 迴圈變數改名 _what;產生器弱點另開文件提交,寫進 Systems/slim-gen-生成器 的 PITFALL 與 REVISIT |
| 佔位符白名單過期 | t_lint_files_substitution_has_one_implementation | 「命令有沒有佔位符」的檢查從 _lint_new_verdict 拆到 _lint_new_run_cmds,白名單沒跟著換 | 白名單換成 _lint_new_run_cmds,註明來由 |

另外,推送前回頭重讀守檔筆記時,Room 守衛那席順帶指出:方法切法加了反引號名支援之後,Room 的 DAO 方法若用反引號命名,會被切成名字空白的一支,守衛要求一支「以空名字呼叫」的測試,永遠找不到而誤擋。這是這次改動帶進的回歸(改動前反引號方法根本不被認成方法、不檢查)。

| 組 | 紅的測試 | 根因 | 修法 |
|---|---|---|---|
| Room 守衛收空名字 | t_room_dao_backtick_method_not_required(新寫,先紅) | 反引號名支援是給測試防竄改的,Room 那半的 _rg_spans 照收空名字 | _rg_spans 的 DAO 方法與型別轉換都不收空名字,回到改動前不檢查;兩處各在複本上拿掉一次,對應斷言各自翻紅;缺口寫進 Systems/room-guard 的 REVISIT |

修後:6 支全綠;相關子集 test_guard 87、lint_new 82、lint_waive 31、doctor 569、room 168 全綠。

沒有再派審查席:四組都是既有守衛測試先紅、照既有做法修,改動不碰 catch、指紋、比對規則的判讀邏輯。字串常值與常數兩條正規式的樣式字元一字未改,只是編譯時機延後;import 樣式只把行首空白從「含換行的空白」收窄成「空格與定位字元」,Kotlin 與 Java 的 import 行不受影響。
