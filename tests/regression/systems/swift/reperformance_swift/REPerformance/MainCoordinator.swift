//
//  MainCoordinator.swift
//
//  Created by Alan Yeung on 2017-04-27.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import UserNotifications


class MainCoordinator {
	
	let mainWindow: UIWindow
	let mainTabBarController: UITabBarController
	let exercisesCoordinator: ExercisesCoordinator
	let reportCardCoordinator: ReportCardCoordinator
	let rewardsCoordinator: RewardsCoordinator
	let leaderboardCoordinator: LeaderboardCoordinator
	let profileCoordinator: ProfileCoordinator
	let profileNotCompleteViewControllerExercises: REPerformanceWarningViewController
	let profileNotCompleteViewControllerReportCard: REPerformanceWarningViewController
	let profileNotCompleteViewControllerRewards: REPerformanceWarningViewController
	let profileNotCompleteViewControllerLeaderboard: REPerformanceWarningViewController
	
	var profileLifeStyle: LifestyleType?
	
	var logout: (()->())?
	
	
	init(window: UIWindow) {
		self.mainWindow = window
		self.mainTabBarController = UITabBarController()
		
		self.exercisesCoordinator = ExercisesCoordinator(dataProvider: ExercisesDataProvider())
		self.reportCardCoordinator = ReportCardCoordinator()
		self.rewardsCoordinator = RewardsCoordinator()
		self.leaderboardCoordinator = LeaderboardCoordinator()
		self.profileCoordinator = ProfileCoordinator(dataProvider: ProfileDataProvider())
		
		self.profileNotCompleteViewControllerExercises = StoryboardScene.Main.rePerformanceWarningVC.instantiate()
		self.profileNotCompleteViewControllerReportCard = StoryboardScene.Main.rePerformanceWarningVC.instantiate()
		self.profileNotCompleteViewControllerRewards = StoryboardScene.Main.rePerformanceWarningVC.instantiate()
		self.profileNotCompleteViewControllerLeaderboard = StoryboardScene.Main.rePerformanceWarningVC.instantiate()
		
		self.setViewControllers()
		self.setUpProfileNotCompleteViewControllers()
		self.setInitialViewController()
		self.setUpProfileCoordinator()
		self.setUpExercisesCoordinator()
	}
	
	func setInitialViewController() {
		if UserDefaults.standard.profileIsComplete == false {
			self.mainTabBarController.selectedViewController = self.profileCoordinator.tabBarViewController()
		} else {
			self.mainTabBarController.selectedViewController = self.exercisesCoordinator.tabBarViewController()
		}
	}
	
	func setViewControllers() {
		if UserDefaults.standard.profileIsComplete == false {
			self.mainTabBarController.viewControllers = [self.profileNotCompleteViewControllerExercises, self.profileNotCompleteViewControllerReportCard, self.profileNotCompleteViewControllerRewards, self.profileNotCompleteViewControllerLeaderboard, self.profileCoordinator.tabBarViewController()]
		} else {
			self.mainTabBarController.viewControllers = [self.exercisesCoordinator.tabBarViewController(), self.reportCardCoordinator.tabBarViewController(), self.rewardsCoordinator.tabBarViewController(), self.leaderboardCoordinator.tabBarViewController(), self.profileCoordinator.tabBarViewController()]
		}
	}
	
	func setUpProfileNotCompleteViewControllers() {
		self.profileNotCompleteViewControllerExercises.tabBarItem = UITabBarItem(title: L10n.testTabBarItemTitle, image: Asset.Assets.TabBar.tabBarTests.image, tag: 0)
		self.profileNotCompleteViewControllerExercises.configureView(titleText: L10n.profileNotLoggedInTitle, descriptionText: L10n.exerciseProfileNotLoggedInDescription, okButtonVisible: true, cancelButtonVisible: false)
		
		self.profileNotCompleteViewControllerReportCard.tabBarItem = UITabBarItem(title: L10n.reportCardTabBarItemTitle, image: Asset.Assets.TabBar.tabBarReportCard.image, tag: 0)
		self.profileNotCompleteViewControllerReportCard.configureView(titleText: L10n.profileNotLoggedInTitle, descriptionText: L10n.reportCardNotLoggedInDescription, okButtonVisible: true, cancelButtonVisible: false)
		
		self.profileNotCompleteViewControllerRewards.tabBarItem = UITabBarItem(title: L10n.rewardsTabItemTitle, image: Asset.Assets.TabBar.tabBarRewards.image, tag: 0)
		self.profileNotCompleteViewControllerRewards.configureView(titleText: L10n.profileNotLoggedInTitle, descriptionText: L10n.rewardsNotLoggedInDescription, okButtonVisible: true, cancelButtonVisible: false)
		
		self.profileNotCompleteViewControllerLeaderboard.tabBarItem = UITabBarItem(title: L10n.leaderboardTabBarItemTitle, image: #imageLiteral(resourceName: "TabBar_Leaderboard"), tag: 0)
		self.profileNotCompleteViewControllerLeaderboard.configureView(titleText: L10n.profileNotLoggedInTitle, descriptionText: L10n.leaderboardNotLoggedInDescription, okButtonVisible: true, cancelButtonVisible: false)
		
		self.profileNotCompleteViewControllerExercises.ok = {
			self.mainTabBarController.selectedViewController = self.profileCoordinator.tabBarViewController()
		}
		
		self.profileNotCompleteViewControllerReportCard.ok = {
			self.mainTabBarController.selectedViewController = self.profileCoordinator.tabBarViewController()
		}
		
		self.profileNotCompleteViewControllerRewards.ok = {
			self.mainTabBarController.selectedViewController = self.profileCoordinator.tabBarViewController()
		}
		
		self.profileNotCompleteViewControllerLeaderboard.ok = {
			self.mainTabBarController.selectedViewController = self.profileCoordinator.tabBarViewController()
		}
	}
	
	func setUpProfileCoordinator() {
		self.profileCoordinator.profileCompletionChanged = {
			self.setViewControllers()
		}
		
		self.profileCoordinator.setReportCardNeedsUpdate = {
			self.reportCardCoordinator.updateReportCardRequired = true
		}
		
		self.profileCoordinator.logout = {
			self.reportCardCoordinator.recreateReportCard()
			self.logout?()
		}
		
		self.profileCoordinator.profileNotification = {
			self.fireProfileReminderNotification()
		}
		
		self.profileCoordinator.profileFilledOutFirstTime = {
			self.mainTabBarController.selectedViewController = self.exercisesCoordinator.tabBarViewController()
		}
		
		self.profileCoordinator.genderChanged = {
			self.reportCardCoordinator.recreateReportCard()
		}
	}
	
	func fireProfileReminderNotification() {
		let content = UNMutableNotificationContent()
		content.body = L10n.profileNotificationBody
		content.sound = .default
		
		let calendar = Calendar(identifier: .gregorian)
		let components = calendar.dateComponents(in: .current, from: Date.init(timeIntervalSinceNow: Constants.Profile.ProfileNotificationTimeInterval))
		let newComponents = DateComponents(calendar: calendar, timeZone: .current, month: components.month, day: components.day, hour: components.hour, minute: components.minute)
		let trigger = UNCalendarNotificationTrigger(dateMatching: newComponents, repeats: true)
		
		let request = UNNotificationRequest(identifier: "Profile Update Reminder Local Notification", content: content, trigger: trigger)
		UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
		UNUserNotificationCenter.current().add(request) { _ in }
	}
	
	func setUpExercisesCoordinator() {
		self.exercisesCoordinator.setReportCardAndCreditsNeedsUpdate = {
			self.reportCardCoordinator.updateReportCardRequired = true
			CreditsUpdater.updateCredits(completion: nil)
		}
	}
	
	func start() {
		self.mainWindow.rootViewController = self.mainTabBarController
		
		CreditsUpdater.updateCredits(completion: nil)
		self.applyUpdatesIfNeeded()
		self.reportCardCoordinator.refreshChatUnreadMessagesStatus()
	}
	
	private func applyUpdatesIfNeeded() {
		let lastAppVersionCheck = UserDefaults.standard.lastAppVersionCheck ?? "0.0.0"
		
		// Submiting the gender with the profile introduced in app version 1.2.6.
		// Makes one silent attempt, otherwise will be sent the next time the profile tab is opened or profile updated.
		if lastAppVersionCheck.compare("1.2.6", options: .numeric) == .orderedAscending {
			self.profileCoordinator.silentlySubmitProfile()
			UserDefaults.standard.lastAppVersionCheck = Bundle.main.infoDictionary!["CFBundleShortVersionString"] as? String
		}
	}
}
