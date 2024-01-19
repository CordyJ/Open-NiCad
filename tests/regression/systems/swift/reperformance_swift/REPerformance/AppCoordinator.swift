//
//  AppCoordinator.swift
//
//  Created by Alan Yeung on 2017-04-25.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Foundation
import UIKit
import Moya
import Bugsnag
import Firebase
import FirebaseMessaging
import IQKeyboardManagerSwift
import FBSDKLoginKit
import KeychainAccess
import GoogleMaps
import GooglePlaces


class AppCoordinator: NSObject {
	
	let appDelegate: UIApplicationDelegate
	let navigationController: UINavigationController
	let onboardingCoordinator: OnboardingCoordinator
	let mainCoordinator: MainCoordinator
	
	
	init(appDelegate: UIApplicationDelegate) {
		guard let window = appDelegate.window ?? nil else {
			fatalError("The App Delegate didn't have a window.")
		}
		
		self.appDelegate = appDelegate
		self.navigationController = StoryboardScene.Main.initialScene.instantiate()
		self.onboardingCoordinator = OnboardingCoordinator(navigationController: self.navigationController, dataProvider: OnboardingDataProvider())
		self.mainCoordinator = MainCoordinator(window: window)
		
		super.init()
		
		FirebaseApp.configure()
		
		Bugsnag.start(withApiKey: Constants.BugsnagAPIKey)
        Bugsnag.configuration()?.setUser(UserDefaults.standard.userID, withName: nil, andEmail: nil)
		
		self.onboardingCoordinator.onboardingHandler = self
		
		self.setupAppearances()
		self.registerUserDefaults()
		self.setUpGoogleMaps()
		self.setupIQKeyboardManager()
		self.checkFirstLaunch()
		self.setUpMainCoordinator()
		self.start()
	}
	
	private func checkFirstLaunch() {
		if let firstLaunch = UserDefaults.standard.firstLaunch, firstLaunch == true {
			self.removeSubscriptionInformationFromKeychain(completion: { (success) in
				UserDefaults.standard.firstLaunch = false
			})
		}
	}
	
	private func setUpMainCoordinator() {
		self.mainCoordinator.logout = {
			LifestyleDataProvider.wipeAllQuestionnaireDataFromPersistenceLayer(completion: nil)
			self.logoutOfFacebook()
			self.clearData()
			self.clearOnboardingTextFields()
			self.start()
		}
	}
	
	private func logoutOfFacebook() {
		let manager = LoginManager()
		manager.logOut()
	}
	
	private func registerUserDefaults() {
		var defaults = [String : Any]()
		defaults[Constants.UserDefaultsKey.UserToken] = ""
		defaults[Constants.UserDefaultsKey.UserID] = ""
		defaults[Constants.UserDefaultsKey.HasViewLifeStyle] = false
		defaults[Constants.UserDefaultsKey.ProfileIsComplete] = false
		defaults[Constants.UserDefaultsKey.UserFirstName] = ""
		defaults[Constants.UserDefaultsKey.UserLastName] = ""
		defaults[Constants.UserDefaultsKey.LifestyleType] = ""
		defaults[Constants.UserDefaultsKey.UserHasRespondedToNotificationsRequest] = false
		defaults[Constants.UserDefaultsKey.UserCredits] = "0"
		defaults[Constants.UserDefaultsKey.UserWeight] = 0
		defaults[Constants.UserDefaultsKey.UserGender] = ""
		defaults[Constants.UserDefaultsKey.UserFacebookID] = ""
		defaults[Constants.UserDefaultsKey.UserCurrentLocation] = ""
		defaults[Constants.UserDefaultsKey.ProfileNeverFilledOut] = true
		defaults[Constants.UserDefaultsKey.FirstLaunch] = true
		defaults[Constants.UserDefaultsKey.ReportCardNeverSeen] = true
		defaults[Constants.UserDefaultsKey.LeaderboardNeverSeen] = true
		defaults[Constants.UserDefaultsKey.CurrentGymPlaceID] = ""
		defaults[Constants.UserDefaultsKey.ProfileIsPrivate] = false
		
		UserDefaults.standard.register(defaults: defaults)
	}
	
	private func clearUserDefaultsData() {
		UserDefaults.standard.userToken = nil
		UserDefaults.standard.userID = nil
		UserDefaults.standard.hasViewLifeStyle = false
		UserDefaults.standard.profileIsComplete = false
		UserDefaults.standard.userLastName = nil
		UserDefaults.standard.userFirstName = nil
		UserDefaults.standard.lifestyleType = ""
		UserDefaults.standard.userCredits = "0"
		UserDefaults.standard.userWeight = 0
		UserDefaults.standard.userGender = ""
		UserDefaults.standard.userFacebookID = nil
		UserDefaults.standard.userCurrentLocation = nil
		UserDefaults.standard.profileNeverFilledOut = true
		UserDefaults.standard.reportCardNeverSeen = true
		UserDefaults.standard.leaderboardNeverSeen = true
		UserDefaults.standard.currentGymPlaceID = ""
		UserDefaults.standard.isProfilePrivate = false
	}
	
	private func clearData() {
		self.clearUserDefaultsData()
		self.removeSubscriptionInformationFromKeychain(completion: nil)
		self.mainCoordinator.setViewControllers()
		self.mainCoordinator.profileCoordinator.loadLifeStyle()
	}
	
	func removeSubscriptionInformationFromKeychain(completion: ((Bool)->())?) {
		let keychain = Keychain(service: Constants.Keychain.Service)
		do {
			try keychain.remove(Constants.Keychain.CurrentSubscription)
			completion?(true)
		} catch let error {
			print("error: \(error)")
			completion?(false)
		}
	}
	
	private func clearOnboardingTextFields() {
		self.onboardingCoordinator.signUpViewController.clearAllTextfields()
		self.onboardingCoordinator.welcomeViewController.clearUsernameAndPassword()
	}
	
	private func setupAppearances() {
		/* UINavigationBar */
		UINavigationBar.appearance().tintColor = UIColor.white
		UINavigationBar.appearance().titleTextAttributes = [NSAttributedString.Key.foregroundColor : UIColor.white]
		// Make the navigation bar transparent.
		UINavigationBar.appearance().setBackgroundImage(UIImage(), for: .default)
		UINavigationBar.appearance().shadowImage = UIImage()
		UINavigationBar.appearance().isTranslucent = true
		
		/* UITabBar */
		UITabBar.appearance().backgroundColor = UIColor.white
		UITabBar.appearance().tintColor = UIColor(named: .rePerformanceOrange)
		
		/* Switch */
		UISwitch.appearance().onTintColor = UIColor(named: .rePerformanceOrange)
	}
	
	private func setupIQKeyboardManager() {
		IQKeyboardManager.shared.enable = true
		IQKeyboardManager.shared.enableAutoToolbar = true
	}
	
	func setUpGoogleMaps() {
		GMSServices.provideAPIKey(Constants.Google.APIKey)
		GMSPlacesClient.provideAPIKey(Constants.Google.APIKey)
	}
	
	func registerUserForPushNotification() {
		guard let appDelegate = self.appDelegate as? AppDelegate else {
			fatalError()
		}
		
		appDelegate.configureNotifications()
	}
	
	func start() {
		guard let window = self.appDelegate.window ?? nil else {
			fatalError("The App Delegate didn't have a window.")
		}
		
		window.rootViewController = self.navigationController
		
		if let userToken = UserDefaults.standard.userToken, userToken.isEmpty {
			self.onboardingCoordinator.start()
		}
		else if UserDefaults.standard.hasViewLifeStyle == false {
			self.onboardingCoordinator.startLifeCategories()
		}
		else {
			self.registerUserForPushNotification()
			self.mainCoordinator.start()
		}
	}
}


extension AppCoordinator: OnboardingHandler {
	
	func userHasLoggedIn(token: String, userID: String, userLastName: String, userFirstName: String, userFacebookID: String?) {
		UserDefaults.standard.userToken = token
		UserDefaults.standard.userID = userID
		UserDefaults.standard.userLastName = userLastName
		UserDefaults.standard.userFirstName = userFirstName
		UserDefaults.standard.userFacebookID = userFacebookID
		self.start()
	}
	
	func userHasViewLifestyleTutorial() {
		UserDefaults.standard.hasViewLifeStyle = true
		self.start()
	}
}
