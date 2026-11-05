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
