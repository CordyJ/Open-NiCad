//
//  CreditsUpdater.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-08.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation


class CreditsUpdater {
	
	static func updateCredits(completion: ((Bool)->())?) {
		let dataProvider = CreditsDataProvider()
		
		dataProvider.retrieveCredits() { (retrieveCreditsResult) in
			switch retrieveCreditsResult {
			case .success(let credits):
				UserDefaults.standard.userCredits = "\(credits.totalCredits)"
				UserDefaults.standard.userDollars = Float(credits.dollarValue)
				completion?(true)
			case .failure(let error):
				UserDefaults.standard.userCredits = error.localizedDescription
				completion?(false)
			}
		}
	}
}
