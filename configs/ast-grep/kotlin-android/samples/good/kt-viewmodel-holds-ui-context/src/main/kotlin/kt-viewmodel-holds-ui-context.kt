class ProfileViewModel(private val repo: Repo) : ViewModel() // GOOD

// 容易誤報:系統服務包成介面注入,型別名字裡有 Context 字樣但不是 Context
class CheckoutViewModel(private val strings: ContextStringProvider) : ViewModel() // GOOD

// 容易誤報:不是 ViewModel 的資料層類別拿 Context 是正常的
class ImageCache(private val context: Context) {
    fun dir() = context.cacheDir
}
