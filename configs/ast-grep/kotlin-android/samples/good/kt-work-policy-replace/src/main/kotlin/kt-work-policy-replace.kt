fun a(wm: WorkManager) = wm.enqueueUniqueWork("sync", ExistingWorkPolicy.KEEP, req) // GOOD
fun b(wm: WorkManager) = wm.enqueueUniquePeriodicWork("p", ExistingPeriodicWorkPolicy.UPDATE, preq) // GOOD
fun c() = OnConflictStrategy.REPLACE // GOOD 不同 API
