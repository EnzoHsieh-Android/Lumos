severity: major

# r1 通才席審查:只換測試綁定不算寫說明

逐節已讀。交叉引用核對:`[S3]`、〈天花板〉1、`_ns_is_tail_append`(`scripts/lumos:28167`)、`_SLOT_KEY_RE`(`scripts/lumos:4138`)、`slot_parse`(`scripts/lumos:4145`)、`_nodehome_parse_note`(`scripts/lumos:26839`)、`_nodehome_mark_note_content`(`scripts/lumos:27220`)皆存在。sig 只有 `scripts/lumos:27239` 與 `:27335` 兩處讀,「一處改兩條路都生效」成立;沒有第三條平行的「內容有沒有變」判定漏掉。

## findings

1. 值的「空白」沒限單行也沒限長度,一個跨行的假標記可把英文說明整段藏進去,而且現有的測試名存在性檢查也看不到它
severity: major
   blocking: 是 — 照 spec 字面實作,放寬的守衛會被拿來繞過寫回落點,而 spec 把這個洞只留給事後回報。
   引句:「標記的值只收英數、底線、點、冒號、斜線、井號、@、逗號、連字號、空白、半形圓括號、單引號」
   輸入:同一個提交改 A 的程式;B(不是 A 的家)正文新增三行
   `[test:This module now retries`、`three times before failing`、`and logs each attempt]`。
   走到:〈做法〉1 的掃描器沒規定「空白」是否含換行;依字面(Python 的 `\s` 慣用寫法)會吞掉整段,字元全在白名單內,標記被整個拿掉,sig 不變,home check 回 0。
   壞在:file: `scripts/lumos:29688`(`_ns_test_ref_lines` 正文逐實體行呼叫 `slot_parse`)是逐行判,第一行 `[test:This module now retries` 沒收尾方括號,`slot_parse` 回的欄位帶錯誤,`_test_names_of`(`scripts/lumos:29586`)對 `err` 直接略過;所以跨行標記連「指不到真測試」都不報。單行英文句子至少會被該檢查擋(見 finding 2),跨行的不會。
   修法方向在 spec 內就能定:值限單行、非反引號值不准空白、設長度上限(spec 自己的 RETIRE-IF 已承認要收窄,現在收成本最低)。

2. 〈天花板〉1 與 RETIRE-IF 沒提到現有的機械守衛,「工具分不出」說得不精確
severity: minor
   blocking: 否 — 只是文件精度,不影響實作行為。
   引句:「值是英文句子的綁定標記可以藏說明,工具分不出那是測試名還是句子;靠 RETIRE-IF 的回報觸發收窄。」
   file: `scripts/lumos:29721`、`scripts/lumos:30020`:筆記形狀擋已對這次新寫的 `[test:]` 值判「指不到真測試」,逗號會被 `_NS_TR_SPLIT_RE` 切開各自判;所以單行英文句子在提交時多半已被擋,只有平台跳過、判不了、反引號 Kotlin 名這幾種會漏。spec 應把這道當第二層寫進〈實務隱患〉藏說明那條,並把它的漏網條件(判不了/跳過)列成天花板,才算誠實,也讓 finding 1 的跨行形狀有對照。

3. 反引號配對是整段文字跨行掃,`slot_parse` 與筆記形狀擋是逐行,兩邊判法不一致
severity: minor
   blocking: 否 — 不一致只造成「舉例標記」的邊角誤放,不涉及藏說明。
   引句:「碰到行內程式碼(反引號到下一個反引號)整段照留」
   輸入:正文第 1 行 ``a `b` c ` ``(奇數個反引號),第 2 行 ``` `[test:t_old]` 說明 ```。逐行(`scripts/lumos:4145` 的 `slot_parse`)第 2 行標記在行內程式碼裡、不算欄位;整段跨行掃描時第 1 行最後一個反引號與第 2 行第一個配成一段,第 2 行的 `[test:t_old]` 落在段外被拿掉,把它改成 `[test:t_new]` 不算內容有變。spec 的〈範圍〉第三條說「跟 slot_parse 的既有判法一致」,在這種輸入下不成立;要嘛規定逐行掃(以換行重置配對),要嘛刪掉「一致」二字。

## 實務隱患鏡頭(守衛面)

- 藏說明:見 finding 1(跨行)與 finding 2(單行的既有第二層)。中文值不拿掉,中文說明藏不進去,這點 spec 對。
- 繞過寫回落點取巧:file: `scripts/hooks/pre-commit:276` Gate 3 只要有任一圖譜 `.md` staged 就放行「改程式沒動圖譜」,所以換綁定本來就能當「我動過圖譜」的憑證(改 `updated` 同樣可以);放寬沒有新增這個出口。放寬真正多出來的只有 finding 1 那條藏說明路徑。
- 判定函式其餘規則:`foreign`(整篇原文,`scripts/lumos:27339` 一帶)、新增沒家、家被拿掉、負責範圍都不讀 sig,已核對不受影響;[S3] 的「只提醒沒家」走 `wb_files` 為空那條,成立。
- 誤判沒變:同行其他字有改仍會算內容有變;唯一的誤放是 finding 3。

## 各節

- 開頭欄位、範圍、做法、驗收條款、回退、天花板:已讀,除上列外無 finding。
- 驗收條款:缺「跨行假標記回 1」與「奇數反引號舉例」兩個情境,補上 finding 1、3 的修法時要一併加進 [S1]。

最嚴重 severity:major;blocking 共 1 條。
