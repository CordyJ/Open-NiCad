//
//  Athlete.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-07-31.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


struct Athlete: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case userIdentifier = "user_id"
		case facebookIdentifier = "facebook_id"
		case name = "name"
		case age = "age"
		case gender = "gender"
		case weight = "weight"
		case rank = "rank"
		case lifestyleCategory = "lifestyle_category"
		case score = "score"
		case isPublic = "public"
		case isVerified = "verified"
        case imageURL = "image"
	}
	
	var userIdentifier: Int
	var facebookIdentifier: String?
	var name: String
	var age: Int?
	var gender: String?
	var weight: Int?
	var rank: Int?
	var lifestyleCategory: String?
	var score: Int?
	var isPublic: Bool?
	var isVerified: Bool?
    var imageURL: URL?
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.userIdentifier = try container.decode(Int.self, forKey: .userIdentifier)
		self.facebookIdentifier = try? container.decode(String.self, forKey: .facebookIdentifier)
		self.name = try container.decode(String.self, forKey: .name)
		self.age = try? container.decode(Int.self, forKey: .age)
		self.gender = try? container.decode(String.self, forKey: .gender)
		self.weight = try? container.decode(Int.self, forKey: .weight)
		self.rank = try? container.decode(Int.self, forKey: .rank)
		self.lifestyleCategory = try? container.decode(String.self, forKey: .lifestyleCategory)
		self.score = try? container.decode(Int.self, forKey: .score)
		self.isPublic = try? container.decode(Bool.self, forKey: .isPublic)
		self.isVerified = try? container.decode(Bool.self, forKey: .isVerified)
        self.imageURL = try? container.decode(URL.self, forKey: .imageURL)
	}
}
