//
//  REPAnalytics.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-09-26.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Firebase
import FirebaseAnalytics


struct ScreenName {
	
	struct HomePage {
		static let Test = "Home Page - Tests"
		static let ReportCard = "Home Page - Report Card"
		static let Rewards = "Home Page - Rewards"
		static let OurValue = "Home Page - Our Value"
		static let Profile = "Home Page - Profile"
	}
	
	struct TestsMileRun {
		static let Description = "Tests - Mile Run Description"
		static let Setup = "Tests - Mile Run Setup"
		static let Input = "Tests - Mile Run Input"
		static let Score = "Tests - Mile Run Score"
	}
	
	struct TestsFortyYardDash {
		static let Description = "Tests - 40 Yard Dash Description"
		static let Setup = "Tests - 40 Yard Dash Setup"
		static let Input = "Tests - 40 Yard Dash Input"
		static let Score = "Tests - 40 Yard Dash Score"
	}
	
	struct TestsBenchPress {
		static let Description = "Tests - Bench Press Description"
		static let Setup = "Tests - Bench Press Setup"
		static let Input = "Tests - Bench Press Input"
		static let Score = "Tests - Bench Press Score"
	}
	
	struct TestsDeadlift {
		static let Description = "Tests - Deadlift Description"
		static let Setup = "Tests - Deadlift Setup"
		static let Input = "Tests - Deadlift Input"
		static let Score = "Tests - Deadlift Score"
	}
	
	struct TestsSquat {
		static let Description = "Tests - Squat Description"
		static let Setup = "Tests - Squat Setup"
		static let Input = "Tests - Squat Input"
		static let Score = "Tests - Squat Score"
	}
	
	struct TestsMilitaryPress {
		static let Description = "Tests - Military Press Description"
		static let Setup = "Tests - Military Press Setup"
		static let Input = "Tests - Military Press Input"
		static let Score = "Tests - Military Press Score"
	}
	
	static let MyScores = "My Scores"
	
	struct LeaderBoard {
		static let Global = "Leaderboard - Global"
		static let MileRun = "Leaderboard - Mile Run"
		static let FortyYardDash = "Leaderboard - 40 Yard Dash"
		static let BenchPress = "Leaderboard - Bench Press"
		static let Deadlift = "Leaderboard - Deadlift"
		static let Squat = "Leaderboard - Squat"
		static let MilitaryPress = "Leaderboard - Military Press"
	}
	
	enum Challenges {
		static func Leaderboard(_ name: String) -> String {
			return "Challenge - \(name) - Leaderboard"
		}
		
		static func Gyms(_ name: String) -> String {
			return "Challenge - \(name) - Gyms"
		}
		
		static func Details(_ name: String) -> String {
			return "Challenge - \(name) - Details"
		}
	}
	
	static let UpgradeToPro = "Upgrade To Pro"
	static let ViewRewards = "View Reward"
	static let RedeemReward = "Redeem Reward"
	
	static let OurValueEndorsements = "Our Value - Endorsements"
	
	struct Profile {
		static let Default = "Profile"
		static let BasicInfo = "Profile - Basic Info"
		static let Nutrition = "Profile - Nutrition"
		static let Lifestyle = "Profile - Lifestyle"
		static let Exercise = "Profile - Exercise"
	}
	
	static let Achievements = "Achievements"
	static let Login = "Login"
	static let CreateAccount = "Create Account"
}


struct EventAnalytics {
	
	enum Challenges {
		static func Join(_ challenge: Challenge) -> String {
			return challenge.hasJoined ? "Join" : "Leave"
		}
		
		static func ChallengeType(_ challenge: Challenge) -> String {
			switch challenge.type {
			case .gym:
				return "Gym Challenge"
			case .personal:
				return "Personal Challenge"
			}
		}
	}
}


class REPAnalytics {
	
	class func trackScreenWithName(screenName: String, className: String) {
		Analytics.setScreenName(screenName, screenClass: className)
	}
	
	class func trackEvent(name: String, parameters: [String : Any]? = nil) {
		Analytics.logEvent(name, parameters: parameters)
	}
}

