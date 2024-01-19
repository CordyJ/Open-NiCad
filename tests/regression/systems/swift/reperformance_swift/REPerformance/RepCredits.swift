//
//  RepCredits.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-26.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


struct RepCredits: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case totalCredits = "credits"
		case dollarValue = "dollars"
	}
	
	
	let totalCredits: Int
	let dollarValue: Double
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.totalCredits = try container.decode(Int.self, forKey: .totalCredits)
		self.dollarValue = try container.decode(Double.self, forKey: .dollarValue)
	}
}
