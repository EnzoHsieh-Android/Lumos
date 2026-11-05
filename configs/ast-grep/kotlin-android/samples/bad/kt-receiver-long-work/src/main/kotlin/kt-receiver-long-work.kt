class R : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        client.newCall(req).enqueue(callback) // BAD
        client.newCall(req).execute() // BAD
    }
}
class R2 : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) = runBlocking { api.sync() } // BAD
}
