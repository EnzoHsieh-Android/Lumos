fun a() = callbackFlow {
    val l = Listener { v -> trySend(v).onFailure { log(it) } } // GOOD
    api.register(l)
    awaitClose { api.unregister(l) }
}
fun b() = callbackFlow {
    val l = Listener { v ->
        val r = trySend(v) // GOOD
        if (r.isFailure) log(r)
    }
    awaitClose { }
}
fun c() = channelFlow {
    trySend(1) // GOOD
}
