//
//  GoogleError.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-06.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Moya

public enum GoogleError: Swift.Error {
    case requestFailed(String?)
}

public extension GoogleError {
    /// Depending on error type, returns a `Response` object.
    var response: Moya.Response? {
        switch self {
        case .requestFailed: return nil
        }
    }
}

extension GoogleError: LocalizedError {
    public var errorDescription: String? {
        switch self {
        case .requestFailed(let message):
            return message
        }
    }
}
