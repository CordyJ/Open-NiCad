//
//  ProfileImage.swift
//  REPerformance
//
//  Created by Greg Brownell on 9/9/19.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


struct ProfileImage: Decodable {
    
    private enum CodingKeys: String, CodingKey {
        case image = "image"
    }
    
    var image: URL
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.image = try container.decode(URL.self, forKey: .image)
    }
}
