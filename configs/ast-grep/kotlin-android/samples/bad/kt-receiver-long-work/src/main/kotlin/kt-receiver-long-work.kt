class R : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        scope.launch { api.sync() } // BAD
        client.newCall(req).execute() // BAD
    }
}
class R2 : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) = runBlocking { api.sync() } // BAD
}
