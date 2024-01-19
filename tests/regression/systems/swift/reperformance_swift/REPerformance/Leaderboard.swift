//
//  Leaderboard.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-07-31.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


struct Leaderboard: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case gym = "gym"
		case topRanking = "top_ranking"
		case localRanking = "local_ranking"
		case total = "total"
	}
	
	
	var gym: Gym?
	var topRanking: [Athlete]
	var localRanking: [Athlete]
	var total: Int
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.gym = try? container.decode(Gym.self, forKey: .gym)
		self.topRanking = try container.decode([Athlete].self, forKey: .topRanking)
		self.localRanking = try container.decode([Athlete].self, forKey: .localRanking)
		self.total = try container.decode(Int.self, forKey: .total)
	}
}


extension Leaderboard {
	
	var userIsTopRanking: Bool {
		get {
			guard let currentUserIdentifier = UserDefaults.standard.userID, let currentUserIdentifierInt = Int(currentUserIdentifier) else {
				return false
			}
			
			return self.topRanking.map({ return $0.userIdentifier }).contains(currentUserIdentifierInt)
		}
	}
	
	var groupedRankings: [[Athlete]] {
		get {
			var groupedRankingsToReturn = [[Athlete]]()
			groupedRankingsToReturn.append(self.topRanking)
			if self.userIsTopRanking == false {							// Omit local rankings if user is in the top ranking.
				groupedRankingsToReturn.append(self.localRanking)
			}
			
			return groupedRankingsToReturn
		}
	}
	
	var isRankingEmpty: Bool {
		get {
			return (self.topRanking + self.localRanking).count == 0
		}
	}
}
