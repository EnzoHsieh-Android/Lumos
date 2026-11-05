class VM(repo: Repo) : ViewModel() {
    val a = repo.users().cachedIn(viewModelScope).map { pd -> pd.map { it.toUi() } } // BAD
    val b = repo.users().cachedIn(viewModelScope).filter { true } // BAD
}
