fun a(f: Flow<Int>) = f.catch { emit(-1) }.onEach { save(it) } // BAD
fun b(f: Flow<Int>) = f.map { it * 2 }.catch { emit(0) }.onEach(::save) // BAD
