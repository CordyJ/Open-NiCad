//
//  CouponsDataProvider.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-25.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation
import Moya
import SWXMLHash
import KeychainAccess
import enum Result.Result
import Alamofire

public typealias CouponsCompletion = (_ result: Result<Coupons, BoltError>) -> Void

struct Coupon {
    let couponImageURLString:String
    var couponImage:UIImage?
    let couponID:String?
}

public struct Coupons {
    var allCoupons:Array<Coupon>
}

class CouponsDataProvider {
    
    let provider = MoyaProvider<CouponService>()
    let reachabilityManager = NetworkReachabilityManager()
    
    func getCoupons(completion: @escaping CouponsCompletion) {
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
            return
        }
        provider.request(.getCoupons) { (result) in
            switch result {
            case let .success(moyaResponse):
                let xml = SWXMLHash.parse(moyaResponse.data)
                let keychain = Keychain(service: Constants.Keychain.Service)
                var coupons:Array<Coupon> = []
                for element in xml["Coupons"]["Coupon"].all {
                    if let imageURLString:String = element["Image"].element?.text {
                        var id = element["ID"].element?.text
                        if id == "" {
                            id = nil
                        }
                        let coupon = Coupon(couponImageURLString: imageURLString, couponImage: nil, couponID: id)
                        if let couponID = coupon.couponID, keychain.isCouponUsed(id: couponID) {
                            //Do nothing, this coupon is already used
                        } else {
                            coupons.append(coupon)
                        }
                    }
                }
                completion(.success(Coupons(allCoupons: coupons)))
            case let .failure(error):
                completion(.failure(BoltError.moyaError(error.localizedDescription)))
            }
        }
    }
}
