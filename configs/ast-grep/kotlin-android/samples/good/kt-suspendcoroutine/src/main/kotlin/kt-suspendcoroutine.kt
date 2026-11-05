suspend fun fetch(api: Api): User = suspendCancellableCoroutine { cont ->
    val call = api.call()
    cont.invokeOnCancellation { call.cancel() } // GOOD
    call.enqueue(callbackOf(cont))
}

// 容易誤報:帶型別參數的 suspendCancellableCoroutine,有註冊取消就算對
suspend fun download(api: Api): Bytes = suspendCancellableCoroutine<Bytes> { cont ->
    val call = api.download()
    cont.invokeOnCancellation { call.cancel() } // GOOD
    call.enqueue(callbackOf(cont))
}

interface UserService {
    @GET("user")
    suspend fun user(): User // GOOD:Retrofit 直接宣告 suspend fun
}
