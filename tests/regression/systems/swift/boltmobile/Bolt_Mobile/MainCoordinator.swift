//
//  MainCoordinator.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-15.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import MapKit
import UserNotifications
import MessageUI
import KeychainAccess
import NVActivityIndicatorView

struct StoreLocation {
    let hoursURL: String
    let title: String
    let picture: String
    let address: String
    let phone: String
    let website: String
    let email: String
    let facebook: String
    let google: String
    let coordinate: CLLocationCoordinate2D

    init(data:Dictionary<String, Any>) {
        self.hoursURL = data["hoursURL"] as? String ?? ""
        self.title = data["title"] as? String ?? ""
        self.picture = data["picture"] as? String ?? ""
        self.address = data["address"] as? String ?? ""
        self.phone = data["phone"] as? String ?? ""
        self.website = data["website"] as? String ?? ""
        self.email = data["email"] as? String ?? ""
        self.facebook = data["facebook"] as? String ?? ""
        self.google = data["google"] as? String ?? ""
        self.coordinate = CLLocationCoordinate2DMake(data["latitude"] as! CLLocationDegrees, data["longitude"] as! CLLocationDegrees)
    }
}

class MainCoordinator:NSObject {
    
    let mainWindow:UIWindow
    let navigationController:UINavigationController
    let referralsCoordinator:ReferralsCoordinator
    
    let messageService:MessageService
    
    var deviceUpgradeVC:DeviceUpgradeViewController?
    
    init(window:UIWindow, navController:UINavigationController){
        mainWindow = window
        navigationController = navController
        messageService = MessageService(navController: navigationController, type: .upgrade)
        referralsCoordinator = ReferralsCoordinator(navController: navigationController)
    }
    
    func start(){
        navigationController.delegate = self
        navigationController.modalPresentationStyle = .fullScreen
        if let hasSeenWelcomeVideo = UserDefaults.hasSeenWelcomeVC, hasSeenWelcomeVideo {
            moveToHomeVC()
        } else {
            moveToWelcomeVC()
        }
    }
    
    private func moveToWelcomeVC(){
        
        let welcomeViewController = StoryboardScene.Main.welcomeVC.instantiate()
        
        welcomeViewController.getStarted = {
            BoltAnalytics.trackEvent(category: .Welcome, action: .GetStartedTapped, label: nil)
            self.moveToHomeVC()
        }
        
        navigationController.setViewControllers([welcomeViewController], animated: true)
        UserDefaults.hasSeenWelcomeVC = true
    }
    
    private func moveToHomeVC(){
        let homeVC = StoryboardScene.Main.homeVC.instantiate()
        homeVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        
        homeVC.myReferrals = {
            self.referralsCoordinator.start()
        }
        
        homeVC.coupons = {
            self.moveToCouponsVC()
        }
        
        homeVC.contactReview = { [unowned self] in
            self.moveToContactReviewVC()
        }
        
        homeVC.askExpert = {
            self.moveToAskExpertVC()
        }
        
        homeVC.deviceUpgrade = {
            self.moveToDeviceUpgradeVC()
        }
        
        homeVC.bookAppointment = { [unowned self] in
            self.moveToBookAppointmentVC()
        }
        
        if navigationController.viewControllers.count > 0 {
            navigationController.pushViewController(homeVC, animated: true)
        } else {
            navigationController.setViewControllers([homeVC], animated: true)
        }
        
        registerPushNotifications()
    }
    
    private func registerPushNotifications(){
        
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { (granted, error) in
            guard granted else {
                return
            }
            self.getNotificationSettings()
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
    
    private func moveToBookAppointmentVC(){
        let bookAppointmentViewController = StoryboardScene.Main.bookAppointmentVC.instantiate()
        bookAppointmentViewController.title = L10n.bookAppointmentTitle
        bookAppointmentViewController.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        
        bookAppointmentViewController.goBack = {
            self.navigationController.popViewController(animated: true)
        }
        
        navigationController.pushViewController(bookAppointmentViewController, animated: true)
        BoltAnalytics.trackScreenWithName(screenName: .BookAppointment)
    }
    
    private func moveToContactReviewVC(){
        let contactReviewViewController = StoryboardScene.Main.contactReviewVC.instantiate()
        contactReviewViewController.title = L10n.contactReviewTitle
        contactReviewViewController.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        contactReviewViewController.didLoad = { [unowned self] in
            contactReviewViewController.loadStoreLocations(locations:self.loadStore())
            contactReviewViewController.setUpLocationManager()
        }
        contactReviewViewController.showStoreLocation = { [unowned self] (storeLocation) in
            self.moveToContactReviewDetailVC(storeLocation: storeLocation)
        }
        navigationController.pushViewController(contactReviewViewController, animated: true)
        BoltAnalytics.trackScreenWithName(screenName: .ContactReview)
    }

    private func moveToContactReviewDetailVC(storeLocation: StoreLocation) {
        let contactReviewDetailViewController = StoryboardScene.Main.contactReviewDetailVC.instantiate()
        contactReviewDetailViewController.title = storeLocation.title
        
        BoltAnalytics.trackEvent(category: .ContactReview, action: .LocationDetailsViewed, label: storeLocation.title)
        let emailService = EmailService(navController: navigationController)
        
        contactReviewDetailViewController.didLoad = {
            contactReviewDetailViewController.configureView(storeLocation: storeLocation)
        }
        
        contactReviewDetailViewController.hours = {
            WebsiteService.openWebsite(fromViewController: contactReviewDetailViewController, urlString: storeLocation.hoursURL)
        }
        
        contactReviewDetailViewController.phoneLocation = {
            BoltAnalytics.trackEvent(category: .ContactReview, action: .PhoneTapped, label: storeLocation.title)
            PhoneService.makeCall(fromViewController: contactReviewDetailViewController, phoneNumber: storeLocation.phone)
        }
        
        contactReviewDetailViewController.goToWebsite = {
            BoltAnalytics.trackEvent(category: .ContactReview, action: .WebsiteTapped, label: storeLocation.title)
            WebsiteService.openWebsite(fromViewController: contactReviewDetailViewController, urlString: "https://\(storeLocation.website)")
        }
        
        contactReviewDetailViewController.emailLocation = {
            BoltAnalytics.trackEvent(category: .ContactReview, action: .EmailTapped, label: storeLocation.title)

            emailService.sendEmail(toAddress: storeLocation.email, subject: L10n.locationEmailSubject, messageBody: L10n.locationEmailBody, presentVC: contactReviewDetailViewController, failureMessage: L10n.locationEmailFailureMessage)
        }
        
        contactReviewDetailViewController.reviewFacebook = {
            BoltAnalytics.trackEvent(category: .ContactReview, action: .ReviewFacebookTapped, label: storeLocation.title)
            WebsiteService.openWebsite(fromViewController: contactReviewDetailViewController, urlString: storeLocation.facebook)
        }
        
        contactReviewDetailViewController.reviewGoogle = {
            BoltAnalytics.trackEvent(category: .ContactReview, action: .ReviewGoogleTapped, label: storeLocation.title)
            WebsiteService.openWebsite(fromViewController: contactReviewDetailViewController, urlString: storeLocation.google)
        }
        
        //The client changed their mind on this so the button has been removed from storyboard. Leave the code here in case they decide they want it in the future.
        contactReviewDetailViewController.getDirections = {
            let storePlacemark = MKPlacemark(coordinate: storeLocation.coordinate)
            let storeMapItem = MKMapItem(placemark: storePlacemark)
            storeMapItem.name = storeLocation.title
            let launchOptions = [MKLaunchOptionsDirectionsModeKey:MKLaunchOptionsDirectionsModeDefault]
            storeMapItem.openInMaps(launchOptions: launchOptions)
        }
        
        navigationController.pushViewController(contactReviewDetailViewController, animated: true)
    }

    private func loadStore() -> [StoreLocation] {
        if let path = Bundle.main.path(forResource: Constants.Location.filename, ofType: "plist") {
            let arrayRoot = NSArray(contentsOfFile: path)
            if let array = arrayRoot as? [Dictionary<String, Any>] {
                var storeLocations = [StoreLocation]()
                for item in array {
                    let storeLocation = StoreLocation(data: item)
                    storeLocations.append(storeLocation)
                }
                return storeLocations
            } else {
                print("can not load file")
            }
        } else {
            print("no file find")
        }
        
        return [StoreLocation]()
    }

    private func moveToAskExpertVC(){
        let askExpertVC = StoryboardScene.Main.askExpertVC.instantiate()
        
        askExpertVC.title = L10n.askExpertTitle
        askExpertVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        
        askExpertVC.loctionSelected = { location in
            self.moveToAskLocation(location: location)
        }
        
        navigationController.pushViewController(askExpertVC, animated: true)
    }
    
    private func moveToAskLocation(location:Location){
        let askLocationVC = StoryboardScene.Main.askLocationVC.instantiate()
        let enclosingNav = UINavigationController(rootViewController: askLocationVC)
        enclosingNav.modalPresentationStyle = .fullScreen
        let emailService = EmailService(navController: enclosingNav)
        
        switch location {
        case .circle:
            askLocationVC.title = L10n.circleDriveTitle
        case .eightStreet:
            askLocationVC.title = L10n.eightStreetTitle
        case .attridge:
            askLocationVC.title = L10n.attridgeTitle
        case .rosewood:
            askLocationVC.title = L10n.rosewoodTitle
        }
        
        askLocationVC.emailLocation = {
            BoltAnalytics.trackEvent(category: .AskExpert, action: .EmailTapped, label: location.rawValue)
            switch location {
            case .circle:
                emailService.sendEmail(toAddress: Constants.AskExpert.CircleEmail, subject: L10n.emailSubject, messageBody: L10n.emailBody, presentVC: askLocationVC, failureMessage: L10n.emailFailureMessage)
            case .eightStreet:
                emailService.sendEmail(toAddress: Constants.AskExpert.EightStreetEmail, subject: L10n.emailSubject, messageBody: L10n.emailBody, presentVC: askLocationVC, failureMessage: L10n.emailFailureMessage)
            case .attridge:
                emailService.sendEmail(toAddress: Constants.AskExpert.AttridgeEmail, subject: L10n.emailSubject, messageBody: L10n.emailBody, presentVC: askLocationVC, failureMessage: L10n.emailFailureMessage)
            case .rosewood:
                emailService.sendEmail(toAddress: Constants.AskExpert.RosewoodEmail, subject: L10n.emailSubject, messageBody: L10n.emailBody, presentVC: askLocationVC, failureMessage: L10n.emailFailureMessage)
            }
        }
        
        askLocationVC.phoneLocation = {
            BoltAnalytics.trackEvent(category: .AskExpert, action: .PhoneTapped, label: location.rawValue)
            switch location {
            case .circle:
                PhoneService.makeCall(fromViewController: askLocationVC, phoneNumber: Constants.AskExpert.CirclePhoneNumber)
            case .eightStreet:
                PhoneService.makeCall(fromViewController: askLocationVC, phoneNumber: Constants.AskExpert.EightStreetPhoneNumber)
            case .attridge:
                PhoneService.makeCall(fromViewController: askLocationVC, phoneNumber: Constants.AskExpert.AttridgePhoneNumber)
            case .rosewood:
                PhoneService.makeCall(fromViewController: askLocationVC, phoneNumber: Constants.AskExpert.RosewoodPhoneNumber)
            }
        }
        
        navigationController.present(enclosingNav, animated: true, completion: nil)
    }
    
    private func moveToDeviceUpgradeVC(){
        let deviceUpgradeVC = StoryboardScene.Main.deviceUpgradeVC.instantiate()
        deviceUpgradeVC.title = L10n.deviceUpgradeTitle
        deviceUpgradeVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        
        deviceUpgradeVC.checkForUpgrade = {
            BoltAnalytics.trackEvent(category: .DeviceUpgrade, action: .UpgradeMessageTapped, label: nil)
            self.messageService.sendMessage(toPhoneNumberString: Constants.DeviceUpgrade.UpgradeNumber, messageBody: L10n.upgradeMessageBody, presentVC: deviceUpgradeVC)
        }
        
        deviceUpgradeVC.browsePhones = {
            WebsiteService.openWebsite(fromViewController: deviceUpgradeVC, urlString: Constants.DeviceUpgrade.BrowsePhonesURLString)
        }
        
        deviceUpgradeVC.shopAccessories = {
            WebsiteService.openWebsite(fromViewController: deviceUpgradeVC, urlString: Constants.DeviceUpgrade.ShopAccessoriesURLString)
        }
        
        self.deviceUpgradeVC = deviceUpgradeVC
        navigationController.pushViewController(deviceUpgradeVC, animated: true)
    }
    
    private func moveToCouponsVC(){
        let couponsVC = StoryboardScene.Main.couponsVC.instantiate()
        couponsVC.title = L10n.couponsTitle
        couponsVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        let couponsDataProvider = CouponsDataProvider()
        var internalCoupons:Coupons? = nil
        
        couponsVC.willAppear = {
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.ActivityIndicator.activityData)
            couponsDataProvider.getCoupons { (result) in
                NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                switch result {
                case let .success(coupons):
                    internalCoupons = coupons
                    couponsVC.coupons = internalCoupons
                    couponsVC.reloadTableView()
                case let .failure(error):
                    UIAlertController.showAlert(title: nil, message: error.localizedDescription, inViewController: couponsVC)
                }
            }
        }
        
        couponsVC.saveCouponImageAtIndex = { index, image in
            internalCoupons?.allCoupons[index].couponImage = image
        }
        
        couponsVC.getCouponAtIndex = { couponIndex in
            //From the yesAction in the code commented above
            BoltAnalytics.trackEvent(category: .Coupons, action: .IndividualCouponTapped, label:nil)
            if internalCoupons?.allCoupons[couponIndex].couponImage != nil {
                if let coupon = internalCoupons?.allCoupons[couponIndex] {
                    self.moveToCouponDetailVC(coupon:coupon)
                }
            } else {
                UIAlertController.showAlert(title: nil, message: L10n.couponErrorMessage, inViewController: couponsVC)
            }
        }
        
        navigationController.pushViewController(couponsVC, animated: true)
        BoltAnalytics.trackScreenWithName(screenName: .Coupons)
    }
    
    private func moveToCouponDetailVC(coupon:Coupon) {
        let couponDetailVC = StoryboardScene.Main.couponDetailVC.instantiate()
        couponDetailVC.title = L10n.couponDetailTitle
        couponDetailVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        couponDetailVC.coupon = coupon
        
        couponDetailVC.redeemCoupon = {
            if let couponID = coupon.couponID {
                let alertController = UIAlertController(title: L10n.couponOneTimeUseTitle, message: L10n.couponOneTimeUseDescription, preferredStyle: .alert)
                let noAction = UIAlertAction(title: L10n.alertActionNoButtonTitle, style: .cancel, handler: nil)
                let yesAction = UIAlertAction(title: L10n.alertActionYesButtonTitle, style: .default, handler: { (_) in
                    let keychain = Keychain(service: Constants.Keychain.Service)
                    keychain.useCoupon(id: couponID)
                    self.navigationController.popViewController(animated: true)
                })
                alertController.addAction(noAction)
                alertController.addAction(yesAction)
                couponDetailVC.present(alertController, animated: true, completion: nil)
            } else {
                self.navigationController.popViewController(animated: true)
            }
        }
        navigationController.pushViewController(couponDetailVC, animated: true)
    }
}

extension MainCoordinator:UINavigationControllerDelegate{
    func navigationController(_ navigationController: UINavigationController, willShow viewController: UIViewController, animated: Bool) {
        if let bookAppointmentViewController = viewController as? BookAppointmentViewController {
            bookAppointmentViewController.loadBookingWebpage()
        }
    }
}
