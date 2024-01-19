//
//  OnboardingDataProvider.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya

struct LoginData {
    let token:String
    let userID:String
    let lastName:String
    let firstName:String
    
    init(token:String, userID:String, lastName:String, firstName:String){
        self.token = token
        self.userID = userID
        self.lastName = lastName
        self.firstName = firstName
    }
}

class OnboardingDataProvider {

    let provider = MoyaProvider<OnboardingService>()
    
    func login(email: String, password: String, completion: @escaping (LoginData?, String?) -> ()) {
        provider.request(.login(email: email, password: password)) { result in
            do {
                let response = try result.dematerialize()
                let loginData = try response.mapToken()
                completion(loginData, nil)
            } catch {
                completion(nil, error.localizedDescription)
            }
        }
	}
	
	func signInWithFacebook(userID: String, token: String, completion: @escaping (LoginData?, String?) -> ()) {
		provider.request(.signupWithFacebook(facebookID: userID, facebookToken: token)) { result in
			do {
				let response = try result.dematerialize()
				let loginData = try response.mapToken()
				completion(loginData, nil)
			} catch {
				completion(nil, error.localizedDescription)
			}
		}
	}
	
    func createAccount(first: String, last: String, email: String, password: String, completion: @escaping (Bool, String?) -> ()) {
        provider.request(.createAccount(first: first, last: last, email: email, password: password)) { result in
            do {
                let response = try result.dematerialize()
                let success = try response.mapSuccess()
                completion(success, nil)
            } catch {
                completion(false, error.localizedDescription)
            }
        }
    }
    
    func forgotPassword(email: String, completion: @escaping (Bool, String?) -> ()) {
        provider.request(.forgotPassword(email: email)) { result in
            do {
                let response = try result.dematerialize()
                let success = try response.mapSuccess()
                completion(success, nil)
            } catch {
                let printableError = error as CustomStringConvertible
                let errorMessage = printableError.description
                completion(false, errorMessage)
            }
        }
    }
}

extension Moya.Response {

    func mapToken() throws -> LoginData {
        let responseObject = try self.map(to: REPerformanceResponse.self)
        
        guard responseObject.success else {
            throw REPerformanceError.requestFailed(responseObject.message)
        }
        
        guard let token = responseObject.data["token"]?.stringValue else {
            throw MoyaError.jsonMapping(self)
        }
        
        guard let userID = responseObject.data["user_id"]?.stringValue else {
            throw MoyaError.jsonMapping(self)
        }
        
        guard let lastName = responseObject.data["last_name"]?.stringValue else {
            throw MoyaError.jsonMapping(self)
        }
        
        guard let firstName = responseObject.data["first_name"]?.stringValue else {
            throw MoyaError.jsonMapping(self)
        }
        
        return LoginData(token: token, userID: userID, lastName:lastName, firstName:firstName)
    }
}
