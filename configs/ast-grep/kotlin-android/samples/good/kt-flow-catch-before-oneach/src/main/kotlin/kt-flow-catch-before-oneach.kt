fun a(f: Flow<Int>) = f.onEach { save(it) }.catch { emit(-1) } // GOOD 下游
fun b(f: Flow<Int>) = f.catch { emit(0) }.onEach { save(it) }.catch { log(it) } // GOOD 下游還有一層 catch
