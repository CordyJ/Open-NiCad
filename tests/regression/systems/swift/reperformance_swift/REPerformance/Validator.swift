//
//  Validator.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-11.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation

func isValidEmail(email:String) -> Bool {
    let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
    
    let emailTest = NSPredicate(format:"SELF MATCHES %@", emailRegEx)
    return emailTest.evaluate(with: email)
}
