//
//  UserDefaults+BoltMobileUserInformation.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-19.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation

extension UserDefaults {
    
    class func registerBoltMobileUserInformationDefaults(){
        standard.register(defaults: [Constants.UserDefaultsKey.UserFirstName : "",
                                     Constants.UserDefaultsKey.UserLastName : "",
                                     Constants.UserDefaultsKey.UserEmail : "",
                                     Constants.UserDefaultsKey.UserPhoneNumber : "",
                                     Constants.UserDefaultsKey.UserToken : ""])
    }
    
    class var userFirstName: String? {
        get {
            return standard.string(forKey: Constants.UserDefaultsKey.UserFirstName)
        }
        set {
            standard.set(newValue, forKey: Constants.UserDefaultsKey.UserFirstName)
        }
    }
    
    class var userLastName: String? {
        get {
            return standard.string(forKey: Constants.UserDefaultsKey.UserLastName)
        }
        set {
            standard.set(newValue, forKey: Constants.UserDefaultsKey.UserLastName)
        }
    }
    
    class var userEmail: String? {
        get {
            return standard.string(forKey: Constants.UserDefaultsKey.UserEmail)
        }
        set {
            standard.set(newValue, forKey: Constants.UserDefaultsKey.UserEmail)
        }
    }
    
    class var userPhoneNumber: String? {
        get {
            return standard.string(forKey: Constants.UserDefaultsKey.UserPhoneNumber)
        }
        set {
            standard.set(newValue, forKey: Constants.UserDefaultsKey.UserPhoneNumber)
        }
    }
    
    class var userToken: String? {
        get {
            return standard.string(forKey: Constants.UserDefaultsKey.UserToken)
        }
        set {
            standard.set(newValue, forKey: Constants.UserDefaultsKey.UserToken)
        }
    }
}
