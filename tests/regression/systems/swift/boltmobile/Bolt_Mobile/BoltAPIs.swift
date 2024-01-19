//
//  BoltAPIs.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-17.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Moya

#if USE_PRODUCTION
    fileprivate let BaseURL = URL(string: "https://bolt-live.appspot.com/api/v1")!
#else
    fileprivate let BaseURL = URL(string: "https://bolt-beta.appspot.com/api/v1")!
#endif

enum ReferralService {
    case getBalance(userToken:String, phoneNumber:String)
    case refer(userToken:String, userName:String, userPhone:String, userEmail:String, referName:String, referPhone:String, referEmail:String?)
    case redeem(userToken:String, phoneNumber:String, email:String)
    case login(userFirstName:String, userLastName:String, userEmail:String, userPhone:String)
    case updateUser(userToken:String, userFirstName:String, userLastName:String, userEmail:String, userPhone:String)
    case verifyPhoneNumber(userToken:String, code:Int)
    case resendCode(userToken:String)
}

enum PushNotificationService {
    case registerPushNotifications(deviceToken:String, deviceType:Int)
}

enum CouponService {
    case getCoupons
}

extension ReferralService:TargetType {
    var baseURL: URL {
        return BaseURL
    }
    
    var path: String {
        switch self {
        case .getBalance:
            return "/balance/"
        case .refer:
            return "/refer/"
        case .redeem:
            return "/redeem/"
        case .login:
            return "/login/"
        case .updateUser:
            return "/update_user/"
        case .verifyPhoneNumber:
            return "/verify/"
        case .resendCode:
            return "/resend_code/"
        }
    }
    
    var method: Moya.Method {
        switch self {
        case .getBalance, .refer, .redeem, .login, .updateUser, .verifyPhoneNumber, .resendCode:
            return .get
        }
    }
    
    var sampleData: Data {
        switch self {
        case .getBalance:
            return "{\"token\":\"15--5fa624b2c8ed8190ee337fdf64676e5ce1b8d543\", \"phone\": \"1234567890\"}".data(using: String.Encoding.utf8)!
        case .refer:
            return "{\"token\":\"15--5fa624b2c8ed8190ee337fdf64676e5ce1b8d543\", \"referrer_name\":\"Referrer Name\", \"referrer_phone\":\"1234567890\", \"referrer_email\":\"test@test.com\", \"referred_name\":\"Referred Name\", \"referred_phone\":\"1112223333\", \"referred_email\":\"test2@test.com\"}".data(using: String.Encoding.utf8)!
        case .redeem:
            return "{\"token\":\"15--5fa624b2c8ed8190ee337fdf64676e5ce1b8d543\", \"phone\":\"1234567890\", \"email\":\"test@test.com\"}".data(using: String.Encoding.utf8)!
        case .login:
            return "{\"first_name\":\"First Name\", \"last_name\":\"Last Name\", \"email\":\"test@test.com\", \"phone\":\"1112223333\"}".data(using: String.Encoding.utf8)!
        case .updateUser:
            return "{\"token\":\"15--5fa624b2c8ed8190ee337fdf64676e5ce1b8d543\", \"first_name\":\"First Name\", \"last_name\":\"Last Name\", \"email\":\"test@test.com\", \"phone\":\"1112223333\"}".data(using: String.Encoding.utf8)!
        case .verifyPhoneNumber:
            return "{\"token\":\"15--5fa624b2c8ed8190ee337fdf64676e5ce1b8d543\", \"code\":\"1234\"}".data(using: String.Encoding.utf8)!
        case .resendCode:
            return "{\"token\":\"15--5fa624b2c8ed8190ee337fdf64676e5ce1b8d543\"}".data(using: String.Encoding.utf8)!
        }
    }
    
    var task: Task {
        switch self {
        case .getBalance(let userToken, let phoneNumber):
            return .requestParameters(parameters: ["token":userToken, "phone":phoneNumber], encoding: URLEncoding.default)
        case .refer(let userToken, let userName, let userPhone, let userEmail, let referName, let referPhone, let referEmail):
            var parameters: [String: String] = ["token":userToken, "referrer_name":userName, "referrer_phone":userPhone, "referrer_email":userEmail, "referred_name":referName, "referred_phone":referPhone]
            if let referEmail = referEmail {
                parameters["referred_email"] = referEmail
            }
            return .requestParameters(parameters: parameters, encoding: URLEncoding.default)
        case .redeem(let userToken, let phoneNumber, let email):
            return .requestParameters(parameters: ["token":userToken, "phone":phoneNumber, "email":email], encoding: URLEncoding.default)
        case .login(let userFirstName, let userLastName, let userEmail, let userPhone):
            return .requestParameters(parameters: ["first_name":userFirstName, "last_name":userLastName, "email":userEmail, "phone":userPhone], encoding: URLEncoding.default)
        case .updateUser(let userToken, let userFirstName, let userLastName, let userEmail, let userPhone):
            return .requestParameters(parameters: ["token":userToken, "first_name":userFirstName, "last_name":userLastName, "email":userEmail, "phone":userPhone], encoding: URLEncoding.default)
        case .verifyPhoneNumber(let userToken, let code):
            return .requestParameters(parameters: ["token":userToken, "code":code], encoding: URLEncoding.default)
        case .resendCode(let userToken):
            return .requestParameters(parameters: ["token":userToken], encoding: URLEncoding.default)
        }
    }
    
    var headers: [String: String]? {
        switch self {
        case .getBalance, .refer, .redeem, .login, .updateUser, .verifyPhoneNumber, .resendCode:
            return nil
        }
    }
}

extension PushNotificationService:TargetType {
    var baseURL: URL {
        return BaseURL
    }
        
    var path: String {
        switch self {
        case .registerPushNotifications:
            return "/register/"
        }
    }
    
    var method: Moya.Method {
        switch self {
        case .registerPushNotifications:
            return .get
        }
    }
    
    var sampleData: Data {
        switch self {
        case .registerPushNotifications:
            return "{\"device_token\":\"test\", \"device_type\":1}".data(using: String.Encoding.utf8)!
        }
    }
    
    var task: Task {
        switch self {
        case .registerPushNotifications(let deviceToken, let deviceType):
            return .requestParameters(parameters: ["device_token":deviceToken, "device_type":deviceType], encoding: URLEncoding.default)
        }
    }
    
    var headers: [String: String]? {
        switch self {
        case .registerPushNotifications:
            return nil
        }
    }
}


extension CouponService:TargetType {
    
    var baseURL: URL {
        return URL(string: "https://boltmobile.ca/_app")!
    }
    
    var path:String {
        switch self {
        case .getCoupons:
            return "/coupons.xml"
        }
    }
    
    
    var method: Moya.Method {
        switch self {
        case .getCoupons:
            return .get
        }
    }
    
    var sampleData: Data {
        switch self {
        case .getCoupons:
            return "{}".data(using: String.Encoding.utf8)!
        }
    }
    
    var task: Task {
        switch self {
        case .getCoupons:
            return .requestPlain
        }
    }
    
    var headers: [String: String]? {
        switch self {
        case .getCoupons:
            return nil
        }
    }
}

extension Moya.Response {
    func boltData() throws -> Moya.Response {
        let decoder = JSONDecoder()
        do {
            let boltResponse = try decoder.decode(BoltResponse.self, from: self.data)
            if boltResponse.success {
                return self
            } else {
                throw BoltError.requestFailed(boltResponse.message)
            }
        } catch {
            if self.statusCode == 403 {
                throw BoltError.requestFailed(error.localizedDescription)
            } else {
                throw BoltError.requestFailed(L10n.requestFailedProblemDecoding + "\n" + error.localizedDescription)
            }
        }
    }
    
    func phoneVerificationSuccess() throws -> Bool {
        let decoder = JSONDecoder()
        do {
            let boltResponse = try decoder.decode(BoltResponse.self, from: self.data)
            if boltResponse.success {
                return boltResponse.success
            } else {
                throw BoltError.verificationFailed(boltResponse.message)
            }
        } catch {
            if self.statusCode == 403 {
                throw BoltError.requestFailed(error.localizedDescription)
            } else {
                throw BoltError.requestFailed(L10n.requestFailedProblemDecoding + "\n" + error.localizedDescription)
            }
        }
    }
    
    func pushNotificationSuccess() throws -> Bool {
        let decoder = JSONDecoder()
        do {
            let boltResponse = try decoder.decode(BoltResponse.self, from: self.data)
            //We don't check if success here becuase we want to fail or succeed silently
            return boltResponse.success
        } catch {
            print(error)
            throw BoltError.requestFailed(L10n.requestFailedProblemDecoding)
        }
    }
}

