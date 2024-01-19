//
//  GoogleAPIs.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-06.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya
import MapKit

fileprivate let BaseURL = URL(string: "https://maps.googleapis.com/maps/api/place")!

enum PlaceSearchService {
    //API Key - key
    //rankby - prominence
    //keyword - search term
    //type - gym
    case nearbySearch(location:CLLocationCoordinate2D, queryString:String)
    case emptySearch(location:CLLocationCoordinate2D, pageToken:String?)
}

extension PlaceSearchService:TargetType {
    var baseURL: URL { return BaseURL }
    var path: String {
        switch self {
        case .nearbySearch, .emptySearch:
            return "/nearbysearch/json"
        }
    }
    
    var method: Moya.Method {
        switch self {
        case .nearbySearch, .emptySearch:
            return .get
        }
    }
    
    var sampleData: Data {
        switch self {
        case .nearbySearch:
            return "{\"key\": \"testKey\", \"location\": \"-33.8670522,151.1957362\", \"rankby\": \"distance\", \"keyword\":\"gym string\", \"type\":\"gym\"}".data(using: String.Encoding.utf8)!
        case .emptySearch:
            return "{\"key\": \"testKey\", \"location\": \"-33.8670522,151.1957362\", \"radius\": 50000, \"type\":\"gym\"}".data(using: String.Encoding.utf8)!
        }
    }
    
    var task:Task {
        switch self {
        case .nearbySearch(let location, let queryString):
            let locationString = "\(location.latitude),\(location.longitude)"
            //Rank results by distance from search
            return .requestParameters(parameters: ["key": Constants.Google.APIKey, "location": locationString, "rankby":"distance", "keyword":queryString, "type":"gym"], encoding: URLEncoding.default)
        case .emptySearch(let location, let pageToken):
            let locationString = "\(location.latitude),\(location.longitude)"
            //Search all gyms within 50km
            if let pageToken = pageToken {
                return .requestParameters(parameters: ["key": Constants.Google.APIKey, "location": locationString, "radius":Constants.GymLeaderboard.NearbySearchRadius, "type":"gym", "pagetoken":pageToken], encoding: URLEncoding.default)
            } else {
                return .requestParameters(parameters: ["key": Constants.Google.APIKey, "location": locationString, "radius":Constants.GymLeaderboard.NearbySearchRadius, "type":"gym"], encoding: URLEncoding.default)
            }
        }
    }
    
    var headers: [String:String]? {
        switch self {
        case .nearbySearch, .emptySearch:
            return nil
        }
    }
}


//MARK: - Response Handlers

extension Moya.Response {
    
    func mapGoogleSuccess() throws -> Bool {
        let responseObject = try self.map(to: GoogleResponse.self)
        
        if responseObject.status == "OK" || responseObject.status == "ZERO_RESULTS" {
            return true
        } else {
            throw GoogleError.requestFailed(responseObject.status)
        }
    }
}
