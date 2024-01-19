//
//  LocationsDataProvider.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-18.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import SwiftyJSON

struct Locations {
    let countries:Array<Country>
    
    init(countries:Array<Country>) {
        self.countries = countries
    }
}

struct Country{
    let name:String
    let id:String
    let provinces:Array<Province>
    
    init(name:String, id:String, provinces:Array<Province>){
        self.name = name
        self.id = id
        self.provinces = provinces
    }
}

struct Province{
    let name:String
    let id:String
    
    init(name:String, id:String){
        self.name = name
        self.id = id
    }
}

class LocationsDataProvider: NSObject {
    
    //MARK: Locations
    class func loadLoactionsFromFile() -> Locations?{
        guard let path = Bundle.main.path(forResource: "locations", ofType: "json") else {
            return nil
        }
        var json: JSON?
        do {
            let data = try Data(contentsOf: URL(fileURLWithPath: path), options: .alwaysMapped)
            json = try JSON(data: data)
            if json == JSON.null {
                //Could not get json from file, make sure that file contains valid json
                return nil
            }
        } catch let error {
            print(error.localizedDescription)
            return nil
        }
        guard let unwrappedJson:JSON = json else {
            return nil
        }
        var countries:Array<Country> = []
        for (_,countriesJson):(String, JSON) in unwrappedJson {
            let countryName = countriesJson["name"].stringValue
            let countryID = countriesJson["code"].stringValue
            let regions = countriesJson["regions"]
            var provinces:Array<Province> = []
            for (_, provincesJson):(String, JSON) in regions{
                let provinceName = provincesJson["name"].stringValue
                let provinceID = provincesJson["code"].stringValue
                let province = Province(name: provinceName, id: provinceID)
                provinces.append(province)
            }
            let country = Country(name: countryName, id: countryID, provinces: provinces)
            countries.append(country)
        }
        
        return Locations(countries: countries)
    }
}
