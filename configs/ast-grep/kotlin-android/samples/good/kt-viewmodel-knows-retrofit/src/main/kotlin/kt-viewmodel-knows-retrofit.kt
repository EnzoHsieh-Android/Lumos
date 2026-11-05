import com.example.domain.NetworkError // GOOD

class VM(private val repo: Repo) : ViewModel() {
    fun load() = viewModelScope.launch {
        try { repo.load() } catch (e: NetworkError) { } // GOOD
    }
}
