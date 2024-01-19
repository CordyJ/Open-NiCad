//
//  ReferralsDataProvider.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation
import Moya
import enum Result.Result
import Alamofire

public typealias ReferralsCompletion = (_ result: Result<String, BoltError>) -> Void
public typealias VerificationCompletion = (_ result: Result<Bool, BoltError>) -> Void

struct Balance: Codable {

    enum CodingKeys: String, CodingKey {
        case balance
    }

    let balance: String

    init(from decoder:Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        let balanceCents = try values.decode(Int.self, forKey: .balance)
        let balanceDollars:Double = Double(balanceCents)/100.00
        balance = String(format: "%.2f", balanceDollars)
    }
}

struct BalanceResponse: Codable {
    let data: Balance
}

struct Refer:Codable {
    enum CodingKeys: String, CodingKey {
        case referralCode = "referral_code"
    }
    
    let referralCode: String
}

struct ReferResponse: Decodable {
    let data:Refer
}

struct RedeemCode: Codable {
    enum CodingKeys: String, CodingKey {
        case redeemCode = "code"
    }
    
    let redeemCode: String
}

struct RedeemResponse:Decodable {
    let data: RedeemCode
}

struct LoginUpdate: Codable {
    enum CodingKeys: String, CodingKey {
        case firstName = "first_name"
        case lastName = "last_name"
        case email
        case phone
        case token
    }
    
    let firstName:String
    let lastName:String
    let email:String
    let phone:String
    let token:String
}

struct LoginUpdateResponse:Decodable {
    let data: LoginUpdate
}

class ReferralsDataProvider {
    
    let provider = MoyaProvider<ReferralService>()
    let reachabilityManager = NetworkReachabilityManager()
    
    func getBalance(phoneNumber:String, completion: @escaping ReferralsCompletion){
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
            return
        }
        guard let userToken = UserDefaults.userToken, userToken != "" else {
            completion(.failure(.missingToken))
            return
        }
        provider.request(.getBalance(userToken:userToken, phoneNumber: phoneNumber)) { (result) in
            switch result {
            case let .success(moyaResponse):
                do {
                    if moyaResponse.isValidUser() {
                        let response = try moyaResponse.boltData()
                        let balanceResponse = try response.mapBalance()
                        completion(.success(balanceResponse.data.balance))
                    } else {
                        completion(.failure(.invalidUser))
                    }
                } catch {
                    completion(.failure(.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(.moyaError(error.localizedDescription)))
            }
        }
    }
    
    func refer(userFirstName:String, userLastName:String, userEmail:String, userPhone:String, referFirstName:String, referLastName:String, referEmail:String?, referPhone:String, completion: @escaping ReferralsCompletion){
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
            return
        }
        guard let userToken = UserDefaults.userToken, userToken != "" else {
            completion(.failure(.missingToken))
            return
        }
        let userName = userFirstName + " " + userLastName
        let referName = referFirstName + " " + referLastName
        provider.request(.refer(userToken:userToken, userName: userName, userPhone: userPhone, userEmail: userEmail, referName: referName, referPhone: referPhone, referEmail: referEmail)) { (result) in
            switch result {
            case let .success(moyaResponse):
                do {
                    if moyaResponse.isValidUser() {
                        let response = try moyaResponse.boltData()
                        let referResponse = try response.mapRefer()
                        completion(.success(referResponse.data.referralCode))
                    } else {
                        completion(.failure(.invalidUser))
                    }
                } catch {
                    completion(.failure(.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(.dataMapping(error.localizedDescription)))
            }
        }
    }
    
    func redeem(userPhoneNumber:String, userEmail:String, completion: @escaping ReferralsCompletion) {
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
            return
        }
        guard let userToken = UserDefaults.userToken, userToken != "" else {
            completion(.failure(.missingToken))
            return
        }
        provider.request(.redeem(userToken:userToken, phoneNumber: userPhoneNumber, email: userEmail)) { (result) in
            switch result {
            case let .success(moyaResponse):
                do {
                    if moyaResponse.isValidUser() {
                        let response = try moyaResponse.boltData()
                        let redeemResponse = try response.mapRedeem()
                        completion(.success(redeemResponse.data.redeemCode))
                    } else {
                        completion(.failure(.invalidUser))
                    }
                } catch {
                    completion(.failure(.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(.dataMapping(error.localizedDescription)))
            }
        }
    }
    
    func login(userFirstName:String, userLastName:String, userEmail:String, userPhone:String, completion: @escaping ReferralsCompletion) {
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
            return
        }
        provider.request(.login(userFirstName: userFirstName, userLastName: userLastName, userEmail: userEmail, userPhone: userPhone)) { (result) in
            switch result {
            case let .success(moyaResponse):
                do {
                    let response = try moyaResponse.boltData()
                    let loginResponse = try response.mapLoginUpdate()
                    completion(.success(loginResponse.data.token))
                } catch {
                    completion(.failure(.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(.dataMapping(error.localizedDescription)))
            }
        }
    }
    
    func updateUser(userFirstName:String, userLastName:String, userEmail:String, userPhone:String, completion: @escaping ReferralsCompletion) {
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
            return
        }
        guard let userToken = UserDefaults.userToken, userToken != "" else {
            completion(.failure(.missingToken))
            return
        }
        provider.request(.updateUser(userToken: userToken, userFirstName: userFirstName, userLastName: userLastName, userEmail: userEmail, userPhone: userPhone)) { (result) in
            switch result {
            case let .success(moyaResponse):
                do {
                    if moyaResponse.isValidUser() {
                        let response = try moyaResponse.boltData()
                        let updateResponse = try response.mapLoginUpdate()
                        completion(.success(updateResponse.data.token))
                    } else {
                        completion(.failure(.invalidUser))
                    }
                } catch {
                    completion(.failure(.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(.dataMapping(error.localizedDescription)))
            }
        }
    }
    
    func verifyPhoneNumber(code:Int, completion: @escaping VerificationCompletion){
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
        }
        guard let userToken = UserDefaults.userToken, userToken != "" else {
            completion(.failure(.missingToken))
            return
        }
        provider.request(.verifyPhoneNumber(userToken: userToken, code: code)) { (result) in
            switch result {
            case let .success(moyaResponse):
                do {
                    if moyaResponse.isValidUser() {
                        let phoneVerified = try moyaResponse.phoneVerificationSuccess()
                        completion(.success(phoneVerified))
                    } else {
                        completion(.failure(.invalidUser))
                    }
                } catch {
                    completion(.failure(.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(.dataMapping(error.localizedDescription)))
            }
        }
    }
    
    func resendCode(completion: @escaping VerificationCompletion){
        if reachabilityManager?.networkReachabilityStatus == .notReachable {
            completion(.failure(.internetNotReachable))
        }
        guard let userToken = UserDefaults.userToken, userToken != "" else {
            completion(.failure(.missingToken))
            return
        }
        provider.request(.resendCode(userToken: userToken)) { (result) in
            switch result{
            case let .success(moyaResponse):
                do {
                    if moyaResponse.isValidUser() {
                        let codeSent = try moyaResponse.phoneVerificationSuccess()
                        completion(.success(codeSent))
                    } else {
                        completion(.failure(.invalidUser))
                    }
                } catch {
                    completion(.failure(.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(.dataMapping(error.localizedDescription)))
            }
        }
    }
}

fileprivate extension Moya.Response {
    
    func isValidUser() -> Bool{
        if self.statusCode == 401 {
            return false
        } else {
            return true
        }
    }
    
    func mapBalance() throws -> BalanceResponse {
        let decoder = JSONDecoder()
        do {
            let balanceData = try decoder.decode(BalanceResponse.self, from: self.data)
            return balanceData
        } catch {
            print(error)
            throw BoltError.dataMapping(L10n.balanceDataMappingFailed)
        }
    }
    
    func mapRefer() throws -> ReferResponse {
        let decoder = JSONDecoder()
        do {
            let referData = try decoder.decode(ReferResponse.self, from: self.data)
            return referData
        } catch {
            print(error)
            throw BoltError.dataMapping(L10n.referralDataMappingFailed)
        }
    }
    
    func mapRedeem() throws -> RedeemResponse {
        let decoder = JSONDecoder()
        do {
            let redeemData = try decoder.decode(RedeemResponse.self, from: self.data)
            return redeemData
        } catch {
            print(error)
            throw BoltError.dataMapping(L10n.redeemDataMappingFailed)
        }
    }
    
    func mapLoginUpdate() throws -> LoginUpdateResponse {
        let decoder = JSONDecoder()
        do {
            let loginUpdateData = try decoder.decode(LoginUpdateResponse.self, from: self.data)
            return loginUpdateData
        } catch {
            print(error)
            throw BoltError.dataMapping(L10n.loginUpdateDataMappingFailed)
        }
    }
}


