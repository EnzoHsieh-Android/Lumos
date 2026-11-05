suspend fun download(api: Api): Bytes = suspendCancellableCoroutine<Bytes> { cont -> // BAD:沒註冊 invokeOnCancellation
    val call = api.download()
    call.enqueue(callbackOf(cont))
}

suspend fun fetch(api: Api): User = suspendCancellableCoroutine { cont -> // BAD:請求取消不了
    val call = api.call()
    call.enqueue(callbackOf(cont))
}
