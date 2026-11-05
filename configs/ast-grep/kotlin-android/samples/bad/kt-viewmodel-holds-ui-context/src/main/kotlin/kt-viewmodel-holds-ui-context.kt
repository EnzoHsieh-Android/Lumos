class ProfileViewModel(private val context: Context) : ViewModel() // BAD

class CheckoutViewModel(val activity: Activity, private val repo: Repo) : ViewModel() // BAD
