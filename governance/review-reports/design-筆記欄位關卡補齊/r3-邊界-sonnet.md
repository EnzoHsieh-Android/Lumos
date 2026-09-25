severity: major

## F1 note_lint 容器型別非物件(如寫成清單)時的行為,spec 全文沒定義

spec 只講 `note_lint.gate` 這個「值」看不懂時怎麼辦,沒講 `note_lint` 這個容器本身型別不對時怎麼辦。同樣借用的 node_home 那份設定,現有程式對容器型別另外有一段獨立防呆(`nh = data.get("node_home") if isinstance(data, dict) else None` 之後 `if not isinstance(nh, dict): cfg["warnings"].append("設定檔的 node_home 不是物件,整段用預設")`,`scripts/lumos:21436-21441`),跟「gate 值看不懂當 on」是兩層各自要接住的判斷。spec 的 PRIOR-ART 只說借用 on/warn/off 與「看不懂當 on」的形狀,沒有提到要借用這層容器型別防呆,S1–S4 四條條款也只涵蓋 on/warn/off/未知字串四種值,沒有一條涵蓋 `note_lint` 被寫成清單(例如 `"note_lint": ["on"]`)這種情境。照 spec 字面實作,合理寫法會是 `data.get("note_lint", {}).get("gate")`,遇到清單就是 `AttributeError`,讓 lint/doctor 對整個圖譜的健檢直接掛掉(而不是照 S3/S4 那樣印一行警告退回預設)——這正是「邊界可執行」鏡頭要收的:奇形怪狀的設定值有沒有路可走,spec 沒寫清楚。

引句:「`.lumos/config.json` 的 `note_lint.gate`,一個開關同時管二與一的新增部分,以及四」

severity: major
blocking: yes

## F2 設定檔不存在或不是合法 JSON 時,走「沒設(warn)」還是「看不懂(on)」,spec 沒裁定

spec 對預設值的敘述只到「沒設 note_lint.gate」這個 key-level 情境(第 53 行),以及「gate 的值看不懂」這個 value-level 情境(第 55 行),兩者的預設方向剛好相反(前者 warn、後者 on)。但「整份 .lumos/config.json 不存在」或「存在但不是合法 JSON」不屬於這兩種情境中的任何一種——它連 key 都讀不到,說是「沒設」也通,說是「看不懂」也通。這不是我在腦補兩可,是同一支程式裡對同類情境已經有多種先例、彼此答案不一致:`node_home` 那段是「設定檔讀不了 → 用預設」,而它的預設 mode 剛好是 `"on"`(`scripts/lumos:21400` 起的 `_nodehome_config`,尤其 `21429`/`21434` 兩處「.lumos/config.json 讀不了」都退回 `cfg = {"mode": "on", ...}` 這個預設);但 note_lint 的預設(沒設)明講是 warn,不是 on。換句話說,借來的形狀在「值域內」的部分（on/warn/off/看不懂當on）是對齊的,但「檔案本身讀不到」這一種不屬於值域內的情境,note_lint 該退到 warn(比照它自己的「沒設」預設)還是退到 on(比照 node_home 讀不了的先例),spec 沒有一句話裁定,S1–S4 也沒有任何一條條款用「設定檔不存在／不是合法 JSON」當前提。這會直接決定沒設定過 `.lumos/config.json` 的消費專案(多數新專案的常態)踩到這規則時是「只提醒」還是「擋提交」,不是無關緊要的細節。

引句:「warn(**沒設就是這個**):新規則只提醒——提交前、健檢、`set` 都不擋」

severity: major
blocking: yes

## F3 status 顯式寫成空字串,算不算「沒有填」,spec 沒定義,且會跟既有值域檢查的行為對不上

spec 第 41 行說 status 四類型必填,S6 條款寫「沒有填 status」——用詞是「沒有填」,沒有區分「frontmatter 裡完全沒有 status 這個 key」跟「status: ""(顯式寫了但是空字串)」。現有的 status 值域檢查(`scripts/lumos:4877-4881`)在 `_created_e >= _ENUM_CUTOFF` 時執行 `_st = str(n.fields.get("status") or "")`,再用 `if t in _STATUS_ENUM and _st and _st not in _STATUS_ENUM[t]` 判斷——這裡的 `and _st` 這個短路條件,代表 `status: ""` 目前會**跳過**既有的值域檢查(空字串判 falsy,不報錯)。新規則若照字面只判斷「key 存不存在」(例如用 `"status" not in n.fields`),那麼一篇顯式寫了 `status: ""` 的筆記會兩邊都放過(舊值域檢查因為空字串跳過、新必填檢查因為 key 存在也跳過)——這正好是 spec 想堵的洞(status 沒填)卻可能因為兩條規則各自的邊界定義不一致而漏掉。若新規則改用「值判空」(例如 `not n.fields.get("status", "").strip()`)才會接住,但 spec 文字沒有寫清楚要用哪一種判法,S6 的測試名稱 `t_lint_status_required` 也看不出要不要覆蓋這個顯式空字串情境。

引句:「`status`:system、project、verification、issue 四種類型必填。」

severity: minor
blocking: no

## 實務隱患

- 金流:無——只動知識庫筆記的欄位格式檢查,不碰交易或計費路徑。
- 對外送出:無——lint、健檢與 `set` 都只讀寫本機檔案,新規則沒有新增任何網路呼叫。
- 不可逆:無——新增的擋點都靠 `note_lint.gate` 這個開關,改開關或 `--no-verify` 就能繞過或退回;沒有動到資料刪除或不能還原的動作。
- 守衛面:是,而且正是這條鏡頭要挑的地方——新增的擋點在多處讀取設定值(對外部/舊消費專案不可控的 `.lumos/config.json` 內容),F1、F2 兩條就是這個擋點在「輸入不是預期形狀」時該退到哪一態,spec 沒交代清楚,實作時容易因為兩種合理讀法選錯一種而讓沒設定過檔的消費專案意外被擋下(或反過來,想擋的專案因為設定檔壞掉而悄悄退回不擋)。

最嚴重 severity: major;blocking 共 2 條。
