//
//  DigitCount.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation


//http://stackoverflow.com/questions/37335286/given-a-number-n-find-how-many-digits-in-that-number-are-useful-a-digit-in-the

extension Int {
	
    /// returns number of digits in Int number
    public var digitCount: Int {
        get {
            return numberOfDigits(in: self)
        }
    }
	
    // private recursive method for counting digits
    private func numberOfDigits(in number: Int) -> Int {
        if abs(number) < 10 {
            return 1
        } else {
            return 1 + numberOfDigits(in: number/10)
        }
    }
}
