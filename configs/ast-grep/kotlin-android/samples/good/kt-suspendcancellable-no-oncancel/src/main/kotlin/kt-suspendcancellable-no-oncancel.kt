suspend fun fetch(api: Api): User = suspendCancellableCoroutine { cont ->
    val call = api.call()
    cont.invokeOnCancellation { call.cancel() } // GOOD
    call.enqueue(callbackOf(cont))
}

suspend fun download(api: Api): Bytes = suspendCancellableCoroutine<Bytes> { cont ->
    val call = api.download()
    cont.invokeOnCancellation { call.cancel() } // GOOD
    call.enqueue(callbackOf(cont))
}

// 容易誤報:suspendCoroutine 歸 kt-suspendcoroutine 報,這條不重複報
suspend fun legacy(api: Api): User = suspendCoroutine { cont -> api.call().enqueue(callbackOf(cont)) }
