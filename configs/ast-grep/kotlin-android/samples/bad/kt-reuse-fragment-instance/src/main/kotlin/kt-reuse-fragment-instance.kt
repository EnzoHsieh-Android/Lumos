package bad

// case: activity-field
class X1Activity : AppCompatActivity() {
    private val detail = DetailFragment()
    fun show() { supportFragmentManager.beginTransaction().replace(R.id.c, detail).commit() }
}
// case: newInstance-lazy
class X2Activity : AppCompatActivity() {
    private val settings by lazy { SettingsFragment.newInstance() }
}
