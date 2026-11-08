class LockScreen(private val biometricPrompt: BiometricPrompt) {
    fun unlockOne(promptInfo: BiometricPrompt.PromptInfo) {
        biometricPrompt.authenticate(promptInfo) // BAD 沒帶 CryptoObject
    }
    fun unlockTwo(prompt: BiometricPrompt, info: BiometricPrompt.PromptInfo) {
        prompt.authenticate(info) // BAD
    }
}
