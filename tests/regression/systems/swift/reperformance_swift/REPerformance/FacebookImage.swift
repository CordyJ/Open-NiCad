//
//  FacebookImage.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import FBSDKCoreKit


enum FacebookImageSize {
	case square
	case small
	case normal
	case large
	
	fileprivate var typeArgument: String {
		get {
			switch self {
			case .square:
				return "type=square"
			case .small:
				return "type=small"
			case .normal:
				return "type=normal"
			case .large:
				return "type=large"
			}
		}
	}
}


class FacebookImage: NSObject {
	
	static func imageURLWithFacebookID(_ facebookID: String?, imageSize: FacebookImageSize = .square) -> URL? {
		guard let facebookID = facebookID, facebookID != "" else {
			return nil
		}
		
		return URL(string: "http://graph.facebook.com/\(facebookID)/picture?\(imageSize.typeArgument)")
	}
	
	static func imageURLWithFacebookID(_ facebookID: String?, size: CGSize) -> URL? {
		guard let facebookID = facebookID, facebookID != "" else {
			return nil
		}
		
		return URL(string: "http://graph.facebook.com/\(facebookID)/picture?width=\(Int(size.width))&height=\(Int(size.height))")
	}
}
