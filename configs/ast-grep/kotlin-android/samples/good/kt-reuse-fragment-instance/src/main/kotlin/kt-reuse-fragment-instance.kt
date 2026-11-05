package good

// case: local-new
class X3Activity : AppCompatActivity() {
    fun show() { supportFragmentManager.beginTransaction().replace(R.id.c, DetailFragment()).commit() }
}
// case: findFragmentByTag
class X4Activity : AppCompatActivity() {
    fun show() { val f = supportFragmentManager.findFragmentByTag("d") as? DetailFragment ?: DetailFragment() }
}
// case: tag-constant-and-factory
class X5Activity : AppCompatActivity() {
    private val tag = "detail"
    private val factory = DetailFragmentFactory()
}
