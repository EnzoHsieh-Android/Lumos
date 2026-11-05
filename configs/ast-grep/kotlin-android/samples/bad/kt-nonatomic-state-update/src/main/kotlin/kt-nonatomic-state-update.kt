class CounterViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    fun refresh() {
        viewModelScope.launch { _state.value = _state.value.copy(loading = true) } // BAD
    }
    fun increment() {
        viewModelScope.launch { _count.value = _count.value + 1 } // BAD
    }
}
