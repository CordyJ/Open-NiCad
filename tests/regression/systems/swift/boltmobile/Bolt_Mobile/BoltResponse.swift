//
//  BoltResponse.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation

class BoltResponse:Decodable {
    
    enum CodingKeys: String, CodingKey {
        case message
        case success
    }
    
    let message: String
    let success: Bool
    
    required init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        message = try values.decode(String.self, forKey: .message)
        let successInt = try values.decode(Int.self, forKey: .success)
        success = successInt == 1
    }
}
