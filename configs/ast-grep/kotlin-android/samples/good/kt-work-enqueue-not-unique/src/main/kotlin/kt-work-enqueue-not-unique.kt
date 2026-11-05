fun a(ctx: Context) {
    WorkManager.getInstance(ctx).enqueueUniqueWork("sync", ExistingWorkPolicy.KEEP, req) // GOOD
}
fun b(call: Call<User>) = call.enqueue(cb) // GOOD Retrofit 的 enqueue
