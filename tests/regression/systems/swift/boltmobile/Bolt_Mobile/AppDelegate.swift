//
//  AppDelegate.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-15.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?
    var appCoordinator:AppCoordinator?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        
        appCoordinator = AppCoordinator(appDelegate: self)
        return true
    }

    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
        // Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
        // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
    }

    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        let tokenParts = deviceToken.map { data -> String in
            return String(format: "%02.2hhx", data)
        }
        let token = tokenParts.joined()
        
        print("TOKEN: \(token)")
        
        let dataProvider = PushNotificationDataProvider()
        dataProvider.registerPushNotifications(deviceToken: token) { (result) in
            switch result {
            case let .success(registrationSuccessful):
                print("Successfully registered for push notifications: \(registrationSuccessful)")
            case let .failure(error):
                print(error.localizedDescription)
            }
        }
    }
    
    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {
        print("Failed to register for push notifications: \(error.localizedDescription)")
    }
    
    func application(_ application: UIApplication, didReceiveRemoteNotification userInfo: [AnyHashable : Any], fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
        guard var currentViewController:UIViewController = UIApplication.shared.keyWindow?.rootViewController else {
            return
        }
        while currentViewController.presentedViewController != nil {
            if let current = currentViewController.presentedViewController {
                currentViewController = current
            }
        }
        
        if let aps = userInfo["aps"] as? [String:Any], let alert = aps["alert"] as? [String:String], let title = alert["title"], let body = alert["body"] {
            UIAlertController.showAlert(title: title, message: body, inViewController: currentViewController)
        }
        
        completionHandler(.noData)
    }
    
}

