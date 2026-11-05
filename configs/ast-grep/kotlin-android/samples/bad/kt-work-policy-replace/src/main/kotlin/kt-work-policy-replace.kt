fun a(wm: WorkManager) = wm.enqueueUniqueWork("sync", ExistingWorkPolicy.REPLACE, req) // BAD
fun b(wm: WorkManager) = wm.enqueueUniquePeriodicWork("p", ExistingPeriodicWorkPolicy.REPLACE, preq) // BAD
