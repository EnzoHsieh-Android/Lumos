class Vm(private val appScope: CoroutineScope) : ViewModel() {
    override fun onCleared() {
        appScope.launch { save() } // GOOD
    }
    fun onSave() {
        viewModelScope.launch { save() } // GOOD
    }
}

// 容易誤報:函式名開頭是 onCleared 但不是 onCleared 本身;onCleared 裡交給 WorkManager
class DraftViewModel(private val work: WorkManager) : ViewModel() {
    fun onClearedDraftClicked() {
        viewModelScope.launch { deleteDraft() } // GOOD
    }
    override fun onCleared() {
        work.enqueue(OneTimeWorkRequestBuilder<SaveDraftWorker>().build()) // GOOD
        super.onCleared()
    }
}
