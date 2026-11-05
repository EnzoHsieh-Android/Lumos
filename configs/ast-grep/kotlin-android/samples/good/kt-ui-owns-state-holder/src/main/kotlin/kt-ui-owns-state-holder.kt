package good

// case: fragment-viewmodels
class O3Fragment : Fragment() {
    private val vm: O3ViewModel by viewModels()
}
// case: viewmodel-holds-state
class O3ViewModel : ViewModel() {
    private val _q = MutableStateFlow("")
}
// case: activity-navargs
class O4Activity : ComponentActivity() {
    private val vm by viewModels<O3ViewModel>()
}
