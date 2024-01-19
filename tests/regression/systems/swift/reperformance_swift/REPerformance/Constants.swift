//
//  Constants.swift
//
//  Created by Alan Yeung on 2017-04-26.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import NVActivityIndicatorView

struct Constants {
    
    static let BundleIdentifier = "com.collegemobile.REPerformance"
    static let BugsnagAPIKey = "e43b72289c095e73d7e527ca92397525"
    static let TermsAndConditionsFilename = "termsAndConditions"
    static let PrivacyFilename = "privacy"
    static let GoogleAnalyticsKey = "UA-38460636-6"
    
    struct UserDefaultsKey {
        static let UserToken = BundleIdentifier + ".USER_TOKEN_DEFAULTS_KEY"
		static let ProfileIsPrivate = BundleIdentifier + ".PROFILE_IS_PRIVATE_DEFAULTS_KEY"
        static let HasViewLifeStyle = BundleIdentifier + ".VIEW_LIFESTYLE_DEFAULTS_KEY"
        static let ProfileIsComplete = BundleIdentifier + ".PROFILE_COMPLETE_DEFAULTS_KEY"
        static let UserLastName = BundleIdentifier + ".USER_LAST_NAME_KEY"
        static let UserFirstName = BundleIdentifier + ".USER_FIRST_NAME_KEY"
        static let LifestyleType = BundleIdentifier + ".LIFESTYLE_TYPE_KEY"
        static let UserID = BundleIdentifier + ".USER_ID_KEY"
		static let UserAge = BundleIdentifier + ".USER_AGE"
        static let UserWeight = BundleIdentifier + ".USER_WEIGHT"
        static let UserGender = BundleIdentifier + ".USER_GENDER"
        static let UserHasRespondedToNotificationsRequest = BundleIdentifier + ".RESPONDED_TO_NOTIFICATIONS_REQUEST_KEY"
        static let UserCurrentLocation = BundleIdentifier + ".REPerformance.USER_CURRENT_LOCATION"
        static let UserCredits = BundleIdentifier + ".USER_CREDITS"
        static let UserDollars = BundleIdentifier + ".USER_DOLLARS"
        static let UserFacebookID = BundleIdentifier + ".USER_FACEBOOK_ID"
        static let ProfileNeverFilledOut = BundleIdentifier + ".PROFILE_NEVER_FILLED_OUT"
        static let ReportCardNeverSeen = BundleIdentifier + ".REPORT_CARD_NEVER_SEEN"
        static let FirstLaunch = BundleIdentifier + ".FIRST_LAUNCH"
        static let LeaderboardNeverSeen = BundleIdentifier + ".LEADERBOARD_NEVER_SEEN"
        static let CurrentGymPlaceID = BundleIdentifier + ".CURRENT_GYM_PLACE_ID"
        static let LastAppVersionCheck = BundleIdentifier + ".LAST_APP_VERSION"
        static let ProfileImage = BundleIdentifier + ".PROFILE_IMAGE"
    }
    
    struct UIConstants {
        static let CornerRadius: CGFloat = 5.0
        static let LogoutButtonCornerRadius:CGFloat = 20.0
        static let BorderWidth: CGFloat = 2.0
        
        struct SearchBar {
            static let BackgroundAlpha:CGFloat = 0.2
            static let CornerRadius:CGFloat = 5.0
            static let BorderWidth:CGFloat = 1.0
            static let PlaceholderAlpha:CGFloat = 0.5
        }
    }
    
    struct ReportCard{
        static let RefreshTimeInterval:TimeInterval = 1800 //time in seconds to refresh the report card screen, currently set to 30 minutes
        
        static let LeaderboardPositionCellIdentifier = "leaderboardPositionCell"
        static let LeaderboardDividerCellIdentifier = "leaderboardDividerCell"
        static let LeaderboardSelectionHeaderCell = "LeaderboardSelectionHeaderCell"
        static let LeaderboardSelectionCell = "LeaderboardSelectionCell"
        static let LeaderboardErrorCellIdentifier = "leaderboardErrorCellID"
        
        static let LeaderboardSelectionHeaderCellHeight:CGFloat = 70
        static let GlobalLeaderboardSelectionCellTitleText = "All Tests"
        
        static let REPerformanceWebsiteURLString = "http://www.reperformanceapp.com"
    }
    
    struct OurValue{
        static let OurValueTableViewCellIdentifier = "ourValueTableViewCell"
        static let EndorsementsTableViewCellIdentifier = "endorsementsTableViewCell"
        static let EndorsementsVideoYouTubeID = "DrIIBcE1wi4"
    }
    
    struct Profile {
        static let TitleKey = "title"
        static let SelectedKey = "selected"
        static let PointsKey = "points"
        static let ValueKey = "value"
        
        static let BasicProfileCellIdentifier = "BasicProfileCellIdentifier"
        static let ValueAndUnitsProfileCellIdentifier = "ValueAndUnitsProfileCellIdentifier"
        static let ValueProfileCellIdentifier = "ValueProfileCellIdentifier"
        static let LocationCellIdentifier = "LocationCellIdentifier"
        static let HeightTableViewCellIdentifier = "HeightTableViewCellIdentifier"
        
        static let BasicInfoQuestionnaireFilePath = "/basicInfo.dat"
        static let NutritionQuestionnaireFilePath = "/nutrition.dat"
        static let LifestyleQuestionnaireFilePath = "/lifestyle.dat"
        static let ExerciseQuestionnaireFilePath = "/exercise.dat"
        
        static let BasicInfoQuestionnaireTitle = "Basic Info"
        static let NutritionQuestionnaireTitle = "Nutrition"
        static let LifestyleQuestionnaireTitle = "Lifestyle"
        static let ExerciseQuestionnaireTitle = "Exercise"
        
        static let LifestyleActionCeiling = 58
        static let LifestyleFitCeiling = 108
        static let LifestyleAthleteCeiling = 147
        
        static let TableViewHeaderBuffer:CGFloat = 20
        static let TableViewHeaderFontSize:CGFloat = 18
        
        static let BasicInfoAgeQuestionIndex = 3
        static let BasicInfoCountryQuestionIndex = 4
        static let BasicInfoProvinceQuestionIndex = 5
        static let BasicInfoWeightQuestionIndex = 0
        static let BasicInfoWeightInKGIndex = 2
        static let BasicInfoGenderQuestionIndex = 1
        static let BasicInfoHeightQuestionIndex = 2
        
        static let PoundsPerKilogram = 2.20463
        
        static let TableViewFooterHeight:CGFloat = 70
        static let TableViewFooterButtonHeight:CGFloat = 40

        static let ProfileNotificationTimeInterval:TimeInterval = 7776000 //Number of seconds since last update until notification is given to update profile, currently set to 90 days
    }
    
    struct Exercises {
        static let InstagramSharedApplicationURL = "instagram://library?LocalIdentifier="
    }
    
    struct Rewards{
        static let RewardsCellIdentifier = "viewRewardsCell"
        static let RefreshTimeInterval:TimeInterval = 1800 //time in seconds to refresh the reward screen, currently set to 30 minutes
    }
    
    struct PaidSubscriptionKey {
        static let ProductIdentifierKey = BundleIdentifier + ".ProductIdentifierKey"
        static let PurchaseDateKey = BundleIdentifier + ".PurchaseDateKey"
        static let ExpiresDateKey = BundleIdentifier + ".ExpiresDateKey"
        static let LevelKey = BundleIdentifier + ".LevelKey"
    }
    
    struct Vimeo {
        static let BackgroundIdentifier = BundleIdentifier + ".Upload"
    #if USE_PRODUCTION
        static let AuthKey = "d2384d9e1264952df06d9354a73f2e85"  // This is Callen's Vimeo account
        static let VideoExpiration:TimeInterval = 60*60*24
        static let UploadTimeout:TimeInterval = 60
    #else
        static let AuthKey = "e73bba6bb158aba46e0fb61a5322e729"  // This is PUSH's Vimeo account
        static let VideoExpiration:TimeInterval = 60
        static let UploadTimeout:TimeInterval = 10
    #endif
    }
    
    static let activityData = ActivityData(type: .ballPulse)
    
    struct UserData{
        static let Male = "Male"
        static let Female = "Female"
    }
    
    struct Keychain {
        static let Service = BundleIdentifier + ".KeychainService"
        static let CurrentSubscription = BundleIdentifier + ".CURRENT_SUBSCRIPTION_KEY"
    }
    
    struct Google {
        static let APIKey = "AIzaSyBGox6E6KaTgf6AsY6KPMXVz08ffAo0_rA"
    }
    
    struct GymLeaderboard {
        static let MapSearchResultsCellID = "mapSearchResultCellIdentifier"
        static let NearbySearchRadius = 30000 //Radius to search in meters.
    }
    
    struct Challenges {
        static let ChallengesCellIdentifier = "ChallengesCellIdentifier"
        static let ChallengeGymCellIdentifier = "ChallengeGymCellIdentifier"
    }
    
    static let secondsInOneHour:TimeInterval = 60*60
}
