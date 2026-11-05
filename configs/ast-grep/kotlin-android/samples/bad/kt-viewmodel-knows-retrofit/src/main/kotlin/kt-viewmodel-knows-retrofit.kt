import retrofit2.HttpException // BAD

class VM(private val repo: Repo) : ViewModel() {
    fun load() = viewModelScope.launch {
        try { repo.load() } catch (e: HttpException) { } // BAD
    }
}
