class R : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        val pending = goAsync()
        scope.launch { // GOOD 有 goAsync
            try { api.sync() } finally { pending.finish() }
        }
    }
}
class R2 : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        WorkManager.getInstance(c).enqueueUniqueWork("s", ExistingWorkPolicy.KEEP, req) // GOOD
    }
}
