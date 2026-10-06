severity: minor

## 問 1 分層與依賴方向
新碼都放在 scripts/lumos 的 drift 區段,跟鄰居同層:純判斷函式(_drift_route_open、_drift_ack_live、_drift_expiring_acked、_drift_ack_buckets)在 `_drift_split_acked` 旁,指令層(cmd_drift_ack)呼叫 `_drift_ack_route`,沒有跨層直呼;推送檢查不傳 as_of/note_state,與 `_drift_m1_split_acked` 另開分支的做法同形(`scripts/lumos:34429`)。`_drift_ack_buckets` 把原本內嵌在 `_drift_split_acked` 的迴圈抽出,方向一致。
引句:「keys, bound, expiring = _drift_ack_buckets(acks)」
唯一的分歧見 F1(doctor 判原文還在)。

## 問 2 命名與錯誤處理
命名 `_drift_*` 前綴一致;擋下訊息用「擋下:…」加 return 2,與 `cmd_drift_ack` 既有擋下同(`scripts/lumos:34659` 一帶);取本機日期用 `_dt.datetime.now(_dt.timezone.utc).astimezone().date()` 加「# 本機日期」註解,與 `scripts/lumos:4063`、`scripts/lumos:37010` 一致。細節不一致見 F2、F3。
引句:「today = _dt.datetime.now(_dt.timezone.utc).astimezone().date()   # 本機日期」

## 問 3 第二種做法
沒有另一套狀態集合:Issue 開著沿用 `_DRIFT_OPEN_ISSUE`(`scripts/lumos:32250`),計劃沿用 `_STATUS_ENUM` 與 `_DRIFT_CLOSED`;prev_ack 印法仍走 `_drift_prev_ack_line`,只加 dead 分支;取最新一筆沿用 `_drift_bound_latest`。有兩處是同功能的另一種寫法,見 F1、F2。
引句:「last = _drift_bound_latest(rows)[-1]」

## F1 doctor 判「那一行原文還在」另寫一套比對
severity: minor
blocking: 否
`_drift_dead_ack_rows` 用逐實體行的 strip 集合比對表態的 text,而表態端的原文是 `_drift_ack_text` 產的(retire 記接回續行的整條,`scripts/lumos:34628`),scan 端則由發現本身比對。同一個「這筆表態還對得上哪一行」有了第二套判法;retire 的多行條目在 doctor 這邊會對不上而被略過(結構問題:應複用 `_ns_summary_logical`/`_retire_lines` 的原文,而不是自己切行)。
引句:「if text not in {ln.strip() for ln in (env_text(env, rel) or "").split("\n")}:」

## F2 「計劃還開著」另寫成集合差,鄰居是 not in _DRIFT_CLOSED
severity: minor
blocking: 否
`_drift_route_open` 的計劃分支用 `_STATUS_ENUM["project"] - set(_DRIFT_CLOSED)`;鄰居判計劃收尾一律 `not in _DRIFT_CLOSED`(`scripts/lumos:32390`),另有現成的 `_DRIFT_SETTLED`(`scripts/lumos:32253`)。語意相同但寫法與鄰居不同,且對狀態表以外的值(手寫壞值)結果相反(新寫法判不開、鄰居判未收尾)。
引句:「return status in _STATUS_ENUM["project"] - set(_DRIFT_CLOSED)」

## F3 表態端驗去處與判活端讀筆記狀態是兩條路,且表態端漏了讀不出的檢查
severity: minor
blocking: 否
`_drift_ack_route` 直接 `env.notes.get(trel)` 加 `_drift_str` 取型別狀態;判活端 `_drift_note_state` 另寫前綴切割加 `_note_unreadable` 檢查。兩邊雖共用 `_drift_route_open`,取狀態的步驟有兩份,表態端沒有 `_note_unreadable` 防護(鄰居讀筆記狀態處如 `scripts/lumos:32385` 一帶是先判 None 再取欄位)。另 `_drift_ack_route` 取日期用 astimezone,同函式 `cmd_drift_ack` 記 date 仍是 `datetime.date.today()`(`scripts/lumos:34675` 一帶),同一支指令內兩種取日期寫法。
引句:「tn = env.notes.get(trel)」

不對齊共 3 條,其中 major 0 條
