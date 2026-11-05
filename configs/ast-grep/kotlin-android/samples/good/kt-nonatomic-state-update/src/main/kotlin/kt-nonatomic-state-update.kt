class CounterViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    fun refresh() {
        viewModelScope.launch { _state.update { it.copy(loading = true) } } // GOOD
    }
}

// 容易誤報:Composable 的 onClick 只在主執行緒跑,讀改寫不會跟別人搶
@Composable
fun Counter(count: MutableState<Int>) {
    Button(onClick = { count.value = count.value + 1 }) { Text("+") } // GOOD
}

// 容易誤報:受 Mutex 保護的讀改寫
class LockedViewModel(private val mutex: Mutex) : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    suspend fun set() { mutex.withLock { _state.value = _state.value.copy(x = 1) } }
}
