package good

// case: save-bundle
class V3Activity : AppCompatActivity() {
    override fun onSaveInstanceState(outState: Bundle) { super.onSaveInstanceState(outState) }
}
// case: jobscheduler-extras
fun schedule(ctx: Context) {
    val info = JobInfo.Builder(1, ComponentName(ctx, SyncJob::class.java)).setExtras(PersistableBundle().apply { putString("k", "v") }).build()
}
// case: other-fun-param
fun enqueue(extras: PersistableBundle) { }
