class Vm : ViewModel() {
    override fun onCleared() {
        super.onCleared()
        viewModelScope.launch { save() } // BAD
        viewModelScope.launch(Dispatchers.IO) { flush() } // BAD
    }
}
