suspend fun a(repo: Repo) = suspendRunCatching { repo.load() } // GOOD
fun b(s: String) = runCatching { s.toInt() } // GOOD 非 suspend 函式
