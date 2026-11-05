suspend fun a() = supervisorScope {
    launch { mayThrow() } // BAD
    launch(Dispatchers.IO) { load(); save() } // BAD
}
