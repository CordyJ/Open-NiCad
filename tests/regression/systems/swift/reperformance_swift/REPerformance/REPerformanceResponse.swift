//
//  REPerformanceResponse.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Moya_SwiftyJSONMapper
import SwiftyJSON


class REPerformanceBaseResponse<T: Decodable>: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case success = "success"
		case message = "message"
		case data = "data"
	}
	
	let success: Int
	let message: String
	let data: T
	
	
	required init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.success = try container.decode(Int.self, forKey: .success)
		self.message = try container.decode(String.self, forKey: .message)
		self.data = try container.decode(T.self, forKey: .data)
	}
}


/*
Should be removed in favour of 'REPerformanceBaseResponse' at some point.
*/
final class REPerformanceResponse: ALSwiftyJSONAble {

    let data: [String: JSON]
    let success: Bool
    let message: String
    let arrayData: [JSON]

    required init?(jsonData:JSON){
        self.data = jsonData["data"].dictionaryValue
        self.success = jsonData["success"].boolValue
        self.message = jsonData["message"].stringValue
        self.arrayData = jsonData["data"].arrayValue
    }
}
