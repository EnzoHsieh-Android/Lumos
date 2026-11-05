package bad

// case: activity-livedata
class O1Activity : AppCompatActivity() {
    private val data = MutableLiveData<List<Item>>()
}
// case: fragment-stateflow
class O2Fragment : Fragment(R.layout.f) {
    private val query = MutableStateFlow("")
}
