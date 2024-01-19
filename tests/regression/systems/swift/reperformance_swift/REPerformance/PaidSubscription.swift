//
//  PaidSubscription.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-30.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import StoreKit

public class PaidSubscription: NSObject, NSCoding {
    
    public enum Level: Int {
        case monthly = 1
        case yearly
        
        init?(productId: String) {
            if productId.contains("monthly") {
                self = .monthly
            } else if productId.contains("annually") {
                self = .yearly
            } else {
                return nil
            }
        }
        
        public var seconds: TimeInterval {
            switch self {
            case .monthly:
                return 30*24*60*60
            case .yearly:
                return 365*24*60*60
            }
        }
    }
    
    public let productId: String
    public let purchaseDate: Date
    public let expiresDate: Date
    public let level: Level
    
    public var isActive: Bool {
        return (purchaseDate...expiresDate).contains(Date())
    }
    
    init?(transaction: SKPaymentTransaction) {
        guard
            let level = Level(productId: transaction.payment.productIdentifier),
            let purchaseDate = transaction.transactionDate
            else {
                return nil
        }
        
        self.productId = transaction.payment.productIdentifier
        self.purchaseDate = purchaseDate
        self.expiresDate = purchaseDate.addingTimeInterval(level.seconds)
        self.level = level
    }
    
    required public init?(coder decoder: NSCoder) {
        guard
            let productId = decoder.decodeObject(forKey: Constants.PaidSubscriptionKey.ProductIdentifierKey) as? String,
            let purchaseDate = decoder.decodeObject(forKey: Constants.PaidSubscriptionKey.PurchaseDateKey) as? Date,
            let expiresDate = decoder.decodeObject(forKey: Constants.PaidSubscriptionKey.ExpiresDateKey) as? Date,
            let level = Level(rawValue: decoder.decodeInteger(forKey: Constants.PaidSubscriptionKey.LevelKey))
            else {
                return nil
        }
        
        self.productId = productId
        self.purchaseDate = purchaseDate
        self.expiresDate = expiresDate
        self.level = level
    }
    
    public func encode(with coder: NSCoder) {
        coder.encode(productId, forKey: Constants.PaidSubscriptionKey.ProductIdentifierKey)
        coder.encode(purchaseDate, forKey: Constants.PaidSubscriptionKey.PurchaseDateKey)
        coder.encode(expiresDate, forKey: Constants.PaidSubscriptionKey.ExpiresDateKey)
        coder.encode(level.rawValue, forKey: Constants.PaidSubscriptionKey.LevelKey)
    }
}
