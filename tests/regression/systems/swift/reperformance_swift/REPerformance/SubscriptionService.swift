//
//  SubscriptionService.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-29.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import StoreKit
import KeychainAccess
import Moya


class SubscriptionService: NSObject {

    static let optionsLoadedNotification = Notification.Name("SubscriptionServiceOptionsLoadedNotification")
    static let purchaseSuccessfulNotification = Notification.Name("SubscriptionServicePurchaseSuccessfulNotification")
    static let purchaseIncompleteNotification = Notification.Name("SubscriptionServicePurchaseIncompleteNotification")

    static let shared = SubscriptionService()
	
	static func checkIsInConferenceMode(completion: @escaping ((Bool)->())) {
		let provider = MoyaProvider<RetrieveService>()
		provider.request(.conferenceMode()) { result in
			do {
				let response = try result.dematerialize()
				let isConferenceModeEnabled = try response.mapConferenceMode()
				completion(isConferenceModeEnabled)
			} catch {
				completion(false)
			}
		}
	}
	
    var currentSubscription: PaidSubscription? {
        get {
            let keychain = Keychain(service: Constants.Keychain.Service)
            guard let data = try! keychain.getData(Constants.Keychain.CurrentSubscription),
                let subscription = NSKeyedUnarchiver.unarchiveObject(with: data) as? PaidSubscription else {
                return nil
            }
            
            return subscription
        }
        set {
            if let subscription = newValue, subscription.isActive == true {
                let encodedData = NSKeyedArchiver.archivedData(withRootObject: subscription)
                let keychain = Keychain(service: Constants.Keychain.Service)
                do {
                    try keychain.set(encodedData, key: Constants.Keychain.CurrentSubscription)
                }
                catch let error {
                    print(error)
                }
            }
        }
    }
    
    var isActive: Bool {
        get {
            #if USE_PRODUCTION
                if let subscription = currentSubscription, subscription.isActive == true {
                    return true
                }
                return false
            #else
                return true
            #endif
        }
    }

    var options: [Subscription]? {
        didSet {
            NotificationCenter.default.post(name: SubscriptionService.optionsLoadedNotification, object: options)
        }
    }

    func loadSubscriptionOptions() {
        
        let productIDPrefix = Bundle.main.bundleIdentifier! + ".sub."
        
        let proMonthly = productIDPrefix + "pro.monthly2"
        let proAnnually  = productIDPrefix + "pro.annually2"
        
        let productIDs = Set([proMonthly, proAnnually])
        
        let request = SKProductsRequest(productIdentifiers: productIDs)
        request.delegate = self
        request.start()
    }
    
    func purchase(subscription: Subscription) {
        let payment = SKPayment(product: subscription.product)
        SKPaymentQueue.default().add(payment)
    }
    
    func restorePurchases() {
        SKPaymentQueue.default().restoreCompletedTransactions()
    }
    
    fileprivate var purchaseTimer: Timer?
}


// MARK: - SKProductsRequestDelegate

extension SubscriptionService: SKProductsRequestDelegate {
    func productsRequest(_ request: SKProductsRequest, didReceive response: SKProductsResponse) {
        options = response.products.map { Subscription(product: $0) }
    }
}

// MARK: - SKPaymentTransactionObserver

extension SubscriptionService: SKPaymentTransactionObserver {
    
    func paymentQueue(_ queue: SKPaymentQueue, updatedTransactions transactions: [SKPaymentTransaction]) {
        for transaction in transactions {
            switch transaction.transactionState {
            case .purchasing:
                handlePurchasingState(for: transaction, in: queue)
            case .purchased:
                handlePurchasedState(for: transaction, in: queue)
            case .restored:
                handleRestoredState(for: transaction, in: queue)
            case .failed:
                handleFailedState(for: transaction, in: queue)
            case .deferred:
                handleDeferredState(for: transaction, in: queue)
            }
        }
    }
    
    fileprivate func handlePurchasingState(for transaction: SKPaymentTransaction, in queue: SKPaymentQueue) {}
    
    fileprivate func handlePurchasedState(for transaction: SKPaymentTransaction, in queue: SKPaymentQueue) {
        saveSubscriptionFromTransaction(transaction)
        
        // Since we can get multiple purchases in a row, will delay making the call to avoid triggering "purchase successful" handlers multiple times.
        purchaseTimer?.invalidate()
        purchaseTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: false, block: { timer in
            NotificationCenter.default.post(name: SubscriptionService.purchaseSuccessfulNotification, object: nil)
        })
        queue.finishTransaction(transaction) // this should be the last method to be called.
    }
    
    fileprivate func handleRestoredState(for transaction: SKPaymentTransaction, in queue: SKPaymentQueue) {
        saveSubscriptionFromTransaction(transaction)
        queue.finishTransaction(transaction)  // this should be the last method to be called.
        // Will fire a notification in paymentQueueRestoreCompletedTransactionsFinished.
    }
    
    fileprivate func handleFailedState(for transaction: SKPaymentTransaction, in queue: SKPaymentQueue) {
        purchaseTimer?.invalidate()
        if let error = transaction.error {
            // Avoids displaying errors for cases where the user cancels the transaction.
            let userInfo: [AnyHashable : Any]?
            if let storeError = error as? SKError, storeError._nsError.domain == SKErrorDomain && storeError.code == .paymentCancelled {
                userInfo = nil
            }
            else {
                userInfo = ["message": error.localizedDescription]
            }
            NotificationCenter.default.post(name: SubscriptionService.purchaseIncompleteNotification, object: nil, userInfo: userInfo)
        }
        queue.finishTransaction(transaction)  // this should be the last method to be called.
    }
    
    fileprivate func handleDeferredState(for transaction: SKPaymentTransaction, in queue: SKPaymentQueue) {
        NotificationCenter.default.post(name: SubscriptionService.purchaseIncompleteNotification, object: nil, userInfo: ["message": L10n.learnAboutProPurchaseDeferred])
    }
    
    fileprivate func saveSubscriptionFromTransaction(_ transaction: SKPaymentTransaction) {
        // Avoids saving older receipts when we get multiple returned from Apple.
        if (currentSubscription == nil) {
            currentSubscription = PaidSubscription(transaction: transaction)
        }
        else if let purchaseDate = currentSubscription?.purchaseDate,
            let transactionDate = transaction.transactionDate,
            transactionDate >= purchaseDate {
            currentSubscription = PaidSubscription(transaction: transaction)
        }
    }
    
    func paymentQueueRestoreCompletedTransactionsFinished(_ queue: SKPaymentQueue) {
        if currentSubscription == nil {
            NotificationCenter.default.post(name: SubscriptionService.purchaseIncompleteNotification, object: nil, userInfo: ["message": L10n.learnAboutProSubscriptionExpired])
        }
        else {
            NotificationCenter.default.post(name: SubscriptionService.purchaseSuccessfulNotification, object: nil)
        }
    }
    
    func paymentQueue(_ queue: SKPaymentQueue, restoreCompletedTransactionsFailedWithError error: Error) {
        NotificationCenter.default.post(name: SubscriptionService.purchaseIncompleteNotification, object: nil, userInfo: ["message": error.localizedDescription])
    }
}

// MARK: - Conference Mode Response

extension Moya.Response {
	
	func mapConferenceMode() throws -> Bool {
		let responseObject = try self.map(to: REPerformanceResponse.self)
		
		guard responseObject.success else {
			throw REPerformanceError.requestFailed(responseObject.message)
		}
		
		let jsonData = responseObject.data
		
		guard let isConferenceModeOn = jsonData["conference_mode_on"]?.boolValue else {
			throw MoyaError.jsonMapping(self)
		}
		
		return isConferenceModeOn
	}
}
