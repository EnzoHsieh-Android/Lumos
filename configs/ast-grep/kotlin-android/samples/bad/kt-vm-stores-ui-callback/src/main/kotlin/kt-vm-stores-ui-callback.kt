package bad

// case: listener-var
class G1ViewModel : ViewModel() {
    private var listener: OnDoneListener? = null
    fun setListener(l: OnDoneListener) { this.listener = l }
}
// case: lambda-var
class G2ViewModel : ViewModel() {
    private var onDone: (() -> Unit)? = null
    fun setOnDone(cb: () -> Unit) { onDone = cb }
}
// case: callback-list
class G3ViewModel : ViewModel() {
    private val callbacks = mutableListOf<UiCallback>()
}

// case: var-default-lambda(代碼審 r2 規則A F2:預設空 lambda 的 var,之後由 UI 指派,照樣留住 Fragment)
class G7ViewModel : ViewModel() {
    var onEvent: (String) -> Unit = {}
    var cb: () -> Unit = {}
}
