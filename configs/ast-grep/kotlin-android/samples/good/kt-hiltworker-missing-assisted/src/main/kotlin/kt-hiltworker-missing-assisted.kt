package good

// case: correct
@HiltWorker
class SyncWorker2 @AssistedInject constructor(@Assisted ctx: Context, @Assisted params: WorkerParameters, private val repo: Repo) : CoroutineWorker(ctx, params)
// case: non-hilt-worker
class PlainWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params)
