//
//  DateConversion.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-27.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


extension Date {
	
	// Convert UTC (or GMT) to local time
	func toLocalTime() -> Date {
		let timezone = TimeZone.current
		let seconds = TimeInterval(timezone.secondsFromGMT(for: self))
		return Date(timeInterval: seconds, since: self)
	}
	
	// Convert local time to UTC (or GMT)
	func toGlobalTime() -> Date {
		let timezone = TimeZone.current
		let seconds = -TimeInterval(timezone.secondsFromGMT(for: self))
		return Date(timeInterval: seconds, since: self)
	}
}
