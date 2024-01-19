//
//  Constants.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-15.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import NVActivityIndicatorView

enum Constants {
    
    enum Bugsnag {
        static let Key = "4432e6768f1f4773bee47a1b88cb8d06"
    }
    
    enum GoogleAnalytics {
        static let Key = "UA-115610224-1"
    }
    
    enum UI{
        static let DefaultCellIdentifier = "default"
    }
    
    enum ActivityIndicator {
        static let activityData = ActivityData(type: .ballClipRotate)
    }
    
    enum BookAppointment {
        static let AppointmentBookingURLString = "https://boltmobile.setmore.com"
        static let RequestTimeout:TimeInterval = 30.0
    }
    
    enum AskExpert {
        static let CirclePhoneNumber = "13066684653"
        static let EightStreetPhoneNumber = "13069556400"
        static let AttridgePhoneNumber = "13066649700"
        static let RosewoodPhoneNumber = "13062494460"
        
        static let CircleEmail = "circle@boltmobile.ca"
        static let EightStreetEmail = "8th@boltmobile.ca"
        static let AttridgeEmail = "attridge@boltmobile.ca"
        static let RosewoodEmail = "rosewood@boltmobile.ca"
    }
    
    enum DeviceUpgrade {
        static let UpgradeNumber = "43383"
        static let BrowsePhonesURLString = "https://boltmobile.ca/product-category/sasktel-apple-iphones/"
        static let ShopAccessoriesURLString = "https://boltmobile.ca/product-category/accessories/"
    }
    

    enum UserDefaultsKey {
        private static let BundleIdentifier = "com.collegemobile.Bolt-Mobile"
        static let SeenReferralsInstructions = BundleIdentifier + ".SEEN_REFERRALS_INSTRUCTIONS"
        static let SeenWelcomeVC = BundleIdentifier + ".SEEN_WELCOME_VC"
        static let UserFirstName = BundleIdentifier + ".USER_FIRST_NAME"
        static let UserLastName = BundleIdentifier + ".USER_LAST_NAME"
        static let UserEmail = BundleIdentifier + ".USER_EMAIL"
        static let UserPhoneNumber = BundleIdentifier + ".USER_PHONE_NUMBER"
        static let PushNotificationsToken = BundleIdentifier + ".PUSH_NOTIFICATIONS_TOKEN"
        static let PushNotificationsAppleRegistrationSuccessful = BundleIdentifier + ".APPLE_REGISTRATION_SUCCESSFUL"
        static let PushNotificationsBoltServerRegistrationSuccessful = BundleIdentifier + ".BOLT_REGISTRATION_SUCCESSFUL"
        static let UserToken = BundleIdentifier + ".USER_TOKEN"
    }
    
    enum Keychain {
        private static let BundleIdentifier = "com.collegemobile.Bolt-Mobile"
        static let Service = BundleIdentifier + ".KEYCHAIN_SERVICE"
        static let UsedCouponsKey = BundleIdentifier + ".USED_COUPONS"
    }
    
    enum Coupons {
        static let CouponCellIdentifier = "couponCell"
    }
    
    enum Location {
        static let filename = "bolt-stores"
    }
}
