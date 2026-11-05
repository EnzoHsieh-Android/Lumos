suspend fun fetch(api: Api): User = suspendCoroutine { cont -> // BAD:不能取消
    api.call().enqueue(callbackOf(cont))
}

suspend fun download(api: Api): Bytes = suspendCancellableCoroutine<Bytes> { cont -> // BAD:沒註冊 invokeOnCancellation
    val call = api.download()
    call.enqueue(callbackOf(cont))
}
