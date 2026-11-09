// 跨規則邊界案例(檔名以 cross- 開頭):suspendCoroutine 歸 kt-suspendcoroutine(API-11)報,
// 放在這裡是證明 kt-suspendcancellable-no-oncancel 不重複報;好例的跨規則檢查略過這種檔
suspend fun legacy(api: Api): User = suspendCoroutine { cont -> api.call().enqueue(callbackOf(cont)) }
