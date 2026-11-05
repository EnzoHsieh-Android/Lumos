suspend fun render(user: Flow<User>, prefs: Flow<Prefs>) {
    user.collect { u ->
        prefs.collect { p -> show(u, p) } // BAD
    }
}

suspend fun watch(query: Flow<String>, filter: Flow<Filter>) {
    query.collectLatest { q ->
        filter.collect { f -> search(q, f) } // BAD
    }
}

// 外層包在 launch 裡、內外層之間沒有新協程,照樣卡
fun CoroutineScope.render2(user: Flow<User>, prefs: Flow<Prefs>) = launch {
    user.collect { u -> prefs.collect { p -> show(u, p) } } // BAD
}
