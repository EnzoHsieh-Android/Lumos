suspend fun fetch(api: Api): User = suspendCoroutine { cont -> // BAD:不能取消
    api.call().enqueue(callbackOf(cont))
}

suspend fun download(api: Api): Bytes = suspendCoroutine<Bytes> { cont -> // BAD:帶型別參數一樣不能取消
    api.download().enqueue(callbackOf(cont))
}
