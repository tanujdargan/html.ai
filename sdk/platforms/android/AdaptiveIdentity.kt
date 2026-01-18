/**
 * Android/Kotlin SDK for Adaptive Identity Engine
 *
 * Usage:
 * ```kotlin
 * import com.adaptiveidentity.sdk.AdaptiveIdentity
 *
 * class ProductActivity : AppCompatActivity() {
 *     private val adaptive = AdaptiveIdentity.getInstance(this)
 *
 *     override fun onCreate(savedInstanceState: Bundle?) {
 *         super.onCreate(savedInstanceState)
 *
 *         adaptive.generateVariant(
 *             experimentId = "product-hero",
 *             originalContent = "<div>Original Product</div>",
 *             componentType = "product_card",
 *             goal = "add_to_cart"
 *         ) { result ->
 *             result.onSuccess { variant ->
 *                 webView.loadData(variant.generatedContent, "text/html", "UTF-8")
 *             }.onFailure { error ->
 *                 Log.e("Adaptive", "Error: $error")
 *             }
 *         }
 *     }
 *
 *     fun onAddToCartClicked() {
 *         adaptive.trackConversion(
 *             experimentId = "product-hero",
 *             conversionType = "add_to_cart"
 *         )
 *     }
 * }
 * ```
 *
 * Add to build.gradle:
 * ```
 * dependencies {
 *     implementation 'com.squareup.okhttp3:okhttp:4.12.0'
 *     implementation 'com.google.code.gson:gson:2.10.1'
 *     implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
 * }
 * ```
 */

package com.adaptiveidentity.sdk

import android.content.Context
import android.content.SharedPreferences
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ProcessLifecycleOwner
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.*
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.TimeUnit

// MARK: - Data Classes

data class VariantResponse(
    val success: Boolean,
    @SerializedName("variant_id") val variantId: String,
    @SerializedName("generated_content") val generatedContent: String,
    @SerializedName("identity_state") val identityState: String?,
    val confidence: Double,
    @SerializedName("experiment_id") val experimentId: String,
    @SerializedName("is_control") val isControl: Boolean,
    val rationale: String
)

data class TrackingEvent(
    @SerializedName("event_name") val eventName: String,
    @SerializedName("component_id") val componentId: String?,
    val properties: Map<String, Any>,
    val timestamp: String = java.time.Instant.now().toString()
)

data class GenerateRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("experiment_id") val experimentId: String,
    @SerializedName("original_content") val originalContent: String,
    @SerializedName("component_type") val componentType: String,
    val goal: String,
    val platform: String = "android",
    val context: Map<String, Any>
)

data class ConversionRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("experiment_id") val experimentId: String,
    @SerializedName("variant_id") val variantId: String,
    @SerializedName("conversion_type") val conversionType: String,
    val value: Double? = null
)

data class EventBatchRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("session_id") val sessionId: String,
    val events: List<TrackingEvent>
)

// MARK: - AdaptiveIdentity SDK

class AdaptiveIdentity private constructor(
    private val context: Context,
    private val apiBaseUrl: String
) : DefaultLifecycleObserver {

    companion object {
        private const val TAG = "AdaptiveIdentity"
        private const val PREFS_NAME = "adaptive_identity_prefs"
        private const val USER_ID_KEY = "adaptive_identity_uid"
        private const val EVENT_BATCH_SIZE = 10
        private const val EVENT_FLUSH_INTERVAL_MS = 5000L

        @Volatile
        private var instance: AdaptiveIdentity? = null

        fun getInstance(
            context: Context,
            apiBaseUrl: String = "http://10.0.2.2:8000" // Android emulator localhost
        ): AdaptiveIdentity {
            return instance ?: synchronized(this) {
                instance ?: AdaptiveIdentity(context.applicationContext, apiBaseUrl).also {
                    instance = it
                }
            }
        }
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()
    private val mainHandler = Handler(Looper.getMainLooper())
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val userId: String = getOrCreateUserId()
    private var sessionId: String = generateSessionId()

    private val pendingEvents = CopyOnWriteArrayList<TrackingEvent>()
    private var flushJob: Job? = null

    init {
        // Observe app lifecycle
        ProcessLifecycleOwner.get().lifecycle.addObserver(this)
        startEventFlushTimer()
    }

    // MARK: - User/Session Management

    private fun getOrCreateUserId(): String {
        val existingId = prefs.getString(USER_ID_KEY, null)
        if (existingId != null) return existingId

        val newId = UUID.randomUUID().toString()
        prefs.edit().putString(USER_ID_KEY, newId).apply()
        return newId
    }

    private fun generateSessionId(): String {
        return "session_${System.currentTimeMillis()}_${UUID.randomUUID().toString().take(8)}"
    }

    fun getUserId(): String = userId
    fun getSessionId(): String = sessionId

    // MARK: - Variant Generation

    fun generateVariant(
        experimentId: String,
        originalContent: String,
        componentType: String = "generic",
        goal: String = "conversion",
        context: Map<String, Any> = emptyMap(),
        callback: (Result<VariantResponse>) -> Unit
    ) {
        val request = GenerateRequest(
            userId = userId,
            sessionId = sessionId,
            experimentId = experimentId,
            originalContent = originalContent,
            componentType = componentType,
            goal = goal,
            context = context + getDeviceContext()
        )

        val json = gson.toJson(request)
        val body = json.toRequestBody("application/json".toMediaType())

        val httpRequest = Request.Builder()
            .url("$apiBaseUrl/api/v2/generate")
            .post(body)
            .build()

        client.newCall(httpRequest).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e(TAG, "Failed to generate variant", e)
                mainHandler.post { callback(Result.failure(e)) }
            }

            override fun onResponse(call: Call, response: Response) {
                try {
                    val responseBody = response.body?.string()
                    if (response.isSuccessful && responseBody != null) {
                        val variant = gson.fromJson(responseBody, VariantResponse::class.java)
                        mainHandler.post { callback(Result.success(variant)) }
                    } else {
                        val error = Exception("HTTP ${response.code}: $responseBody")
                        mainHandler.post { callback(Result.failure(error)) }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to parse variant response", e)
                    mainHandler.post { callback(Result.failure(e)) }
                }
            }
        })
    }

    suspend fun generateVariantAsync(
        experimentId: String,
        originalContent: String,
        componentType: String = "generic",
        goal: String = "conversion",
        context: Map<String, Any> = emptyMap()
    ): Result<VariantResponse> = withContext(Dispatchers.IO) {
        suspendCancellableCoroutine { continuation ->
            generateVariant(experimentId, originalContent, componentType, goal, context) { result ->
                continuation.resume(result) {}
            }
        }
    }

    // MARK: - Event Tracking

    fun trackEvent(
        eventName: String,
        componentId: String? = null,
        properties: Map<String, Any> = emptyMap()
    ) {
        val event = TrackingEvent(
            eventName = eventName,
            componentId = componentId,
            properties = properties
        )

        pendingEvents.add(event)

        if (pendingEvents.size >= EVENT_BATCH_SIZE) {
            flushEvents()
        }
    }

    private fun startEventFlushTimer() {
        flushJob?.cancel()
        flushJob = scope.launch {
            while (isActive) {
                delay(EVENT_FLUSH_INTERVAL_MS)
                if (pendingEvents.isNotEmpty()) {
                    flushEvents()
                }
            }
        }
    }

    fun flushEvents() {
        if (pendingEvents.isEmpty()) return

        val eventsToSend = pendingEvents.toList()
        pendingEvents.clear()

        val request = EventBatchRequest(
            userId = userId,
            sessionId = sessionId,
            events = eventsToSend
        )

        val json = gson.toJson(request)
        val body = json.toRequestBody("application/json".toMediaType())

        val httpRequest = Request.Builder()
            .url("$apiBaseUrl/api/v2/track/events")
            .post(body)
            .build()

        client.newCall(httpRequest).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e(TAG, "Failed to flush events", e)
                // Re-queue events on failure
                pendingEvents.addAll(0, eventsToSend)
            }

            override fun onResponse(call: Call, response: Response) {
                response.close()
                if (!response.isSuccessful) {
                    Log.w(TAG, "Event flush failed with code ${response.code}")
                    pendingEvents.addAll(0, eventsToSend)
                }
            }
        })
    }

    // MARK: - Conversion Tracking

    fun trackConversion(
        experimentId: String,
        variantId: String,
        conversionType: String = "primary",
        value: Double? = null
    ) {
        val request = ConversionRequest(
            userId = userId,
            sessionId = sessionId,
            experimentId = experimentId,
            variantId = variantId,
            conversionType = conversionType,
            value = value
        )

        val json = gson.toJson(request)
        val body = json.toRequestBody("application/json".toMediaType())

        val httpRequest = Request.Builder()
            .url("$apiBaseUrl/api/v2/track/conversion")
            .post(body)
            .build()

        client.newCall(httpRequest).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e(TAG, "Failed to track conversion", e)
            }

            override fun onResponse(call: Call, response: Response) {
                response.close()
                if (!response.isSuccessful) {
                    Log.w(TAG, "Conversion tracking failed with code ${response.code}")
                }
            }
        })
    }

    // MARK: - Lifecycle Events

    fun trackScreenView(screenName: String, properties: Map<String, Any> = emptyMap()) {
        trackEvent(
            eventName = "screen_viewed",
            properties = properties + mapOf("screen_name" to screenName)
        )
    }

    override fun onStart(owner: LifecycleOwner) {
        // App came to foreground - new session
        sessionId = generateSessionId()
        trackEvent("app_foreground")
    }

    override fun onStop(owner: LifecycleOwner) {
        trackEvent("app_background")
        flushEvents()
    }

    // MARK: - Context

    private fun getDeviceContext(): Map<String, Any> {
        val displayMetrics = context.resources.displayMetrics
        return mapOf(
            "screen_width" to displayMetrics.widthPixels,
            "screen_height" to displayMetrics.heightPixels,
            "density" to displayMetrics.density,
            "platform" to "android",
            "os_version" to android.os.Build.VERSION.SDK_INT,
            "device_model" to android.os.Build.MODEL,
            "device_manufacturer" to android.os.Build.MANUFACTURER
        )
    }

    // MARK: - Cleanup

    fun destroy() {
        flushEvents()
        flushJob?.cancel()
        scope.cancel()
        ProcessLifecycleOwner.get().lifecycle.removeObserver(this)
    }
}

// MARK: - Jetpack Compose Support

/**
 * Compose integration example:
 *
 * ```kotlin
 * @Composable
 * fun AdaptiveProductCard(
 *     experimentId: String,
 *     originalContent: String
 * ) {
 *     val adaptive = AdaptiveIdentity.getInstance(LocalContext.current)
 *     var content by remember { mutableStateOf(originalContent) }
 *     var isLoading by remember { mutableStateOf(true) }
 *     var variantId by remember { mutableStateOf<String?>(null) }
 *
 *     LaunchedEffect(experimentId) {
 *         adaptive.generateVariant(
 *             experimentId = experimentId,
 *             originalContent = originalContent,
 *             componentType = "product_card",
 *             goal = "add_to_cart"
 *         ) { result ->
 *             result.onSuccess { variant ->
 *                 content = variant.generatedContent
 *                 variantId = variant.variantId
 *                 isLoading = false
 *             }.onFailure {
 *                 content = originalContent
 *                 isLoading = false
 *             }
 *         }
 *     }
 *
 *     if (isLoading) {
 *         CircularProgressIndicator()
 *     } else {
 *         AndroidView(
 *             factory = { context ->
 *                 WebView(context).apply {
 *                     loadData(content, "text/html", "UTF-8")
 *                 }
 *             }
 *         )
 *     }
 * }
 * ```
 */
