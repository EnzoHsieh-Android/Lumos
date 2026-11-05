package bad

// case: both-missing
@HiltWorker
class SyncWorker @AssistedInject constructor(ctx: Context, params: WorkerParameters, private val repo: Repo) : CoroutineWorker(ctx, params)
// case: params-missing
@HiltWorker
class UploadWorker @AssistedInject constructor(@Assisted ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params)
