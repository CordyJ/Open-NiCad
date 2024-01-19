//
//  PushNotificationsDataProvider.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-24.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation
import Moya
import Result

class PushNotificationDataProvider {
    
    public typealias PushNotificationsCompletion = (_ result: Result<Bool, BoltError>) -> Void
    
    let provider = MoyaProvider<PushNotificationService>()
    
    func registerPushNotifications(deviceToken:String, completion: @escaping PushNotificationsCompletion){
        provider.request(.registerPushNotifications(deviceToken: deviceToken, deviceType: 1)) { (result) in
            switch result {
            case let .success(moyaResponse):
                do {
                    let registrationSuccessful = try moyaResponse.pushNotificationSuccess()
                    completion(.success(registrationSuccessful))
                } catch {
                    completion(.failure(BoltError.dataMapping(error.localizedDescription)))
                }
            case let .failure(error):
                completion(.failure(BoltError.dataMapping(error.localizedDescription)))
            }
        }
    }
}
