package good

class Holder {
    val parser by lazy { Parser() }
    val other by lazy(LazyThreadSafetyMode.PUBLICATION) { Other() }
}

// 容易誤報:lazy 的初值字串剛好是 "NONE",不是 LazyThreadSafetyMode.NONE
class Labels {
    val none = lazy { "NONE" } // GOOD
    val sync by lazy(LazyThreadSafetyMode.SYNCHRONIZED) { load() } // GOOD
}
