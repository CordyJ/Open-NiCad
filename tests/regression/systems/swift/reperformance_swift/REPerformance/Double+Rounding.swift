//
//  DoubleRounding.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-15.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import Foundation


extension Double {
    
    public func roundToNearestFive() -> Int {
        let test = self
        return 5 * Int(Darwin.round(test/5.0))
    }
}
