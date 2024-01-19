//
//  ChallengeDataProvider.swift
//  REPerformance
//
//  Created by Alan Yeung on 2018-05-30.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Result
import Moya


class ChallengeDataProvider {
	
	let retrieveProvider = MoyaProvider<RetrieveService>()
	let submitProvider = MoyaProvider<SubmitService>()
	let leaderboardProvider = MoyaProvider<SubmitService>()
	
	
	func retreiveChallenges(completion: @escaping (Result<[Challenge], REPerformanceError>) -> ()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(.failure(.userTokenMissing))
			return
		}
		
		self.retrieveProvider.request(.getChallenges(token: token)) { result in
			do {
				let response = try result.dematerialize()
				let challenges = try response.map([Challenge].self, atKeyPath: "data")
				completion(.success(challenges))
			} catch {
				completion(.failure(.requestFailed(error.localizedDescription)))
			}
		}
	}
	
	func submitChallengeAction(challenge: Challenge, completion: @escaping (Result<Bool, REPerformanceError>) -> ()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(.failure(.userTokenMissing))
			return
		}
		
		let challengeCompletion: Completion = { result in
			do {
				let response = try result.dematerialize()
				let isSuccess = try response.mapSuccess()
				completion(.success(isSuccess))
			} catch {
				completion(.failure(.requestFailed(error.localizedDescription)))
			}
		}
		
		if challenge.hasJoined {
			self.submitProvider.request(.submitChallengeLeave(token:token, challenge: challenge), completion: challengeCompletion)
		} else {
			self.submitProvider.request(.submitChallengeJoin(token:token, challenge: challenge), completion: challengeCompletion)
		}
	}
	
	func retreiveLeaderboard(challenge: Challenge, gym: Gym? = nil, completion: @escaping (Result<[Athlete], REPerformanceError>) -> ()) {
		self.retrieveProvider.request(.getChallengeLeaderboard(challenge: challenge, gym: gym)) { result in
			do {
				let response = try result.dematerialize()
				let athletes = try response.map([Athlete].self, atKeyPath: "data")
				completion(.success(athletes))
			} catch {
				completion(.failure(.requestFailed(error.localizedDescription)))
			}
		}
	}
}
