fun a() { try { load() } catch (e: IOException) { throw MyError("load failed", e) } } // GOOD
fun e() { try { load() } catch (e: IOException) { throw MyError(code = 1, cause = e) } } // GOOD 具名參數帶 cause
fun b() { try { load() } catch (e: IOException) { throw e } } // GOOD
fun c(x: Int) { if (x < 0) throw IllegalArgumentException("x < 0") } // GOOD 不在 catch
fun d() { try { load() } catch (e: IOException) { throw MyError(e) } } // GOOD
