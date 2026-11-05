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
