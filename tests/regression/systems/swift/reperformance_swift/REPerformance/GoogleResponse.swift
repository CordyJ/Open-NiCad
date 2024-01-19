//
//  GoogleResponse.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-06.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Moya_SwiftyJSONMapper
import SwiftyJSON

final class GoogleResponse: ALSwiftyJSONAble {
    
    let status: String
    let results: [JSON]
    let success:Bool
    let nextPageToken:String
    let attributions:[String]
    
    required init?(jsonData:JSON){
        self.status = jsonData["status"].stringValue
        self.results = jsonData["results"].arrayValue
        self.nextPageToken = jsonData["next_page_token"].stringValue
        self.attributions = jsonData["html_attributions"].arrayObject as? [String] ?? [String]()
        self.success = status == "OK"
    }
}
