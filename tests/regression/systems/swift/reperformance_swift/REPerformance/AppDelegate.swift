//
//  AppDelegate.swift
//
//  Created by Alan Yeung on 2017-04-24.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import UserNotifications
import StoreKit
import Photos
import Moya
import FirebaseInstanceID
import FBSDKCoreKit


@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {
	
	//WARNING: Issue with having multiple checkboxes in a single view with M13Checkbox 3.2.1. https://github.com/Marxon13/M13Checkbox/issues/102 , applied fix from the post to line 218/219 of M13Checkbox.swift while we wait for a release that fixes this.
	
	var window: UIWindow?
	var appCoordinator: AppCoordinator?
	
	
	func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
		UNUserNotificationCenter.current().delegate = self
		
		REPVimeoUploaderManager.sharedVideoManager.videoUploader?.applicationDidFinishLaunching()
		ApplicationDelegate.shared.application(application, didFinishLaunchingWithOptions: launchOptions)
		SKPaymentQueue.default().add(SubscriptionService.shared)
		
		self.appCoordinator = AppCoordinator(appDelegate: self)
		
		if let notificationPayload = launchOptions?[UIApplication.LaunchOptionsKey.remoteNotification] as? [String : Any] {
			DispatchQueue.main.asyncAfter(deadline: (.now() + 1), execute: {
				self.handleNotification(notificationPayload)
			})
		}
		
		return true
	}
	
	func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
		let handled = ApplicationDelegate.shared.application(app, open: url, options: options)
		
		return handled
	}
	
	func applicationWillEnterForeground(_ application: UIApplication) {
		DispatchQueue.global(qos: .background).async {
			let cacheManager = CacheSubmissionManager()
			let cacheSubmissions = cacheManager.cacheSubmissions
			
			for submission in cacheSubmissions {
				let videoURL = cacheManager.videoURLInCurrentSandbox(url: submission.videoURL)
				// Deletes the submission data for missing videos otherwise we could end up with a AVURLAsset with no duration.
				if FileManager.default.fileExists(atPath: videoURL.path) == false {
					cacheManager.removeSubmission(submission: submission)
					continue
				}
				
				let asset = AVURLAsset(url: videoURL)
				REPVimeoUploaderManager.sharedVideoManager.uploadToVimeo(asset: asset, identifier: submission.videoIdentifier) {  (vimeoID, error) in
					guard let vimeoID = vimeoID else {
						return
					}
					
					let submitProvider = ExercisesDataProvider()
					submitProvider.submitVimeoId(vimeoId: vimeoID, submissionId: submission.submissionID, completion: { (success, error) in
						if success {
							// remove the submission from the cache list
							cacheManager.removeSubmission(submission: submission)
						}
					})
				}
			}
			cacheManager.clearExpiredMovieFiles()
		}
	}
	
	func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
		guard let token = UserDefaults.standard.userToken else {
			return
		}
		
		let tokenParts = deviceToken.map { data -> String in
			return String(format: "%02.2hhx", data)
		}
		
		let deviceTokenString = tokenParts.joined()
		
		let provider = MoyaProvider<NotificationService>()
		provider.request(.registerDevice(token: token, deviceToken: deviceTokenString)) { _ in }
		
		InstanceID.instanceID().instanceID { (result, error) in
			if let error = error {
				print("Error fetching remote instance ID: \(error)")
			} else if let result = result {
				let provider = MoyaProvider<NotificationService>()
				provider.request(.registerFirebaseToken(token: token, firebaseToken: result.token)) { _ in }
			}
		}
	}
	
	func application(_ application: UIApplication, didReceiveRemoteNotification userInfo: [AnyHashable : Any], fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
		if let _ = userInfo["conversation_id"] as? String {
			guard let appCoordinator = self.appCoordinator else {
				completionHandler(.noData)
				return
			}
			
			appCoordinator.mainCoordinator.reportCardCoordinator.refreshChatUnreadMessagesStatus() {
				completionHandler(.newData)
			}
		}
		else {
			completionHandler(.noData)
		}
	}
	
	
	func configureNotifications() {
		UNUserNotificationCenter.current().requestAuthorization(options: [.sound, .alert, .badge]) { (granted, error) in
			if granted {
				self.getNotificationSettings()
			}
		}
	}
	
	private func getNotificationSettings() {
		UNUserNotificationCenter.current().getNotificationSettings { (settings) in
			guard settings.authorizationStatus == .authorized else {
				return
			}
			
			DispatchQueue.main.async {
				UIApplication.shared.registerForRemoteNotifications()
			}
		}
	}
	
	fileprivate func handleNotification(_ payload: [String : Any]) {
		if let conversationIdentifier = payload["conversation_id"] as? String {
			let name = (((payload["aps"] as? [String : Any])?["alert"] as? [String : Any])?["title"] as? String) ?? ""
			self.launchChat(for: conversationIdentifier, name: name)
		}
	}
	
	static func topMostController() -> UIViewController {
		guard let window = UIApplication.shared.keyWindow, let rootViewController = window.rootViewController else {
			fatalError()
		}
		
		var topController = rootViewController
		while let newTopController = topController.presentedViewController {
			topController = newTopController
		}
		
		return topController
	}
	
	fileprivate func launchChat(for conversationIdentifier: String, name: String) {
		let beginChat = { (vc: UIViewController) in
			let chatCoordinator = ChatCoordinator()
			chatCoordinator.start(presenting: vc, conversationIdentifier: conversationIdentifier, name: name)
		}
		
		// If we are conversing with someone already, dismiss it and show the new conversation (otherwise just present the new conversation).
		let topMostController = AppDelegate.topMostController()
		if let navigationController = topMostController as? UINavigationController, navigationController.viewControllers.filter({ return $0 is ChatMessagesViewController }).count > 0 {
			topMostController.dismiss(animated: true) {
				let nextTopMostController = AppDelegate.topMostController()
				beginChat(nextTopMostController)
			}
		}
		else {
			beginChat(topMostController)
		}
	}
}


extension AppDelegate: UNUserNotificationCenterDelegate {
	
	func userNotificationCenter(_ center: UNUserNotificationCenter, didReceive response: UNNotificationResponse, withCompletionHandler completionHandler: @escaping () -> Void) {
		if let userInfo = response.notification.request.content.userInfo as? [String : Any] {
			self.handleNotification(userInfo)
		}
		
		completionHandler()
	}
	
	func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
		if let conversationIdentifier = notification.request.content.userInfo["conversation_id"] as? String {
			let topMostController = AppDelegate.topMostController()
			if let navigationController = topMostController as? UINavigationController, let chatMessagesViewController = navigationController.viewControllers.first(where: {$0 is ChatMessagesViewController }) as? ChatMessagesViewController {
				// If we are in chat, avoid displaying a notification if we are already conversing with the person (when applicable).
				guard chatMessagesViewController.messagingIdentifiers?.conversationIdentifier != conversationIdentifier else {
					completionHandler([])
					return
				}
			}
		}
		
		completionHandler([.alert, .badge, .sound])
	}
}
