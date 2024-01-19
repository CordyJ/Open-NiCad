//
//  REPerformanceError.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation


public enum REPerformanceError: Swift.Error {
	case userTokenMissing
	case requestFailed(String?)
}


extension REPerformanceError: LocalizedError {
	
	public var errorDescription: String? {
		switch self {
		case .userTokenMissing:
			return L10n.userTokenMissingMessage
		case .requestFailed(let message):
			return message
		}
	}
}
