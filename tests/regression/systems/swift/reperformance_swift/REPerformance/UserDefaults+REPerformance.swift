//
//  NSUserDefaults+REPerformance.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-29.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Bugsnag


extension UserDefaults {
	
	var userToken: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserToken)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserToken)
		}
	}
	
	var isProfilePrivate: Bool {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.ProfileIsPrivate)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.ProfileIsPrivate)
		}
	}
	
	var hasViewLifeStyle: Bool? {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.HasViewLifeStyle)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.HasViewLifeStyle)
		}
	}
	
	var profileIsComplete: Bool? {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.ProfileIsComplete)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.ProfileIsComplete)
		}
	}
	
	var userLastName: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserLastName)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserLastName)
		}
	}
	
	var userFirstName: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserFirstName)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserFirstName)
		}
	}
	
	var lifestyleType: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.LifestyleType)
		}
		set {
			UserDefaults.standard.set(newValue, forKey:Constants.UserDefaultsKey.LifestyleType)
		}
	}
	
	var userID: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserID)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserID)
            Bugsnag.configuration()?.setUser(newValue, withName: nil, andEmail: nil)
		}
	}
	
	var userAge: Int? {
		get {
			if let _ = UserDefaults.standard.value(forKey: Constants.UserDefaultsKey.UserAge) {
				return UserDefaults.standard.integer(forKey: Constants.UserDefaultsKey.UserAge)
			}
			else {		// Age is normally stored as a file but is slow to read from, so try and extract the age and assign it to UserDefaults for future use.
				let lifestyleDataProvider = LifestyleDataProvider()
				if let lifestyleBasicInfoData = lifestyleDataProvider.loadBasicInfoData(), let age = lifestyleDataProvider.getAge(basicInfo: lifestyleBasicInfoData) {
					UserDefaults.standard.set(age, forKey: Constants.UserDefaultsKey.UserAge)
					return age
				}
			}
			
			return nil
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserAge)
		}
	}
	
	var userWeight: Int? {
		get {
			return UserDefaults.standard.integer(forKey: Constants.UserDefaultsKey.UserWeight)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserWeight)
		}
	}
	
	var userGender: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserGender)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserGender)
		}
	}
	
	var userHasRespondedToNotificationsRequest: Bool? {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.UserHasRespondedToNotificationsRequest)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserHasRespondedToNotificationsRequest)
		}
	}
	
	var userCredits: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserCredits)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserCredits)
		}
	}
	
	var userDollars: Float? {
		get {
			return UserDefaults.standard.float(forKey: Constants.UserDefaultsKey.UserDollars)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserDollars)
		}
	}
	
	var userFacebookID: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserFacebookID)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserFacebookID)
		}
	}
	
	var userCurrentLocation: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.UserCurrentLocation)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.UserCurrentLocation)
		}
	}
	var profileNeverFilledOut: Bool? {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.ProfileNeverFilledOut)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.ProfileNeverFilledOut)
		}
	}
	
	var firstLaunch: Bool? {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.FirstLaunch)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.FirstLaunch)
		}
	}
	
	var reportCardNeverSeen: Bool? {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.ReportCardNeverSeen)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.ReportCardNeverSeen)
		}
	}
	
	var leaderboardNeverSeen: Bool? {
		get {
			return UserDefaults.standard.bool(forKey: Constants.UserDefaultsKey.LeaderboardNeverSeen)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.LeaderboardNeverSeen)
		}
	}
	
	var currentGymPlaceID: String? {
		get {
			return UserDefaults.standard.string(forKey: Constants.UserDefaultsKey.CurrentGymPlaceID)
		}
		set {
			UserDefaults.standard.set(newValue, forKey: Constants.UserDefaultsKey.CurrentGymPlaceID)
		}
	}
	
	var lastAppVersionCheck: String? {
		get {
			return string(forKey: Constants.UserDefaultsKey.LastAppVersionCheck)
		}
		set {
			set(newValue, forKey: Constants.UserDefaultsKey.LastAppVersionCheck)
		}
	}
}
