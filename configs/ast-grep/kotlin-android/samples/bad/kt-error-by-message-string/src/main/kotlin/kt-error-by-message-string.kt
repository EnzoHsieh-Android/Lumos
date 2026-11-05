fun a(e: Exception) = if (e.message?.contains("timeout") == true) Timeout else Other // BAD
fun b() = try { load() } catch (x: IOException) { if (x.localizedMessage?.contains("Unable to resolve") == true) Offline else Other } // BAD
fun c(f: Flow<Int>) = f.catch { if (it.message == "closed") emit(0) } // BAD
