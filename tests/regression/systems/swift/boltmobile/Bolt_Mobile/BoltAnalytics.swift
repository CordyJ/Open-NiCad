//
//  BoltAnalytics.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-27.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import Foundation
import Firebase

enum ScreenName:String {
    case Welcome
    case HomeScreen
    case Referrals
    case Coupons
    case ContactReview
    case AskExpert
    case DeviceUpgrade
    case BookAppointment
}

enum Action:String {
    case GetStartedTapped
    case SubmitReferralTapped
    case RedeemBoltBucksTapped
    case IndividualCouponTapped
    case LocationDetailsViewed
    case PhoneTapped
    case WebsiteTapped
    case EmailTapped
    case ReviewFacebookTapped
    case ReviewGoogleTapped
    case UpgradeMessageTapped
}

class BoltAnalytics {
    
    class func initializeAnalytics(){
        FirebaseApp.configure()
    }
    
    class func trackScreenWithName(screenName:ScreenName){
        Analytics.setScreenName(screenName.rawValue, screenClass: nil)
    }
    
    class func trackEvent(category:ScreenName, action:Action, label:String?){
        var parameters = [String : Any]()
        parameters["action"] = action.rawValue
        if let label = label {
            parameters["label"] = label
        }
        Analytics.logEvent(category.rawValue, parameters: parameters)
    }
}
