//
//  ProfileDataProvider.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya


class ProfileDataProvider {
	
	let submitProvider = MoyaProvider<SubmitService>()
	
	
	func submitProfile(lifestyle: LifestyleType, gender: String, weight: Int, age: Int, countryCode: String, regionCode: String, completion: @escaping (Bool, String?)->()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(false, L10n.userTokenMissingMessage)
			return
		}
		
		self.submitProvider.request(.submitProfile(token: token, lifestyle_category: lifestyle, gender: gender, weight: weight, age: age, country_code: countryCode, region_code: regionCode)) { result in
			do {
				let response = try result.dematerialize()
				let success = try response.mapSuccess()
				completion(success, nil)
			} catch {
				completion(false, error.localizedDescription)
			}
		}
	}
}
