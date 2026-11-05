package bad

// case: ctor-param
class D1ViewModel(private val navController: NavController) : ViewModel()
// case: method-param
class D2ViewModel : ViewModel() {
    fun onLogin(nav: NavHostController) { nav.navigate("home") }
}
// case: lateinit-property
class D3ViewModel : ViewModel() {
    lateinit var nav: NavController
}
