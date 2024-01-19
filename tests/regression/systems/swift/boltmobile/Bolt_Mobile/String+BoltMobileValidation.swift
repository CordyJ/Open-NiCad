//
//  String+BoltMobileValidation.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-19.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation

extension String {
    func isValidEmail() -> Bool {
        let emailValidationRegex:String = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailValidationRegex)
        return emailPredicate.evaluate(with:self)
    }
    
    func isValidPhoneNumber() -> Bool {
        let phoneValidationRegex:String = "[0-9]{10}"
        let phonePredicate = NSPredicate(format: "SELF MATCHES %@", phoneValidationRegex)
        return phonePredicate.evaluate(with:self)
    }
}

