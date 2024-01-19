//
//  AchievementsDataProvider.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2017-05-25.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya
import SwiftyJSON


struct Achievements {
	let mileRun: Achievement
	let fourtyYardDash: Achievement
	let benchPress: Achievement
	let deadlift: Achievement
	let squat: Achievement
	let militaryPress: Achievement
    let challenge: Achievement_Challenge
    let loyalty: Achievement_Loyalty
}

struct Achievement {
	let personalBestCount: Int
	let personalBestCreditWorth: Int
	let videoCount: Int
	let videoCreditWorth: Int
	let submissionCount: Int
	let submissionCreditWorth: Int
}

struct Achievement_Challenge {
    let joinChallengeCount: Int
    let joinChallengeCreditWorth: Int
    let challengeStreakCount: Int
    let challgeneStreakCreditWorth: Int
}

struct Achievement_Loyalty {
    let dailyVisitCount: Int
    let dailyVisitCreditWorth: Int
}


class AchievementsDataProvider {
	let provider = MoyaProvider<AchievementsService>()
	
	func retrieveAchievements(completion: @escaping (Achievements?, String?)->()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(nil, L10n.userTokenMissingMessage)
			return
		}
		
		provider.request(.getAchievements(token: token)) { result in
			do {
				let response = try result.dematerialize()
				let achievements = try response.mapAchievements()
				completion(achievements, nil)
			} catch {
				completion(nil, error.localizedDescription)
			}
		}
	}
}

extension Moya.Response {
	
	func mapAchievements() throws -> Achievements {
		let responseObject = try self.map(to: REPerformanceResponse.self)
		
		guard responseObject.success else {
			throw REPerformanceError.requestFailed(responseObject.message)
		}
		
		let jsonData = responseObject.data
		
		guard
			let squatData = jsonData["squat"]?.dictionary,
			let squatPersonalBest = squatData["personal_best"],
			let squatPersonalBestCount = squatPersonalBest["amount"].int,
			let squatPersonalBestCreditWorth = squatPersonalBest["value"].int,
			let squatVideo = squatData["video"],
			let squatVideoCount = squatVideo["amount"].int,
			let squatVideoCreditWorth = squatVideo["value"].int,
			let squatSubmission = squatData["submission"],
			let squatSubmissionCount = squatSubmission["amount"].int,
			let squatSubmissionCreditWorth = squatSubmission["value"].int,
		
			let benchPressData = jsonData["bench_press"]?.dictionary,
			let benchPressPersonalBest = benchPressData["personal_best"],
			let benchPressPersonalBestCount = benchPressPersonalBest["amount"].int,
			let benchPressPersonalBestCreditWorth = benchPressPersonalBest["value"].int,
			let benchPressVideo = benchPressData["video"],
			let benchPressVideoCount = benchPressVideo["amount"].int,
			let benchPressVideoCreditWorth = benchPressVideo["value"].int,
			let benchPressSubmission = benchPressData["submission"],
			let benchPressSubmissionCount = benchPressSubmission["amount"].int,
			let benchPressSubmissionCreditWorth = benchPressSubmission["value"].int,
		
			let militaryPressData = jsonData["military_press"]?.dictionary,
			let militaryPressPersonalBest = militaryPressData["personal_best"],
			let militaryPressPersonalBestCount = militaryPressPersonalBest["amount"].int,
			let militaryPressPersonalBestCreditWorth = militaryPressPersonalBest["value"].int,
			let militaryPressVideo = militaryPressData["video"],
			let militaryPressVideoCount = militaryPressVideo["amount"].int,
			let militaryPressVideoCreditWorth = militaryPressVideo["value"].int,
			let militaryPressSubmission = militaryPressData["submission"],
			let militaryPressSubmissionCount = militaryPressSubmission["amount"].int,
			let militaryPressSubmissionCreditWorth = militaryPressSubmission["value"].int,
		
			let fortyYardDashData = jsonData["forty_yard_dash"]?.dictionary,
			let fortyYardDashPersonalBest = fortyYardDashData["personal_best"],
			let fortyYardDashPersonalBestCount = fortyYardDashPersonalBest["amount"].int,
			let fortyYardDashPersonalBestCreditWorth = fortyYardDashPersonalBest["value"].int,
			let fortyYardDashVideo = fortyYardDashData["video"],
			let fortyYardDashVideoCount = fortyYardDashVideo["amount"].int,
			let fortyYardDashVideoCreditWorth = fortyYardDashVideo["value"].int,
			let fortyYardDashSubmission = fortyYardDashData["submission"],
			let fortyYardDashSubmissionCount = fortyYardDashSubmission["amount"].int,
			let fortyYardDashSubmissionCreditWorth = fortyYardDashSubmission["value"].int,
		
			let deadliftData = jsonData["deadlift"]?.dictionary,
			let deadliftPersonalBest = deadliftData["personal_best"],
			let deadliftPersonalBestCount = deadliftPersonalBest["amount"].int,
			let deadliftPersonalBestCreditWorth = deadliftPersonalBest["value"].int,
			let deadliftVideo = deadliftData["video"],
			let deadliftVideoCount = deadliftVideo["amount"].int,
			let deadliftVideoCreditWorth = deadliftVideo["value"].int,
			let deadliftSubmission = deadliftData["submission"],
			let deadliftSubmissionCount = deadliftSubmission["amount"].int,
			let deadliftSubmissionCreditWorth = deadliftSubmission["value"].int,
			
			let mileRunData = jsonData["mile_run"]?.dictionary,
			let milePersonalBest = mileRunData["personal_best"],
			let milePersonalBestCount = milePersonalBest["amount"].int,
			let milePersonalBestCreditWorth = milePersonalBest["value"].int,
			let mileVideo = mileRunData["video"],
			let mileVideoCount = mileVideo["amount"].int,
			let mileVideoCreditWorth = mileVideo["value"].int,
			let mileSubmission = mileRunData["submission"],
			let mileSubmissionCount = mileSubmission["amount"].int,
			let mileSubmissionCreditWorth = mileSubmission["value"].int,
            
            let challengeData = jsonData["challenge"]?.dictionary,
            let challengeJoin = challengeData["join_challenge"],
            let challengeJoinCount = challengeJoin["amount"].int,
            let challengeJoinCreditWorth = challengeJoin["value"].int,
            let challengeStreak = challengeData["join_challenge_streak"],
            let challengeStreakCount = challengeStreak["amount"].int,
            let challengeStreakCreditWorth = challengeStreak["value"].int,
        
            let loyaltyData = jsonData["loyalty"]?.dictionary,
            let loyaltyDailyVisit = loyaltyData["daily_visit"],
            let loyaltyDailyVisitCount = loyaltyDailyVisit["amount"].int,
            let loyaltyDailyVisitCreditWorth = loyaltyDailyVisit["value"].int
			else {
				throw MoyaError.jsonMapping(self)
		}
		
		let squatAchievement = Achievement(personalBestCount: squatPersonalBestCount, personalBestCreditWorth: squatPersonalBestCreditWorth, videoCount: squatVideoCount, videoCreditWorth: squatVideoCreditWorth, submissionCount: squatSubmissionCount, submissionCreditWorth: squatSubmissionCreditWorth)
		let benchPressAchievement = Achievement(personalBestCount: benchPressPersonalBestCount, personalBestCreditWorth: benchPressPersonalBestCreditWorth, videoCount: benchPressVideoCount, videoCreditWorth: benchPressVideoCreditWorth, submissionCount: benchPressSubmissionCount, submissionCreditWorth: benchPressSubmissionCreditWorth)
		let militaryPressAchievement = Achievement(personalBestCount: militaryPressPersonalBestCount, personalBestCreditWorth: militaryPressPersonalBestCreditWorth, videoCount: militaryPressVideoCount, videoCreditWorth: militaryPressVideoCreditWorth, submissionCount: militaryPressSubmissionCount, submissionCreditWorth: militaryPressSubmissionCreditWorth)
		let fortyYardDashAchievement = Achievement(personalBestCount: fortyYardDashPersonalBestCount, personalBestCreditWorth: fortyYardDashPersonalBestCreditWorth, videoCount: fortyYardDashVideoCount, videoCreditWorth: fortyYardDashVideoCreditWorth, submissionCount: fortyYardDashSubmissionCount, submissionCreditWorth: fortyYardDashSubmissionCreditWorth)
		let deadliftAchievement = Achievement(personalBestCount: deadliftPersonalBestCount, personalBestCreditWorth: deadliftPersonalBestCreditWorth, videoCount: deadliftVideoCount, videoCreditWorth: deadliftVideoCreditWorth, submissionCount: deadliftSubmissionCount, submissionCreditWorth: deadliftSubmissionCreditWorth)
		let mileRunAchievement = Achievement(personalBestCount: milePersonalBestCount, personalBestCreditWorth: milePersonalBestCreditWorth, videoCount: mileVideoCount, videoCreditWorth: mileVideoCreditWorth, submissionCount: mileSubmissionCount, submissionCreditWorth: mileSubmissionCreditWorth)
        let challengeAchievement = Achievement_Challenge(joinChallengeCount: challengeJoinCount, joinChallengeCreditWorth: challengeJoinCreditWorth, challengeStreakCount: challengeStreakCount, challgeneStreakCreditWorth: challengeStreakCreditWorth)
        let loyaltyAchievement = Achievement_Loyalty(dailyVisitCount: loyaltyDailyVisitCount, dailyVisitCreditWorth: loyaltyDailyVisitCreditWorth)
		
        return Achievements(mileRun: mileRunAchievement, fourtyYardDash: fortyYardDashAchievement, benchPress: benchPressAchievement, deadlift: deadliftAchievement, squat: squatAchievement, militaryPress: militaryPressAchievement, challenge: challengeAchievement, loyalty: loyaltyAchievement)
	}
}
