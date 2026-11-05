fun a(api: Api) {
    GlobalScope.launch { api.sync() } // BAD
    CoroutineScope(Dispatchers.IO).launch { api.sync() } // BAD
    val d = GlobalScope.async(Dispatchers.IO) { api.sync() } // BAD
}
