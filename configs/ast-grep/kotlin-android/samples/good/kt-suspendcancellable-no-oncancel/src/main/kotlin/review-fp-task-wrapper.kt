// 語意覆核級已知誤報(代碼審 r1 M11):包一次性的 Play Services Task,沒有可取消的資源,不加 invokeOnCancellation 本來就對;形狀分不出,留給盲判
suspend fun sus(task: Task<Int>): Int = suspendCancellableCoroutine<Int> { cont ->
    task.addOnSuccessListener { cont.resume(it) }
}
