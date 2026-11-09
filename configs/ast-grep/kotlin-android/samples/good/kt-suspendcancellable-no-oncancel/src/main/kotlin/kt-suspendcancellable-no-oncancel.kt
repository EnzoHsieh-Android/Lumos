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
