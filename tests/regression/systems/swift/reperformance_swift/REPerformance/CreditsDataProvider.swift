//
//  CreditsDataProvider.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-08.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Result
import Moya


class CreditsDataProvider {
	
	let retrieveProvider = MoyaProvider<RetrieveService>()
	
	
	func retrieveCredits(completion: @escaping(Result<RepCredits, REPerformanceError>) -> ()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(.failure(.userTokenMissing))
			return
		}
		
		self.retrieveProvider.request(.getCredits(token: token)) { (result) in
			do {
				let response = try result.dematerialize()
				let repCredits = try response.map(RepCredits.self, atKeyPath: "data")
				completion(.success(repCredits))
			} catch {
				completion(.failure(.requestFailed(error.localizedDescription)))
			}
		}
	}
}
