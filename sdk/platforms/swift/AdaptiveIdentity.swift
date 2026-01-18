/**
 * Swift/iOS SDK for Adaptive Identity Engine
 *
 * Usage:
 * ```swift
 * import AdaptiveIdentity
 *
 * class ProductViewController: UIViewController {
 *     let adaptive = AdaptiveIdentity.shared
 *
 *     override func viewDidLoad() {
 *         super.viewDidLoad()
 *
 *         adaptive.generateVariant(
 *             experimentId: "product-hero",
 *             originalContent: "<div>Original Product</div>",
 *             componentType: "product_card",
 *             goal: "add_to_cart"
 *         ) { result in
 *             switch result {
 *             case .success(let variant):
 *                 self.updateUI(with: variant.generatedContent)
 *             case .failure(let error):
 *                 print("Error: \(error)")
 *             }
 *         }
 *     }
 *
 *     @IBAction func addToCartTapped() {
 *         adaptive.trackConversion(
 *             experimentId: "product-hero",
 *             conversionType: "add_to_cart"
 *         )
 *     }
 * }
 * ```
 */

import Foundation

// MARK: - Models

public struct VariantResponse: Codable {
    public let success: Bool
    public let variantId: String
    public let generatedContent: String
    public let identityState: String?
    public let confidence: Double
    public let experimentId: String
    public let isControl: Bool
    public let rationale: String

    enum CodingKeys: String, CodingKey {
        case success
        case variantId = "variant_id"
        case generatedContent = "generated_content"
        case identityState = "identity_state"
        case confidence
        case experimentId = "experiment_id"
        case isControl = "is_control"
        case rationale
    }
}

public struct TrackingEvent: Codable {
    public let eventName: String
    public let sessionId: String
    public let userId: String
    public let componentId: String?
    public let properties: [String: AnyCodable]

    enum CodingKeys: String, CodingKey {
        case eventName = "event_name"
        case sessionId = "session_id"
        case userId = "user_id"
        case componentId = "component_id"
        case properties
    }
}

// MARK: - AnyCodable Helper

public struct AnyCodable: Codable {
    public let value: Any

    public init(_ value: Any) {
        self.value = value
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if let intValue = try? container.decode(Int.self) {
            value = intValue
        } else if let doubleValue = try? container.decode(Double.self) {
            value = doubleValue
        } else if let stringValue = try? container.decode(String.self) {
            value = stringValue
        } else if let boolValue = try? container.decode(Bool.self) {
            value = boolValue
        } else {
            value = ""
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        if let intValue = value as? Int {
            try container.encode(intValue)
        } else if let doubleValue = value as? Double {
            try container.encode(doubleValue)
        } else if let stringValue = value as? String {
            try container.encode(stringValue)
        } else if let boolValue = value as? Bool {
            try container.encode(boolValue)
        }
    }
}

// MARK: - AdaptiveIdentity SDK

public class AdaptiveIdentity {

    // MARK: - Singleton

    public static let shared = AdaptiveIdentity()

    // MARK: - Properties

    private let apiBaseURL: String
    private let userId: String
    private var sessionId: String
    private var pendingEvents: [TrackingEvent] = []
    private let eventQueue = DispatchQueue(label: "com.adaptive-identity.events")

    // MARK: - Keys

    private let userIdKey = "adaptive_identity_uid"
    private let sessionIdKey = "adaptive_identity_session"

    // MARK: - Initialization

    public init(apiBaseURL: String = "http://localhost:8000") {
        self.apiBaseURL = apiBaseURL
        self.userId = Self.getOrCreateUserId(key: userIdKey)
        self.sessionId = Self.generateSessionId()

        // Sync pending events when app becomes active
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(syncPendingEvents),
            name: UIApplication.didBecomeActiveNotification,
            object: nil
        )
    }

    // MARK: - User/Session Management

    private static func getOrCreateUserId(key: String) -> String {
        if let existingId = UserDefaults.standard.string(forKey: key) {
            return existingId
        }

        let newId = UUID().uuidString
        UserDefaults.standard.set(newId, forKey: key)
        return newId
    }

    private static func generateSessionId() -> String {
        return "session_\(Int(Date().timeIntervalSince1970))_\(UUID().uuidString.prefix(8))"
    }

    public func getUserId() -> String {
        return userId
    }

    public func getSessionId() -> String {
        return sessionId
    }

    // MARK: - Generate Variant

    public func generateVariant(
        experimentId: String,
        originalContent: String,
        componentType: String = "generic",
        goal: String = "conversion",
        context: [String: Any]? = nil,
        completion: @escaping (Result<VariantResponse, Error>) -> Void
    ) {
        guard let url = URL(string: "\(apiBaseURL)/api/v2/generate") else {
            completion(.failure(NSError(domain: "AdaptiveIdentity", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "user_id": userId,
            "session_id": sessionId,
            "experiment_id": experimentId,
            "original_content": originalContent,
            "component_type": componentType,
            "goal": goal,
            "platform": "ios",
            "context": context ?? [:]
        ]

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } catch {
            completion(.failure(error))
            return
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let data = data else {
                completion(.failure(NSError(domain: "AdaptiveIdentity", code: -2, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }

            do {
                let variant = try JSONDecoder().decode(VariantResponse.self, from: data)
                DispatchQueue.main.async {
                    completion(.success(variant))
                }
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }

    // MARK: - Event Tracking

    public func trackEvent(
        eventName: String,
        componentId: String? = nil,
        properties: [String: Any] = [:]
    ) {
        let codableProperties = properties.mapValues { AnyCodable($0) }

        let event = TrackingEvent(
            eventName: eventName,
            sessionId: sessionId,
            userId: userId,
            componentId: componentId,
            properties: codableProperties
        )

        eventQueue.async { [weak self] in
            self?.pendingEvents.append(event)
            self?.flushEventsIfNeeded()
        }
    }

    private func flushEventsIfNeeded() {
        guard pendingEvents.count >= 10 else { return }
        syncPendingEvents()
    }

    @objc private func syncPendingEvents() {
        eventQueue.async { [weak self] in
            guard let self = self, !self.pendingEvents.isEmpty else { return }

            let eventsToSync = self.pendingEvents
            self.pendingEvents = []

            guard let url = URL(string: "\(self.apiBaseURL)/api/v2/track/events") else { return }

            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")

            let body: [String: Any] = [
                "user_id": self.userId,
                "session_id": self.sessionId,
                "events": eventsToSync.map { event -> [String: Any] in
                    return [
                        "event_name": event.eventName,
                        "component_id": event.componentId ?? "",
                        "properties": event.properties.mapValues { $0.value },
                        "timestamp": ISO8601DateFormatter().string(from: Date())
                    ]
                }
            ]

            do {
                request.httpBody = try JSONSerialization.data(withJSONObject: body)
                URLSession.shared.dataTask(with: request).resume()
            } catch {
                // Re-queue events on failure
                self.eventQueue.async {
                    self.pendingEvents.insert(contentsOf: eventsToSync, at: 0)
                }
            }
        }
    }

    // MARK: - Conversion Tracking

    public func trackConversion(
        experimentId: String,
        variantId: String,
        conversionType: String = "primary",
        value: Double? = nil
    ) {
        guard let url = URL(string: "\(apiBaseURL)/api/v2/track/conversion") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        var body: [String: Any] = [
            "user_id": userId,
            "session_id": sessionId,
            "experiment_id": experimentId,
            "variant_id": variantId,
            "conversion_type": conversionType
        ]

        if let value = value {
            body["value"] = value
        }

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
            URLSession.shared.dataTask(with: request).resume()
        } catch {
            print("[AdaptiveIdentity] Failed to track conversion: \(error)")
        }
    }

    // MARK: - Lifecycle Events

    public func trackScreenView(screenName: String, properties: [String: Any] = [:]) {
        var props = properties
        props["screen_name"] = screenName
        trackEvent(eventName: "screen_viewed", properties: props)
    }

    public func trackAppBackground() {
        trackEvent(eventName: "app_background")
        syncPendingEvents()
    }

    public func trackAppForeground() {
        sessionId = Self.generateSessionId() // New session on foreground
        trackEvent(eventName: "app_foreground")
    }
}

// MARK: - SwiftUI Support

#if canImport(SwiftUI)
import SwiftUI

@available(iOS 13.0, *)
public struct AdaptiveView<Content: View>: View {
    let experimentId: String
    let originalContent: String
    let componentType: String
    let goal: String
    let content: (String, Bool) -> Content

    @State private var generatedContent: String = ""
    @State private var isLoading: Bool = true

    public init(
        experimentId: String,
        originalContent: String,
        componentType: String = "generic",
        goal: String = "conversion",
        @ViewBuilder content: @escaping (String, Bool) -> Content
    ) {
        self.experimentId = experimentId
        self.originalContent = originalContent
        self.componentType = componentType
        self.goal = goal
        self.content = content
    }

    public var body: some View {
        content(generatedContent.isEmpty ? originalContent : generatedContent, isLoading)
            .onAppear {
                loadVariant()
            }
    }

    private func loadVariant() {
        AdaptiveIdentity.shared.generateVariant(
            experimentId: experimentId,
            originalContent: originalContent,
            componentType: componentType,
            goal: goal
        ) { result in
            switch result {
            case .success(let variant):
                self.generatedContent = variant.generatedContent
                self.isLoading = false
            case .failure:
                self.generatedContent = originalContent
                self.isLoading = false
            }
        }
    }
}
#endif
