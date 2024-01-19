//
//  UserDefaults+BoltMobile.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation

extension UserDefaults {
    
    class func registerBoltMobileDefaults(){
        standard.register(defaults: [Constants.UserDefaultsKey.SeenReferralsInstructions : false,
                                     Constants.UserDefaultsKey.SeenWelcomeVC : false])
    }
    
    class var hasSeenReferralsInstructions: Bool? {
        get {
            return standard.bool(forKey: Constants.UserDefaultsKey.SeenReferralsInstructions)
        }
        set {
            standard.set(newValue, forKey: Constants.UserDefaultsKey.SeenReferralsInstructions)
        }
    }
    
    class var hasSeenWelcomeVC: Bool? {
        get {
            return standard.bool(forKey: Constants.UserDefaultsKey.SeenWelcomeVC)
        }
        set {
            standard.set(newValue, forKey: Constants.UserDefaultsKey.SeenWelcomeVC)
        }
    }
}
