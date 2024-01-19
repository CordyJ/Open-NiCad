//
//  AppCoordinator.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-15.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import Bugsnag
import IQKeyboardManagerSwift

class AppCoordinator {
    
    let navigationController:UINavigationController
    let mainCoordinator:MainCoordinator
    
    init(appDelegate:UIApplicationDelegate) {
        guard let window:UIWindow = appDelegate.window ?? nil else {
            fatalError("The App Delegate didn't have a window")
        }
        navigationController = StoryboardScene.Main.initialScene.instantiate()
        mainCoordinator = MainCoordinator(window: window, navController: navigationController)
        
        setUpBugsnag()
        
        BoltAnalytics.initializeAnalytics()
        
        UserDefaults.registerBoltMobileDefaults()
        UserDefaults.registerBoltMobileUserInformationDefaults()
        
        setUpAppearance()
        setUpKeyboardManager()
        
        start(window: window)
    }
    
    private func setUpBugsnag() {
        Bugsnag.start(withApiKey: Constants.Bugsnag.Key)
    }
    
    
    private func setUpAppearance() {
        UINavigationBar.appearance().backgroundColor = UIColor.white
        UINavigationBar.appearance().isTranslucent = false
        UINavigationBar.appearance().tintColor = UIColor(named: .boltMobileBlueLabel)
        UINavigationBar.appearance().titleTextAttributes = [NSAttributedString.Key.foregroundColor : UIColor(named: .boltMobileBlueLabel)]
    }
    
    private func setUpKeyboardManager() {
        IQKeyboardManager.shared.enable = true
    }
    
    func start(window:UIWindow) {
        window.rootViewController = navigationController
        mainCoordinator.start()
    }
    
}
