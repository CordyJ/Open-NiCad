//
//  OnboardingCoordinator.swift
//
//  Created by Alan Yeung on 2017-04-25.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya
import NVActivityIndicatorView

protocol OnboardingHandler {
    func userHasLoggedIn(token: String, userID:String, userLastName:String, userFirstName:String, userFacebookID:String?)
    func userHasViewLifestyleTutorial()
}

class OnboardingCoordinator {

    let onboardingNavigationController: UINavigationController
    let onboardingDataProvider: OnboardingDataProvider
    let welcomeViewController = StoryboardScene.Onboarding.initialScene.instantiate()
    let signUpViewController = StoryboardScene.Onboarding.signUpVC.instantiate()

    var onboardingHandler: OnboardingHandler?
    
    init(navigationController: UINavigationController, dataProvider: OnboardingDataProvider) {
        self.onboardingNavigationController = navigationController
        self.onboardingDataProvider = dataProvider

        setupWelcomeViewController()
        setupSignUpViewController()
        setupFacebookLogin()
    }

    fileprivate func setupWelcomeViewController() {
        welcomeViewController.login = { (email, password) in
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
            self.onboardingDataProvider.login(email: email, password: password, completion: { (loginData, errorMsg) in
                NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                if let loginData = loginData {
                    self.onboardingHandler?.userHasLoggedIn(token: loginData.token, userID: loginData.userID, userLastName: loginData.lastName, userFirstName: loginData.firstName, userFacebookID: nil)
                }
                else {
                    let errorMsg = errorMsg ?? L10n.unknownErrorMessage
                    UIAlertController.showAlert("Login", message: errorMsg, inViewController: self.welcomeViewController)
                }
            })
        }
        
        welcomeViewController.createAccount = {
            self.onboardingNavigationController.setNavigationBarHidden(false, animated: false)
            self.onboardingNavigationController.pushViewController(self.signUpViewController, animated: true)
        }
        
        welcomeViewController.submitForgotPassword = { email in
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(ActivityData())
            self.onboardingDataProvider.forgotPassword(email: email, completion: { (success, errorMsg) in
                NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                if success {
                    let alertController = UIAlertController(title: "Forgot password", message: "An email has been sent with a link to reset your password", preferredStyle: .alert)
                    let ok = UIAlertAction(title: "OK", style: .default, handler: { alertAction in
                        self.start()
                    })
                    alertController.addAction(ok)
                    self.welcomeViewController.present(alertController, animated: true, completion: nil)
                }
                else {
                    let errorMsg = errorMsg ?? L10n.unknownErrorMessage
                    UIAlertController.showAlert("Forgot password", message: errorMsg, inViewController: self.welcomeViewController)
                }
            })
        }
    }

    fileprivate func setupSignUpViewController() {
        signUpViewController.showTermsAndConds = {
            let termsAndCondsViewController = StoryboardScene.Onboarding.termsAndCondVC.instantiate()
            termsAndCondsViewController.dismiss = {
                termsAndCondsViewController.dismiss(animated: true, completion: nil)
            }
            self.onboardingNavigationController.present(termsAndCondsViewController, animated: true, completion: nil)
        }
        
        signUpViewController.signUp = { signupInfo in
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
            self.onboardingDataProvider.createAccount(first: signupInfo.first, last: signupInfo.last, email: signupInfo.email, password: signupInfo.password, completion: { (success, errorMessage) in
                NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                if success{
                    UserDefaults.standard.userLastName = signupInfo.last
                    UserDefaults.standard.userFirstName = signupInfo.first
                    let alertController = UIAlertController(title: "Sign up", message: L10n.accountActivationMessage, preferredStyle: .alert)
                    let ok = UIAlertAction(title: "OK", style: .default, handler: { alertAction in
                        self.signUpViewController.clearAllTextfields()
                        self.start()
                    })
                    alertController.addAction(ok)
                    self.signUpViewController.present(alertController, animated: true, completion: nil)
                }
                else {
                    let errorMessage = errorMessage ?? L10n.unknownErrorMessage
                    UIAlertController.showAlert("Sign up", message: errorMessage, inViewController: self.signUpViewController)
                }
            })
        }
    }

    fileprivate func setupFacebookLogin() {
        let facebookLogin:((String, String) ->() ) = { (userID, token) in
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
            self.onboardingDataProvider.signInWithFacebook(userID: userID, token: token, completion: { (loginData, errorMsg) in
                NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                if let loginData = loginData {
                    self.onboardingHandler?.userHasLoggedIn(token: loginData.token, userID: loginData.userID, userLastName: loginData.lastName, userFirstName: loginData.firstName, userFacebookID: userID)
                }
                else {
                    let errorMsg = errorMsg ?? L10n.unknownErrorMessage
                    UIAlertController.showAlert("Login", message: errorMsg, inViewController: self.signUpViewController)
                }
            })
        }
        welcomeViewController.facebookLogin = facebookLogin
        signUpViewController.facebookLogin = facebookLogin
    }

    
    func start () {
        welcomeViewController.presentWelcomeLayout()
        self.onboardingNavigationController.setViewControllers([welcomeViewController], animated: false)
    }
    
    func startLifeCategories() {
        let lifestyleTutorialController = StoryboardScene.Onboarding.lifestyleTutorialVC.instantiate()
        let lifestyleController = StoryboardScene.Onboarding.lifestyleVC.instantiate()
        
        lifestyleTutorialController.selectedLifestyleType = { lifestyleType in
            var lifestyle: Lifestyle?
            switch lifestyleType {
            case .Action:
                lifestyle = Lifestyle(title: L10n.lifestyleActionTitle, detail: L10n.lifestyleActionDetail, backgroundImage: Asset.Assets.LifestyleTutorial.lifestyleActionBG.image)
                
            case .Fit:
                lifestyle = Lifestyle(title: L10n.lifestyleFitTitle, detail: L10n.lifestyleFitDetail, backgroundImage: Asset.Assets.LifestyleTutorial.lifestyleFitBG.image)
                
            case .Athlete:
                lifestyle = Lifestyle(title: L10n.lifestyleAthleteTitle, detail: L10n.lifestyleAthleteDetail, backgroundImage: Asset.Assets.LifestyleTutorial.lifestyleAthleteBG.image)
                
            case .Elite:
                lifestyle = Lifestyle(title: L10n.lifestyleEliteTitle, detail: L10n.lifestyleEliteDetail, backgroundImage: Asset.Assets.LifestyleTutorial.lifestyleEliteBG.image)
            }
            
            lifestyleController.lifestyle = lifestyle
            
            let navigationController = UINavigationController(rootViewController: lifestyleController)
            navigationController.setNavigationBarHidden(true, animated: false)
            lifestyleTutorialController.present(navigationController, animated: true, completion: nil)
        }
        
        lifestyleController.exit = {
            lifestyleTutorialController.dismiss(animated: true, completion: nil)
        }
        
        lifestyleTutorialController.exit = {
            self.onboardingHandler?.userHasViewLifestyleTutorial()
        }

        self.onboardingNavigationController.setNavigationBarHidden(false, animated: false)
        self.onboardingNavigationController.setViewControllers([lifestyleTutorialController], animated: false)
    }
}
