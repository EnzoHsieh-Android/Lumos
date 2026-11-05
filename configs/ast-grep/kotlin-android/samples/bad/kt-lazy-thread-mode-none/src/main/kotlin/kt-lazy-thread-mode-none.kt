package bad

class Holder {
    val parser by lazy(LazyThreadSafetyMode.NONE) { Parser() } // BAD
    val other by lazy(mode = NONE) { Other() } // BAD
}
