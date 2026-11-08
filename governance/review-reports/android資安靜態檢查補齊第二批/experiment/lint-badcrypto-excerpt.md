# Google 資安包 BadCryptographyUsageDetector.kt 摘錄

來源:https://github.com/google/android-security-lints/blob/main/checks/src/main/java/com/example/lint/checks/BadCryptographyUsageDetector.kt(2026-11-08 以 gh api 下載,只摘判斷段)

```kotlin
    override fun visitMethodCall(context: JavaContext, node: UCallExpression, method: PsiMethod) {
        if (!context.evaluator.isMemberInSubClassOf(method, CRYPTO_CIPHER, false)) return

        val args = node.valueArguments
        // Currently only checking unsafe algorithms being passed in as an argument
        if (args.isEmpty()) return
        val transformation = ConstantEvaluator.evaluate(context, args[0])

        if (!handleVulnerableAlgorithmReporting(transformation.toString(), context, node)) {
            // If we haven't already warned about a vulnerable crypto algorithm being used
            // Check if we should warn about unsafe crypto algorithm usage
            handleUnsafeAlgorithmUsage(transformation.toString(), context, node)
        }
    }

// ...
        // Acceptable for RSA to use CBC cipher mode with OAEPWithSHA-256AndMGF1Padding
        if (algorithm == "RSA" && padding == "PKCS1Padding") {
            incident.fix = fix().replace().range(context.getLocation(node))
                .with("Cipher.getInstance(\"RSA/$mode/OAEPWithSHA-256AndMGF1Padding\")").build()
            context.report(incident)
        }

        // Unsafe Cipher Mode
        else if (mode == "CBC") {
            if (padding == "NoPadding") {
                // This is a more serious issue, and should be an error instead of a warning
                incident.severity = Severity.ERROR
            } else if (algorithm == "RSA" && padding.startsWith("OAEP")) {
                // This is an acceptable combination of algorithm / mode / padding and does not need to be warned
                return
            }
            incident.fix = fix().replace().range(context.getLocation(node))
                .with("Cipher.getInstance(\"$algorithm/GCM/NoPadding\")").build()
            context.report(incident)
        }
    }

    companion object {
        // Classes
// ...

        // Argument values
        private val VULNERABLE_STREAM_CIPHER_ALGORITHMS = setOf("RC4", "ARCFOUR")
        private const val SAFE_STREAM_CIPHER = "ChaCha20"
        private val VULNERABLE_BLOCK_CIPHER_ALGORITHMS = setOf("Blowfish", "DES", "RC2", "RC5")
        private const val SAFE_BLOCK_CIPHER = "AES/GCM/NoPadding"
```
