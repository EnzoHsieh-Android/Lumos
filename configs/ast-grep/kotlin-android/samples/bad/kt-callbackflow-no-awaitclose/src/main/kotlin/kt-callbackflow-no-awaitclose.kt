fun locations(client: LocationClient): Flow<Location> = callbackFlow {
    val listener = LocationListener { trySend(it) }
    client.register(listener) // BAD:沒有 awaitClose,監聽器永遠不移除
}

fun clicks(view: View): Flow<Unit> = callbackFlow {
    view.setOnClickListener { trySend(Unit) }
    close() // BAD:用 close 收尾也不算 awaitClose
}
