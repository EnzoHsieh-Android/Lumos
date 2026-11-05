package bad

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { // BAD
        super.onCreate(savedInstanceState)
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}

class RouterActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { // BAD
        super.onCreate(savedInstanceState)
        val target = if (loggedIn) HomeActivity::class.java else LoginActivity::class.java
        startActivity(Intent(this, target).apply { flags = Intent.FLAG_ACTIVITY_NEW_TASK })
        finish()
    }
}
