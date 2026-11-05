package bad

object Navigator {
    lateinit var activity: Activity // BAD
    private var current: AppCompatActivity? = null // BAD
}

class Overlay {
    companion object {
        var anchor: View? = null // BAD
        var host: Fragment? = null // BAD
    }
}
