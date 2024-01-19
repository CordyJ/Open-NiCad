//
//  Gym.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-07-31.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


struct Gym: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case name = "name"
		case placeIdentifier = "place_id"
		case totalReps = "total_reps"
        case id = "id"
	}
	
	
	var name: String
	var placeIdentifier: String
	var totalReps: Int?
    var id: Int
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.name = try container.decode(String.self, forKey: .name)
		self.placeIdentifier = try container.decode(String.self, forKey: .placeIdentifier)
		self.totalReps = try? container.decode(Int.self, forKey: .totalReps)
        self.id = try container.decode(Int.self, forKey: .id)
	}
}
