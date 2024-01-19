//
//  DateFormats.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation

extension DateFormatter{
    
    static func exercisesResultsDateFormatter() -> DateFormatter
    {
        let dateFormatter:DateFormatter = DateFormatter()
        dateFormatter.dateFormat = "MMMM d, y"
        return dateFormatter
    }
    
    static func displayScoreResultsDateFormatter() -> DateFormatter
    {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "MM/dd/yyyy"
        return dateFormatter
    }
    
    static func serverDateFormatter() -> DateFormatter
    {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy'-'MM'-'dd'T'HH':'mm':'ss'Z'"	// RFC 3339 Format
        dateFormatter.timeZone = TimeZone(abbreviation: "UTC")
        return dateFormatter
    }
    
    static func storedDateFormatter() -> DateFormatter
    {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "MM-dd-yyyy-HH-mm-ss"
        return dateFormatter
    }
}
