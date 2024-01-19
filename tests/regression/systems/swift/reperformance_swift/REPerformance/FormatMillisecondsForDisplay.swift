//
//  FormatMillisecondsForDisplay.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


class FormatMillisecondsForDisplay: NSObject {
	
	static func convertScoreForDisplayMileRun(score: String) -> String? {
		guard let timeIntervalMilliseconds = TimeInterval(score) else {
			return nil
		}
		
		let timeDateComponentsFormatter = DateComponentsFormatter()
		timeDateComponentsFormatter.allowedUnits = [.minute, .second]
		timeDateComponentsFormatter.unitsStyle = .positional
		timeDateComponentsFormatter.zeroFormattingBehavior = .pad
		
		let timeIntervalSeconds = timeIntervalMilliseconds / 1000
		let milliseconds = Int(timeIntervalMilliseconds.truncatingRemainder(dividingBy: 1000))
		let millisecondsDecimal:Int = milliseconds/10
		if let timeString = timeDateComponentsFormatter.string(from: timeIntervalSeconds) {
			return "\(timeString).\(String(format: "%02d", millisecondsDecimal))"
		} else {
			return nil
		}
	}
	
	static func convertScoreForDisplayFortyYardDash(score: String) -> String? {
		guard let timeIntervalMilliseconds = TimeInterval(score) else {
			return nil
		}
		
		let timeDateComponentsFormatter = DateComponentsFormatter()
		timeDateComponentsFormatter.allowedUnits = [.second]
		timeDateComponentsFormatter.unitsStyle = .positional
		timeDateComponentsFormatter.zeroFormattingBehavior = .pad
		
		let timeIntervalSeconds = timeIntervalMilliseconds / 1000
		let milliseconds = Int(timeIntervalMilliseconds.truncatingRemainder(dividingBy: 1000))
		let millisecondsDecimal:Int = milliseconds/10
		if let timeString = timeDateComponentsFormatter.string(from: timeIntervalSeconds) {
			return "\(timeString).\(String(format: "%02d", millisecondsDecimal))"
		} else {
			return nil
		}
	}
}
