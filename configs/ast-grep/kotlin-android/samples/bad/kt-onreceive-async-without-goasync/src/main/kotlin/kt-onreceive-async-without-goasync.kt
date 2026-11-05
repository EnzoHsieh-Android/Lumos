package bad

class SyncReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) { // BAD
        CoroutineScope(Dispatchers.IO).launch { repo.sync() }
    }
}

class UploadReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) { // BAD
        thread { uploader.upload(File(context.filesDir, "a")) }
    }
}

class GlobalReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) { // BAD
        GlobalScope.launch(Dispatchers.IO) { repo.refresh() }
    }
}
