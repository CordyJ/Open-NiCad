//
//  WelcomeViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import FBSDKLoginKit

enum OnboardingState {
    case Welcome
    case Login
    case ForgotPassword
}

class WelcomeViewController: UIViewController {

    @IBOutlet fileprivate var createAccountButton: UIButton?
    @IBOutlet fileprivate var actionButton: UIButton?
    @IBOutlet fileprivate var exitButton: UIButton?
    @IBOutlet fileprivate var loginStackView: UIStackView?
    @IBOutlet fileprivate var facebookContainerView: UIView!

    @IBOutlet fileprivate var welcomeContraint: NSLayoutConstraint?
    @IBOutlet fileprivate var loginContraint: NSLayoutConstraint?
    @IBOutlet fileprivate var forgotPasswordContraint: NSLayoutConstraint?
    @IBOutlet fileprivate var createAccountCenterContraint: NSLayoutConstraint?
    @IBOutlet fileprivate var loginStackViewCenterContraint: NSLayoutConstraint?
    @IBOutlet fileprivate var showFBContraint: NSLayoutConstraint?
    @IBOutlet fileprivate var logoToForgotPasswordContraint: NSLayoutConstraint?
    
    @IBOutlet fileprivate var emailTextfield: UITextField?
    @IBOutlet fileprivate var passwordTextfield: UITextField?
    
    @IBOutlet fileprivate var forgotPasswordLabel: UILabel?

    fileprivate var onboardingState = OnboardingState.Welcome

	let animationOptions: UIView.AnimationOptions = .curveEaseIn
    var createAccount: (()->())?
    var login: ((String, String)->())?
    var submitForgotPassword: ((String)->())?
    var facebookLogin:((String, String)->())?
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        self.navigationController?.setNavigationBarHidden(true, animated: true)
    }

    override func viewDidLoad() {
        super.viewDidLoad()
		
		NotificationCenter.default.addObserver(forName: Notification.Name.AccessTokenDidChange, object: nil, queue: nil) { (_) in
            if let currentAccessToken = AccessToken.current {
                self.facebookLogin?(currentAccessToken.userID, currentAccessToken.tokenString)
            }
        }
        
		let facebookLoginButton = FBLoginButton()
        facebookLoginButton.permissions = [FacebookPermissions.email.rawValue, FacebookPermissions.publicProfile.rawValue, FacebookPermissions.userFriends.rawValue]
        facebookContainerView?.addSubview(facebookLoginButton)
        facebookLoginButton.snp.makeConstraints { (make) in
            make.edges.equalToSuperview()
        }

        
        self.createAccountButton?.backgroundColor = UIColor(named: .rePerformanceBlue)
        self.actionButton?.backgroundColor = UIColor(named: .rePerformanceYellow)

        // setup For Welcome State by default
        self.onboardingState = .Welcome
        self.exitButton?.alpha = 0
        self.forgotPasswordLabel?.alpha = 0
        self.facebookContainerView.isHidden = true
        self.showFBContraint?.isActive = false
        self.loginStackViewCenterContraint?.constant += self.view.bounds.width
        self.view.layoutIfNeeded()
    }
    
    override var preferredStatusBarStyle: UIStatusBarStyle {
        return .lightContent
    }
    
    @IBAction fileprivate func viewCreateAccount(_ sender: UIButton) {
        createAccount?()
    }

    @IBAction fileprivate func showLogin(_ sender: UIButton) {
        switch self.onboardingState {
        case .Welcome:
            presentLoginLayoutFromWelcome()
        case .Login:
            loginTapped()
        case .ForgotPassword:
            submitTapped()
        }
    }
    
    @IBAction fileprivate func backToWelcome(_ sender: UIButton) {
        switch self.onboardingState {
        case .Welcome:
            break
        case .Login:
            presentWelcomeLayout()
        case .ForgotPassword:
            presentLoginLayoutFromForgotPassword()
        }
    }
    
    @IBAction fileprivate func forgotPassword() {
        showForgottenPassword()
    }
    
    func clearUsernameAndPassword(){
        emailTextfield?.text = ""
        passwordTextfield?.text = ""
    }
    
    fileprivate func loginTapped() {
        guard let email = emailTextfield?.text, !email.isEmpty else {
            UIAlertController.showAlert(L10n.missingInfo, message: L10n.emailMissing, inViewController: self)
            return
        }
        guard isValidEmail(email: email) else {
            UIAlertController.showAlert(L10n.validation, message: L10n.emailInvalid, inViewController: self)
            return
        }
        guard let password = passwordTextfield?.text, !password.isEmpty else {
            UIAlertController.showAlert(L10n.missingInfo, message: L10n.passwordMissing, inViewController: self)
            return
        }
        
        login?(email, password)
    }
    
    fileprivate func submitTapped() {
        guard let email = emailTextfield?.text, !email.isEmpty else {
            UIAlertController.showAlert(L10n.missingInfo, message: L10n.emailMissing, inViewController: self)
            return
        }
        guard isValidEmail(email: email) else {
            UIAlertController.showAlert(L10n.validation, message: L10n.emailInvalid, inViewController: self)
            return
        }

        submitForgotPassword?(email)
    }
    
    func presentWelcomeLayout() {
        self.onboardingState = .Welcome

        self.actionButton?.setTitle("Login", for: .normal)

        UIView.animate(withDuration: 0.4, delay: 0, options: animationOptions, animations: {
            self.loginStackViewCenterContraint?.constant += self.view.bounds.width
            self.view.layoutIfNeeded()
        }) {(success) in
            UIView.animate(withDuration: 0.2, delay: 0, options: self.animationOptions, animations: {
                self.createAccountCenterContraint?.constant = 0
                self.loginContraint?.isActive = false
                self.welcomeContraint?.isActive = true
                self.forgotPasswordContraint?.isActive = false

                self.showFBContraint?.isActive = false

                self.exitButton?.alpha = 0
                self.forgotPasswordLabel?.alpha = 0
                self.facebookContainerView.isHidden = true

                self.view.layoutIfNeeded()
            })
        }
    }
    
    fileprivate func presentLoginLayoutFromWelcome() {
        REPAnalytics.trackScreenWithName(screenName: ScreenName.Login, className: String(describing: self))
        
        self.onboardingState = .Login

        self.passwordTextfield?.alpha = 1
        
        UIView.animate(withDuration: 0.2, delay: 0, options: animationOptions, animations: {
            self.welcomeContraint?.isActive = false
            self.loginContraint?.isActive = true
            self.forgotPasswordContraint?.isActive = false

            self.showFBContraint?.isActive = true
            self.createAccountCenterContraint?.constant -= self.view.bounds.width
            
            self.view.layoutIfNeeded()
        }) {(success) in
            UIView.animate(withDuration: 0.4, delay: 0, options: self.animationOptions, animations: {
                self.loginStackViewCenterContraint?.constant = 0
                self.view.layoutIfNeeded()
                
                self.exitButton?.alpha = 1
                self.forgotPasswordLabel?.alpha = 1
                self.facebookContainerView.isHidden = false
            })
        }
    }
    
    fileprivate func showForgottenPassword() {
        self.onboardingState = .ForgotPassword
        
        self.actionButton?.setTitle("Submit", for: .normal)
		self.view.bringSubviewToFront(self.actionButton!)

        UIView.animate(withDuration: 0.4, delay: 0, options: animationOptions, animations: {
            self.welcomeContraint?.isActive = false
            self.loginContraint?.isActive = false
            self.forgotPasswordContraint?.isActive = true

            self.showFBContraint?.isActive = false
            
            self.view.layoutIfNeeded()

            self.passwordTextfield?.alpha = 0
            self.forgotPasswordLabel?.alpha = 0
            self.facebookContainerView.isHidden = true
            self.logoToForgotPasswordContraint?.constant = 100
        })
    }

    fileprivate func presentLoginLayoutFromForgotPassword() {
        REPAnalytics.trackScreenWithName(screenName: ScreenName.Login, className: String(describing: self))
        self.onboardingState = .Login
        
        self.actionButton?.setTitle("Login", for: .normal)

        UIView.animate(withDuration: 0.4, delay: 0, options: animationOptions, animations: {
            self.welcomeContraint?.isActive = false
            self.loginContraint?.isActive = true
            self.forgotPasswordContraint?.isActive = false
            self.showFBContraint?.isActive = true
            self.logoToForgotPasswordContraint?.constant = 20
            
            self.view.layoutIfNeeded()
            
            self.passwordTextfield?.alpha = 1
            self.forgotPasswordLabel?.alpha = 1
            self.facebookContainerView.isHidden = false
        })
    }
}
