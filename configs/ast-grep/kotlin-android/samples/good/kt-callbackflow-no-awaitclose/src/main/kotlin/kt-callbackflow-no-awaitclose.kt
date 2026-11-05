fun locations(client: LocationClient): Flow<Location> = callbackFlow {
    val listener = LocationListener { trySend(it) }
    client.register(listener)
    awaitClose { client.unregister(listener) } // GOOD
}

// 容易誤報:awaitClose 寫成具名參數形式或寫在 try 後面,一樣算數
fun clicks(view: View): Flow<Unit> = callbackFlow {
    view.setOnClickListener { trySend(Unit) }
    awaitClose(block = { view.setOnClickListener(null) }) // GOOD
}

fun typed(api: Api): Flow<Int> = callbackFlow<Int> {
    val l = Listener { trySend(it) }
    api.register(l)
    awaitClose { api.unregister(l) } // GOOD
}
