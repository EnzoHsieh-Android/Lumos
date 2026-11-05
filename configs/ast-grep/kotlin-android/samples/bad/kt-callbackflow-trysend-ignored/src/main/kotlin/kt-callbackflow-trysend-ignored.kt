fun a() = callbackFlow {
    val l = Listener { v -> trySend(v) } // BAD
    api.register(l)
    awaitClose { api.unregister(l) }
}
fun b() = callbackFlow<Loc> {
    val cb = object : Callback {
        override fun onLoc(x: Loc) {
            channel.trySend(x) // BAD
        }
    }
    awaitClose { }
}
