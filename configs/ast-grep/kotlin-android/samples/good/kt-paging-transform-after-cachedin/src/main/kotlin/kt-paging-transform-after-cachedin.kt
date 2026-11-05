class VM(repo: Repo) : ViewModel() {
    val a = repo.users().map { pd -> pd.map { it.toUi() } }.cachedIn(viewModelScope) // GOOD
    val b = list.map { it.id } // GOOD
}

// 容易誤報:filter 寫在 cachedIn 前面,cachedIn 之後只 collect
class OrderViewModel(repo: Repo) : ViewModel() {
    val visible = repo.orders().map { pd -> pd.filter { it.visible } }.cachedIn(viewModelScope) // GOOD
}
