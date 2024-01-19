//
//  ReferralsCoordinator.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import NVActivityIndicatorView

enum ViewDisplayType {
    case Push
    case Present
}

class ReferralsCoordinator {
    
    let navigationController:UINavigationController
    let dataProvider:ReferralsDataProvider
    let messageService:MessageService
    
    init(navController:UINavigationController) {
        navigationController = navController
        dataProvider = ReferralsDataProvider()
        messageService = MessageService(navController: navigationController, type: .referral)
    }
    
    func start(){
        if let seenReferralsInformation = UserDefaults.hasSeenReferralsInstructions, seenReferralsInformation {
            moveToReferralsVC()
        } else {
            moveToReferralsInformationVC(viewData: ReferralsInformationViewControllerViewData(presentationStyle: .push))
        }
    }

    func moveToReferralsInformationVC(viewData:ReferralsInformationViewControllerViewData){
        let referralsInformationVC = StoryboardScene.Referrals.referralsInformationVC.instantiate()
        referralsInformationVC.title = L10n.referralInformationTitle
        referralsInformationVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        
        referralsInformationVC.viewData = viewData
        
        referralsInformationVC.getStarted = {
            self.moveToReferralsContactVC(viewType: .UserInfoPush)
        }
        
        referralsInformationVC.dismiss = {
            referralsInformationVC.dismiss(animated: true, completion: nil)
        }
        
        switch  viewData.presentationStyle {
        case .push:
            navigationController.pushViewController(referralsInformationVC, animated: true)
        case .present:
            let enclosingNav = UINavigationController(rootViewController: referralsInformationVC)
            navigationController.present(enclosingNav, animated: true, completion: nil)
        }
    }
    
    func moveToReferralsVC(){
        let referralsVC = StoryboardScene.Referrals.referralsVC.instantiate()
        referralsVC.title = L10n.referralRedeemTitle
        referralsVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        
        NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.ActivityIndicator.activityData)
        referralsVC.didAppear = {
            if let phoneNumber = UserDefaults.userPhoneNumber {
                
                self.dataProvider.getBalance(phoneNumber: phoneNumber, completion: { (result) in
                    NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                    switch result {
                    case let .success(balance):
                        referralsVC.setBalance(balance: "$\(balance)")
                    case let .failure(error):
                        switch error {
                        case .invalidUser:
                            self.kickUser(message: error.localizedDescription, vcToPresentOn: referralsVC)
                        default:
                            UIAlertController.showAlert(title: nil, message: error.localizedDescription, inViewController: referralsVC)
                        }
                    }
                })
            }
        }

        referralsVC.viewInfo = {
             self.moveToReferralsInformationVC(viewData: ReferralsInformationViewControllerViewData(presentationStyle: .present))
        }
        
        referralsVC.newReferral = {
            self.moveToReferralsContactVC(viewType: .ReferralInfo)
        }
        
        referralsVC.redeem = {
            BoltAnalytics.trackEvent(category: .Referrals, action: .RedeemBoltBucksTapped, label:nil)

            if let userPhoneNumber = UserDefaults.userPhoneNumber, let userEmail = UserDefaults.userEmail {
                NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.ActivityIndicator.activityData)
                
                self.dataProvider.redeem(userPhoneNumber: userPhoneNumber, userEmail: userEmail, completion: { (result) in
                    NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                    switch result {
                    case let .success(redeemCode):
                        self.moveToRedeemCodeViewController(code: redeemCode)
                    case let .failure(error):
                        switch error {
                        case .invalidUser:
                            self.kickUser(message: error.localizedDescription, vcToPresentOn: referralsVC)
                        default:
                            UIAlertController.showAlert(title: nil, message: error.localizedDescription, inViewController: referralsVC)
                        }
                    }
                })
            } else {
                UIAlertController.showAlert(title: nil, message: L10n.referralErrorMessage, inViewController: referralsVC)
            }
        }
        
        referralsVC.editInfo = {
            self.moveToReferralsContactVC(viewType: .UserInfoPresent)
        }
        
        //Pop to ReferralsVC so that ReferralsContactVC and ReferralsInformationVC are no longer in the list of view controllers if they were (they would be if this is the first time viewing referrals).
        for index in navigationController.viewControllers.indices {
            if navigationController.viewControllers[index] is HomeViewController {
                navigationController.popToViewController(navigationController.viewControllers[index], animated: false)
                break
            }
        }
        navigationController.pushViewController(referralsVC, animated: true)
    }
    
    func moveToRedeemCodeViewController(code:String){
        let redeemCodeViewController = StoryboardScene.Referrals.redeemCodeVC.instantiate()
        redeemCodeViewController.code = code
        
        let enclosingNav = UINavigationController(rootViewController: redeemCodeViewController)
        enclosingNav.navigationBar.barTintColor = UIColor(named: .boltMobileDarkBlue)
        enclosingNav.navigationBar.tintColor = UIColor.white
        navigationController.present(enclosingNav, animated: true, completion: nil)
    }
    
    func moveToReferralsContactVC(viewType:ReferralsContactViewType) {
        let referralsContactVC = StoryboardScene.Referrals.referralsContactVC.instantiate()
        referralsContactVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        referralsContactVC.viewType = viewType
        let enclosingNav = UINavigationController(rootViewController: referralsContactVC)
        
        switch viewType {
        case .UserInfoPush, .UserInfoPresent:
            referralsContactVC.title = L10n.referralsUserInformationTitle
            
            if let firstName = UserDefaults.userFirstName, let lastName = UserDefaults.userLastName, let email = UserDefaults.userEmail, let phoneNumber = UserDefaults.userPhoneNumber {
                referralsContactVC.viewData = ReferralsContactViewData(firstName: firstName, lastName: lastName, email: email, phoneNumber: phoneNumber)
            } else {
                referralsContactVC.viewData = nil
            }
            
            referralsContactVC.submitUserInfo = { firstName, lastName, email, phoneNumber in
                NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.ActivityIndicator.activityData)
                if viewType == .UserInfoPush {
                    //Login
                    self.dataProvider.login(userFirstName: firstName, userLastName: lastName, userEmail: email, userPhone: phoneNumber, completion: { (result) in
                        NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                        switch result {
                        case let .success(token):
                            UserDefaults.userToken = token
                            UserDefaults.userFirstName = firstName
                            UserDefaults.userLastName = lastName
                            UserDefaults.userEmail = email
                            UserDefaults.userPhoneNumber = phoneNumber
                            UserDefaults.hasSeenReferralsInstructions = true
                            self.moveToPhoneNumberVerificationVC(viewType: .Push, presentedNavigationController: nil)
                        case let .failure(error):
                            UIAlertController.showAlert(title: nil, message: error.localizedDescription, inViewController: referralsContactVC)
                        }
                    })
                } else if viewType == .UserInfoPresent {
                    //Update User
                    self.dataProvider.updateUser(userFirstName: firstName, userLastName: lastName, userEmail: email, userPhone: phoneNumber, completion: { (result) in
                        NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                        switch result {
                        case let .success(token):
                            UserDefaults.userToken = token
                            UserDefaults.userFirstName = firstName
                            UserDefaults.userLastName = lastName
                            UserDefaults.userEmail = email
                            UserDefaults.hasSeenReferralsInstructions = true
                            if let oldPhoneNumber = UserDefaults.userPhoneNumber, oldPhoneNumber == phoneNumber {
                                UserDefaults.userPhoneNumber = phoneNumber
                                referralsContactVC.dismiss(animated: true, completion: nil)
                            } else {
                                UserDefaults.userPhoneNumber = phoneNumber
                                self.moveToPhoneNumberVerificationVC(viewType: .Present, presentedNavigationController: enclosingNav)
                            }
                        case let .failure(error):
                            switch error {
                            case .invalidUser:
                                self.kickUser(message: error.localizedDescription, vcToPresentOn: referralsContactVC)
                            default:
                                UIAlertController.showAlert(title: nil, message: error.localizedDescription, inViewController: referralsContactVC)
                            }
                        }
                    })
                }
            }
        case .ReferralInfo:
            referralsContactVC.title = L10n.referralsTitle
            referralsContactVC.viewData = nil
            referralsContactVC.submitReferralInfo = { firstName, lastName, email, phoneNumber in
                BoltAnalytics.trackEvent(category: .Referrals, action: .SubmitReferralTapped, label:nil)

                if let userFirstName = UserDefaults.userFirstName, let userLastName = UserDefaults.userLastName, let userEmail = UserDefaults.userEmail, let userPhone = UserDefaults.userPhoneNumber {
                    NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.ActivityIndicator.activityData)

                    self.dataProvider.refer(userFirstName: userFirstName, userLastName: userLastName, userEmail: userEmail, userPhone: userPhone, referFirstName: firstName, referLastName: lastName, referEmail: email, referPhone: phoneNumber, completion: { (result) in
                        NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                        switch result {
                        case .success(let referralCode):
                            self.messageService.sendMessage(toPhoneNumberString: phoneNumber, messageBody: L10n.referralSentMessageBody(referralCode), presentVC: referralsContactVC)
                        case let .failure(error):
                            switch error {
                            case .invalidUser:
                                self.kickUser(message: error.localizedDescription, vcToPresentOn: referralsContactVC)
                            default:
                                UIAlertController.showAlert(title: nil, message: error.localizedDescription, inViewController: referralsContactVC)
                            }
                        }
                    })
                } else {
                    UIAlertController.showAlert(title: nil, message: L10n.referralErrorMessage, inViewController: referralsContactVC)
                }
            }
        }
        
        switch viewType {
        case .UserInfoPush, .ReferralInfo:
            navigationController.pushViewController(referralsContactVC, animated: true)
        case .UserInfoPresent:
            navigationController.present(enclosingNav, animated: true, completion: nil)
        }
    }
    
    func moveToPhoneNumberVerificationVC(viewType:ViewDisplayType, presentedNavigationController:UINavigationController?){
        let phoneNumberVerificationVC = StoryboardScene.Referrals.phoneNumberVerificationVC.instantiate()
        phoneNumberVerificationVC.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
        phoneNumberVerificationVC.title = L10n.verificationTitle
        
        phoneNumberVerificationVC.submitCode = { code in
            if let codeInt = Int(code) {
                NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.ActivityIndicator.activityData)
                self.dataProvider.verifyPhoneNumber(code: codeInt, completion: { (result) in
                    NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                    switch result{
                    case .success(_):
                        switch viewType {
                        case .Push:
                            self.moveToReferralsVC()
                        case .Present:
                            phoneNumberVerificationVC.dismiss(animated: true, completion: nil)
                        }
                    case let .failure(error):
                        switch error {
                        case .invalidUser:
                            self.kickUser(message: error.localizedDescription, vcToPresentOn: phoneNumberVerificationVC)
                        default:
                            UIAlertController.showAlert(title: nil, message: error.localizedDescription, inViewController: phoneNumberVerificationVC)
                        }
                    }
                })
            } else {
                UIAlertController.showAlert(title: nil, message: L10n.verificationInvalidCodeMessage, inViewController: phoneNumberVerificationVC)
            }
        }
        
        phoneNumberVerificationVC.resendCode = {
            self.dataProvider.resendCode(completion: { (result) in
                switch result {
                case .success(_):
                    UIAlertController.showAlert(title: nil, message: L10n.verificationResendCodeSuccessMessage, inViewController: phoneNumberVerificationVC)
                case let .failure(error):
                    switch error {
                    case .invalidUser:
                        self.kickUser(message: error.localizedDescription, vcToPresentOn: phoneNumberVerificationVC)
                    default:
                        UIAlertController.showAlert(title: nil, message: L10n.verificationResendCodeFailureMessage + "\n\(error.localizedDescription)", inViewController: phoneNumberVerificationVC)
                    }
                }
            })
        }
        
        switch viewType {
        case .Push:
            navigationController.pushViewController(phoneNumberVerificationVC, animated: true)
        case .Present:
            if let presentedNavigationController = presentedNavigationController {
                presentedNavigationController.pushViewController(phoneNumberVerificationVC, animated: true)
            }
        }
    }
    
    func kickUser(message:String, vcToPresentOn:UIViewController) {
        let alertController = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        let okAction = UIAlertAction(title: L10n.alertActionOkButtonTitle, style: .cancel) { (_) in
            UserDefaults.userToken = ""
            UserDefaults.userFirstName = ""
            UserDefaults.userLastName = ""
            UserDefaults.userEmail = ""
            UserDefaults.userPhoneNumber = ""
            UserDefaults.hasSeenReferralsInstructions = false
            self.navigationController.popToRootViewController(animated: true)
        }
        alertController.addAction(okAction)
        vcToPresentOn.present(alertController, animated: true, completion: nil)
    }
    
}
