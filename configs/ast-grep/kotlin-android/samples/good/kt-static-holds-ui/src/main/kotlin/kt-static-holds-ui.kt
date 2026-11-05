package good

object Navigator {
    var activityRef: WeakReference<Activity>? = null
    lateinit var app: Application
}

class Overlay(private val anchor: View) {
    companion object {
        const val TAG = "Overlay"
        val viewModelKey: ViewModel? = null
    }
}
