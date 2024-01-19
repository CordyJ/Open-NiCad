//
//  Challenge.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-20.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


enum ChallengeRule: String, Decodable {
	case leader = "by_leader"
	case date = "by_date"
}


enum ChallengeType: String, Decodable {
	case personal = "personal"
	case gym = "gym"
}


struct Challenge: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case uniqueIdentifier = "id"
		case name = "name"
		case description = "description"
		case hasJoined = "has_joined"
		case subtitle = "subtitle"
		case reps = "reps"
		case rule = "rule"
		case imageURL = "image_url"
		case gymOne = "gym_one"
		case gymTwo = "gym_two"
        case gyms = "gyms"
		case complete = "complete"
		case joinedTotal = "joined_no"
		case type = "type"
		case exercise = "exercise"
		case format = "format"
		case startDate = "start_date"
		case endDate = "end_date"
	}
	
	
	let uniqueIdentifier: Int
	let name: String
	let description: String
	var hasJoined: Bool
	let subtitle: String?
	let reps: Int?
	let rule: ChallengeRule
	let imageURL: URL?
	private let gymOne: Gym?
	private let gymTwo: Gym?
	let gyms: [Gym]?
	let complete: Bool
	let joinedTotal: Int
	let type: ChallengeType
	let exercise: ExerciseCategory?			// squat , etc...
	let format: String
	private let startDateString: String?
	private let endDateString: String?
	
	var startDate: Date? {
		get {
			guard let startDateString = self.startDateString else {
				return nil
			}
			
			let dateFormatter = DateFormatter.serverDateFormatter()
			
			return dateFormatter.date(from: startDateString)
		}
	}
	
	var endDate: Date? {
		get {
			guard let endDateString = self.endDateString else {
				return nil
			}
			
			let dateFormatter = DateFormatter.serverDateFormatter()
			
			return dateFormatter.date(from: endDateString)
		}
	}
	
	var hasExpired: Bool? {
		get {
			guard let endDate = self.endDate else {
				return nil
			}
			
			return (endDate.compare(Date()) == .orderedAscending)
		}
	}
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.uniqueIdentifier = try container.decode(Int.self, forKey: .uniqueIdentifier)
		self.name = try container.decode(String.self, forKey: .name)
		self.description = try container.decode(String.self, forKey: .description)
		self.hasJoined = try container.decode(Bool.self, forKey: .hasJoined)
		self.subtitle = try? container.decode(String.self, forKey: .subtitle)
		self.reps = try? container.decode(Int.self, forKey: .reps)
		self.rule = try container.decode(ChallengeRule.self, forKey: .rule)
		self.imageURL = try? container.decode(URL.self, forKey: .imageURL)
		self.gymOne = try? container.decode(Gym.self, forKey: .gymOne)
		self.gymTwo = try? container.decode(Gym.self, forKey: .gymTwo)
		self.complete = try container.decode(Bool.self, forKey: .complete)
        self.gyms = try? container.decode([Gym].self, forKey: .gyms)
		self.joinedTotal = try container.decode(Int.self, forKey: .joinedTotal)
		self.startDateString = try? container.decode(String.self, forKey: .startDate)
		self.endDateString = try? container.decode(String.self, forKey: .endDate)
		self.type = try container.decode(ChallengeType.self, forKey: .type)
		self.exercise = try container.decode(ExerciseCategory.self, forKey: .exercise)
		self.format = try container.decode(String.self, forKey: .format)
		
	}
}
