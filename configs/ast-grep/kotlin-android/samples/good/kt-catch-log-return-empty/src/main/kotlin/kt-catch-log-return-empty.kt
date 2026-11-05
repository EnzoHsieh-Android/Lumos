suspend fun a(api: Api): Result<List<User>> = try { Result.success(api.users()) } catch (e: IOException) { Log.e("t", "x", e); Result.failure(e) } // GOOD
fun b(): List<User> = try { load() } catch (e: NoSuchFileException) { emptyList() } // GOOD 沒有只記 log,檔案不存在本來就是空
fun c() = try { load() } catch (e: Exception) { Log.e("t", "x", e); throw e } // GOOD 重拋
