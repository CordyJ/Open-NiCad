//
//  LeaderboardDataProvider.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-06-01.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya
import SwiftyJSON


class LeaderboardDataProvider {
	
	let retrieveProvider = MoyaProvider<RetrieveService>()
	let submitProvider = MoyaProvider<SubmitService>()
	
	func retreiveLeaderboard(group: LeaderboardGroup, filterAge: Bool, exercise: ExerciseCategory?, testFormat: ExerciseTestFormat?, completion: @escaping (Leaderboard?, String?)->()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(nil, L10n.userTokenMissingMessage)
			return
		}
		
		if let exercise = exercise, let testFormat = testFormat {
			self.retrieveProvider.request(.getLeaderboard(token: token, group: group, filter_age: filterAge, exercise: exercise, test_format: testFormat)) { (result) in
				do {
					let response = try result.dematerialize()
					let leaderboard = try response.map(Leaderboard.self, atKeyPath: "data")
					completion(leaderboard, nil)
				} catch {
					completion(nil, error.localizedDescription)
				}
			}
		}
		else {
			self.retrieveProvider.request(.getDefaultLeaderboard(token: token, group: group, filter_age: filterAge)) { (result) in
				do {
					let response = try result.dematerialize()
					let leaderboard = try response.map(Leaderboard.self, atKeyPath: "data")
					completion(leaderboard, nil)
				} catch {
					completion(nil, error.localizedDescription)
				}
			}
		}
	}
	
	func retreiveGymLeaderboard(exercise: ExerciseCategory, testFormat: ExerciseTestFormat, completion: @escaping (Leaderboard?, String?) -> ()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(nil, L10n.userTokenMissingMessage)
			return
		}
		
		self.retrieveProvider.request(.getGymLeaderboard(token: token, exercise: exercise, test_format: testFormat)) { (result) in
			do {
				let response = try result.dematerialize()
				let leaderboard = try response.map(Leaderboard.self, atKeyPath: "data")
				completion(leaderboard, nil)
			} catch {
				completion(nil, error.localizedDescription)
			}
		}
	}
	
	func submitGym(placeID: String, name: String, region: String, completion: @escaping (Bool, String?) -> ()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(false, L10n.userTokenMissingMessage)
			return
		}
		
		self.submitProvider.request(.submitGym(token: token, placeID: placeID, name: name, region: region)) { (result) in
			do {
				let _ = try result.dematerialize()
				completion(true, nil)
			} catch {
				completion(false, error.localizedDescription)
			}
		}
	}
}
