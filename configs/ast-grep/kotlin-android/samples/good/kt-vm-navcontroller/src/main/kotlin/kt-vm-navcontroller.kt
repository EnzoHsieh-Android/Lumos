package good

// case: screen-composable-takes-nav(擁有 NavHost 的那層組建收 NavController,ViewModel 不碰)
@Composable
fun LoginScreen(navController: NavHostController = rememberNavController(), vm: LoginViewModel = hiltViewModel()) {
    val s by vm.uiState.collectAsStateWithLifecycle()
    NavHost(navController, startDestination = "login") {
        composable("login") { LoginContent(s, onLoggedIn = dropUnlessResumed { navController.navigate("home") }) }
    }
}
// case: vm-exposes-state
class D4ViewModel : ViewModel() {
    val isUserLoggedIn = MutableStateFlow(false).asStateFlow()
}
// case: helper-class-with-nav
class Navigator(private val navController: NavController) { fun home() = navController.navigate("home") }
