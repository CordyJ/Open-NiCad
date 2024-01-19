//
//  KeychainAccess+BoltMobile.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-24.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation
import KeychainAccess

extension Keychain {
    
    struct UsedCoupons:Codable {
        var usedCoupons:[String]
    }
    
    func useCoupon(id:String) {
        var usedCoupons = allCoupons()
        usedCoupons.append(id)
        let data = NSKeyedArchiver.archivedData(withRootObject: usedCoupons)
        
        do{
            try self.set(data, key: Constants.Keychain.UsedCouponsKey)
        } catch {
            print(error)
        }
    }
    
    func isCouponUsed(id:String) -> Bool {
        let usedCoupons = allCoupons()
        if usedCoupons.contains(id) {
            return true
        } else {
            return false
        }
    }
    
    private func allCoupons() -> [String] {
        do {
            if let data = try self.getData(Constants.Keychain.UsedCouponsKey), let coupons = NSKeyedUnarchiver.unarchiveObject(with: data) as? [String] {
                return coupons
            } else {
                return []
            }
        } catch {
            print(error)
            return []
        }
    }
}
