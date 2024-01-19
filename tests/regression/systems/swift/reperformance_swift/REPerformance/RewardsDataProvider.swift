//
//  RewardsDataProvider.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-07.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya
import SwiftyJSON

struct RewardServerFormat{
    let costProMembers:String
    let costNonMembers:String

    let itemImageURL:String?
    let logoURL:String?
    
    let couponCode:String

    let discountDescription:String
    let productDescription:String

    let canRedeem:Bool
    let rewardID:String
    
    let discount:Int
    let proDiscount:Int
}

class RewardsDataProvider {
    
    let retrieveProvider = MoyaProvider<RetrieveService>()
    let submitProvider = MoyaProvider<SubmitService>()
    
    func retreiveListOfRewards(completion: @escaping (Array<RewardServerFormat>?, String?)->()){
        guard let token = UserDefaults.standard.userToken else {
            completion(nil, L10n.userTokenMissingMessage)
            return
        }
        
        retrieveProvider.request(.getRewards(token: token)) { (result) in
            do{
                let response = try result.dematerialize()
                let rewardData = try response.mapRewards()
                completion(rewardData, nil)
            } catch {
                completion(nil, error.localizedDescription)
            }
        }
    }
    
    func purchaseReward(rewardID:String, proUser:Bool, completion: @escaping (RewardServerFormat?, String?)->()){
        guard let token = UserDefaults.standard.userToken else {
            completion(nil, L10n.userTokenMissingMessage)
            return
        }
        
        submitProvider.request(.purchaseReward(token: token, rewardID: rewardID, proUser: proUser)) { (result) in
            do{
                let response = try result.dematerialize()
                let rewardData = try response.mapSingleReward()
                completion(rewardData, nil)
            } catch {
                completion(nil, error.localizedDescription)
            }
        }
    }
    
    func redeemReward(rewardID:String, completion: @escaping (RewardServerFormat?, String?)->()){
        guard let token = UserDefaults.standard.userToken else {
            completion(nil, L10n.userTokenMissingMessage)
            return
        }
        
        submitProvider.request(.redeemReward(token: token, rewardID: rewardID)) { (result) in
            do{
                let response = try result.dematerialize()
                let rewardData = try response.mapSingleReward()
                completion(rewardData, nil)
            } catch {
                completion(nil, error.localizedDescription)
            }
        }
    }

}

extension Moya.Response{
    
    func mapRewards() throws -> Array<RewardServerFormat>{
        
        let responseObject = try self.map(to: REPerformanceResponse.self)
        
        guard responseObject.success else {
            throw REPerformanceError.requestFailed(responseObject.message)
        }
        let jsonData = responseObject.data
        
        guard let rewardsData = jsonData["rewards"] else {
            throw MoyaError.jsonMapping(self)
        }
        var rewards:Array<RewardServerFormat> = []
        for (_,rewardJson):(String, JSON) in rewardsData {
            let costProMembers = String(format: "$%.2f",rewardJson["cost_pro_members"].floatValue)
            let costNonMembers = String(format: "$%.2f",rewardJson["cost_non_members"].floatValue)
            let itemImageURL = rewardJson["image_url"].stringValue.addingPercentEncoding(withAllowedCharacters: CharacterSet.urlQueryAllowed)
            let couponCode = rewardJson["coupon_code"].stringValue
            let logoURL = rewardJson["logo_url"].stringValue.addingPercentEncoding(withAllowedCharacters: CharacterSet.urlQueryAllowed)
            let discountDescription = rewardJson["discount_description"].stringValue
            let productDescription = rewardJson["product_description"].stringValue
            let canRedeem = rewardJson["can_redeem"].boolValue
            let rewardID = rewardJson["reward_id"].stringValue
            let discount = rewardJson["discount"].intValue
            let proDiscount = rewardJson["pro_discount"].intValue
            
            let reward = RewardServerFormat(costProMembers: costProMembers, costNonMembers: costNonMembers, itemImageURL: itemImageURL, logoURL: logoURL, couponCode: couponCode, discountDescription: discountDescription, productDescription: productDescription, canRedeem: canRedeem, rewardID: rewardID, discount: discount, proDiscount: proDiscount)
            rewards.append(reward)
        }
        
        return rewards
    }
    
    func mapSingleReward() throws -> RewardServerFormat{
        let responseObject = try self.map(to: REPerformanceResponse.self)
        
        guard responseObject.success else {
            throw REPerformanceError.requestFailed(responseObject.message)
        }
        let jsonData = responseObject.data
        
        guard let rewardData = jsonData["reward"] else {
            throw MoyaError.jsonMapping(self)
        }
        
        let costProMembers = String(format: "$%.2f",rewardData["cost_pro_members"].floatValue)
        let costNonMembers = String(format: "$%.2f",rewardData["cost_non_members"].floatValue)
        let itemImageURL = rewardData["image_url"].stringValue
        let couponCode = rewardData["coupon_code"].stringValue
        let logoURL = rewardData["logo_url"].stringValue
        let discountDescription = rewardData["discount_description"].stringValue
        let productDescription = rewardData["product_description"].stringValue
        let canRedeem = rewardData["can_redeem"].boolValue
        let rewardID = rewardData["reward_id"].stringValue
        let discount = rewardData["discount"].intValue
        let proDiscount = rewardData["pro_discount"].intValue
        
        let reward = RewardServerFormat(costProMembers: costProMembers, costNonMembers: costNonMembers, itemImageURL: itemImageURL, logoURL: logoURL, couponCode: couponCode, discountDescription: discountDescription, productDescription: productDescription, canRedeem: canRedeem, rewardID: rewardID, discount: discount, proDiscount: proDiscount)
        
        return reward
    }
}
