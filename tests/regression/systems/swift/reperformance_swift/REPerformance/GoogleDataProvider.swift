//
//  GoogleDataProvider.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-10.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya
import SwiftyJSON
import MapKit

struct REPPlace {
    let location:CLLocationCoordinate2D
    let name:String
    let placeID:String
    let vicinity:String
}

class GoogleDataProvider {
    
    let provider = MoyaProvider<PlaceSearchService>()
    
    func searchNearbyPlaces(location:CLLocationCoordinate2D, queryString:String, completion: @escaping ([REPPlace]?, String?, String?)->()){
        
        provider.request(.nearbySearch(location: location, queryString: queryString)) { (result) in
            do {
                let response = try result.dematerialize()
                let placesResponse = try response.mapPlacesResponse()
                completion(placesResponse.places, placesResponse.pageToken, nil)
            } catch {
                completion(nil, nil, error.localizedDescription)
            }
        }
    }
    
    func findNearbyGyms(location:CLLocationCoordinate2D, pageToken:String?, completion: @escaping ([REPPlace]?, String?, [String]?, String?)->()){
        provider.request(.emptySearch(location: location, pageToken: pageToken)) { (result) in
            do {
                let response = try result.dematerialize()
                let placesResponse = try response.mapPlacesResponse()
                completion(placesResponse.places, placesResponse.pageToken, placesResponse.htmlAttributions, nil)
            } catch {
                completion(nil, nil, nil, error.localizedDescription)
            }
        }
    }
}

extension Moya.Response {
    
    func mapPlacesResponse() throws -> (places:[REPPlace], pageToken:String, htmlAttributions:[String]) {
        let responseObject = try self.map(to: GoogleResponse.self)
        
        guard responseObject.success else {
            throw GoogleError.requestFailed(responseObject.status)
        }
        
        let jsonData = responseObject.results
        var places:[REPPlace] = []
        for (placeJson):(JSON) in jsonData {
            
            guard let geometryJson = placeJson["geometry"].dictionary, let locationJson = geometryJson["location"]?.dictionary, let lat = locationJson["lat"]?.doubleValue, let lng = locationJson["lng"]?.doubleValue else {
                throw MoyaError.jsonMapping(self)
            }
            let currentName = placeJson["name"].stringValue
            let currentPlaceID = placeJson["place_id"].stringValue
            let vicinity = placeJson["vicinity"].stringValue

            let currentCoordinate = CLLocationCoordinate2D(latitude: lat, longitude: lng)
            let currentPlace = REPPlace(location: currentCoordinate, name: currentName, placeID: currentPlaceID, vicinity: vicinity)
            
            places.append(currentPlace)

        }
        
        let attributionJSON = responseObject.attributions
        
        return (places, responseObject.nextPageToken, attributionJSON)
    }
}
