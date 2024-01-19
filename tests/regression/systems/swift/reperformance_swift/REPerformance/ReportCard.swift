//
//  ReportCard.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-07-31.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


struct ReportCard: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case rank = "rank"
		case rankOutOf = "rank_out_of"
		case mileRunGrade = "mile_run"
		case fourtyYardDashGrade = "forty_yard_dash"
		case benchPressGrade = "bench_press"
		case deadliftGrade = "deadlift"
		case squatGrade = "squat"
		case militaryPressGrade = "military_press"
		case totalReps = "total_reps"
		case totalVolume = "total_volume"
	}
	
	
	var rank: Int?
	var rankOutOf: Int?
	var mileRunGrade: String?
	var fourtyYardDashGrade: String?
	var benchPressGrade: String?
	var deadliftGrade: String?
	var squatGrade: String?
	var militaryPressGrade: String?
	var totalReps: Int?
	var totalVolume: Int?
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.rank = try? container.decode(Int.self, forKey: .rank)
		self.rankOutOf = try? container.decode(Int.self, forKey: .rank)
		self.mileRunGrade = try? container.decode(String.self, forKey: .mileRunGrade)
		self.fourtyYardDashGrade = try? container.decode(String.self, forKey: .fourtyYardDashGrade)
		self.benchPressGrade = try? container.decode(String.self, forKey: .benchPressGrade)
		self.deadliftGrade = try? container.decode(String.self, forKey: .deadliftGrade)
		self.squatGrade = try? container.decode(String.self, forKey: .squatGrade)
		self.militaryPressGrade = try? container.decode(String.self, forKey: .militaryPressGrade)
		self.totalReps = try? container.decode(Int.self, forKey: .totalReps)
		self.totalVolume = try? container.decode(Int.self, forKey: .totalVolume)
	}
}
