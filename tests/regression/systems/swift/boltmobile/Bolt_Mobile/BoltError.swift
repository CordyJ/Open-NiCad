//
//  BoltError.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation
//import Moya

public enum BoltError: Swift.Error {
    case requestFailed(String?)
    case dataMapping(String?)
    case moyaError(String?)
    case internetNotReachable
    case missingToken
    case verificationFailed(String?)
    case invalidUser
}

extension BoltError: LocalizedError {
    public var errorDescription: String? {
        switch self {
        case .requestFailed(let message), .dataMapping(let message), .moyaError(let message), .verificationFailed(let message):
            return message
        case .internetNotReachable:
            return L10n.internetNotReachableError
        case .missingToken:
            return L10n.verificationMissingToken
        case .invalidUser:
            return L10n.verificationInvalidUserMessage
        }
    }
}
