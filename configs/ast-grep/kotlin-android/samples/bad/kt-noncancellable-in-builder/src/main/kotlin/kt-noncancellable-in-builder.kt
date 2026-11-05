fun a() {
    scope.launch(NonCancellable) { save() } // BAD
    val d = async(NonCancellable + Dispatchers.IO) { upload() } // BAD
    viewModelScope.launch(context = NonCancellable) { flush() } // BAD
}
