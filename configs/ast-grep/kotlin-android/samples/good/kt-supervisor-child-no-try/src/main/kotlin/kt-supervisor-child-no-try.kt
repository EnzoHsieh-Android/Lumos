suspend fun a() = supervisorScope {
    launch { try { mayThrow() } catch (e: CancellationException) { throw e } catch (e: Exception) { log(e) } } // GOOD
    launch(handler) { mayThrow() } // GOOD
    launch { runCatching { mayThrow() }.onFailure { if (it is CancellationException) throw it; log(it) } } // GOOD
}
suspend fun b() = coroutineScope {
    launch { mayThrow() } // GOOD
}
