class LockScreen(private val biometricPrompt: BiometricPrompt) {
    fun unlockOne(promptInfo: BiometricPrompt.PromptInfo, cipher: Cipher) {
        biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher)) // GOOD 綁 Keystore 金鑰
    }
}
fun loginOne(auth: AuthClient, request: LoginRequest) {
    auth.authenticate(request) // GOOD 不是生物辨識
}
