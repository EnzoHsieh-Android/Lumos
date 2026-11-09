// 跨規則邊界案例(檔名以 cross- 開頭):公開 MutableStateFlow 屬性歸 kt-public-mutable-stateflow(STATE-2)報,
// 放在這裡是證明 kt-repository-exposes-mutable-or-dto 不重複報;好例的跨規則檢查略過這種檔
class SessionRepository {
    val session: MutableStateFlow<Session?> = MutableStateFlow(null)
}
