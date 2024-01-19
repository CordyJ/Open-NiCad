//
//  Subscription.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-29.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import StoreKit

private var formatter: NumberFormatter = {
    let formatter = NumberFormatter()
    formatter.numberStyle = .currency
    formatter.formatterBehavior = .behavior10_4
    
    return formatter
}()

struct Subscription {
    let product: SKProduct
    let formattedPrice: String
    
    init(product: SKProduct) {
        self.product = product
        
        if formatter.locale != self.product.priceLocale {
            formatter.locale = self.product.priceLocale
        }

        formattedPrice = formatter.string(from: product.price) ?? "\(product.price)"
    }
}
