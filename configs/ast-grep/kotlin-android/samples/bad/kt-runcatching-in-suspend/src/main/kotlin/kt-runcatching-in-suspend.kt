suspend fun a(repo: Repo) = runCatching { repo.load() } // BAD
suspend fun b(repo: Repo) {
    val r = repo.runCatching { load() } // BAD
}
