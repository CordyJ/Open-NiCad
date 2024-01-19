//
//  SignUpViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import SnapKit
import FBSDKLoginKit


enum FacebookPermissions: String {
	case email = "email"
	case publicProfile = "public_profile"
	case userFriends = "user_friends"
}

struct SignUpInfo {
    let first: String
    let last: String
    let email: String
    let password: String
}

let MAX_CHARACTER_LENGTH = 30

class SignUpViewController: UITableViewController, UITextFieldDelegate {
	
	var facebookLogin:((String, String)->())?
    var showTermsAndConds:(()->())?
    var signUp:((SignUpInfo)->())?
	
	@IBOutlet fileprivate var facebookSignInContainerView: UIView?
    @IBOutlet fileprivate var firstnameTextfield: UITextField?
    @IBOutlet fileprivate var lastnameTextfield: UITextField?
    @IBOutlet fileprivate var emailTextfield: UITextField?
    @IBOutlet fileprivate var passwordTextfield: UITextField?
    @IBOutlet fileprivate var retypePasswordTextfield: UITextField?

    override func viewDidLoad() {
        super.viewDidLoad()

		title = L10n.signUpTitle
		
		NotificationCenter.default.addObserver(forName: Notification.Name.AccessTokenDidChange, object: nil, queue: nil) { (_) in
			if let currentAccessToken = AccessToken.current {
				self.facebookLogin?(currentAccessToken.userID, currentAccessToken.tokenString)
			}
		}
		
		let facebookLoginButton = FBLoginButton()
		facebookLoginButton.permissions = [FacebookPermissions.email.rawValue, FacebookPermissions.publicProfile.rawValue, FacebookPermissions.userFriends.rawValue]
		facebookSignInContainerView?.addSubview(facebookLoginButton)
		facebookLoginButton.snp.makeConstraints { (make) in
			make.edges.equalToSuperview()
		}
    }
	
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.CreateAccount, className: String(describing: self))
    }
	
    @IBAction fileprivate func termsAndCondsTapped() {
        showTermsAndConds?()
    }
    
    @IBAction fileprivate func signupTapped(_ sender: UIButton) {
        guard let firstname = firstnameTextfield?.text, !firstname.isEmpty else {
            UIAlertController.showAlert(L10n.missingInfo, message: L10n.firstNameMissing, inViewController: self)
            return
        }
        guard let lastname = lastnameTextfield?.text, !lastname.isEmpty else {
            UIAlertController.showAlert(L10n.missingInfo, message: L10n.lastNameMissing, inViewController: self)
            return
        }
        
        if firstname.count > MAX_CHARACTER_LENGTH || lastname.count > MAX_CHARACTER_LENGTH {
            UIAlertController.showAlert(L10n.missingInfo, message: L10n.nameTooLong, inViewController: self)
            return
        }
        
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
        guard let retypePassword = retypePasswordTextfield?.text, password == retypePassword else {
            UIAlertController.showAlert(L10n.validation, message: L10n.passwordInvalid, inViewController: self)
            return
        }
        
        signUp?(SignUpInfo(first: firstname, last: lastname, email: email, password: password))
    }
    
    func clearAllTextfields() {
        self.firstnameTextfield?.text = ""
        self.lastnameTextfield?.text = ""
        self.emailTextfield?.text = ""
        self.passwordTextfield?.text = ""
        self.retypePasswordTextfield?.text = ""
    }
    
    func textField(_ textField: UITextField, shouldChangeCharactersIn range: NSRange, replacementString string: String) -> Bool {
        guard let textFieldText = textField.text,
            let rangeOfTextToReplace = Range(range, in: textFieldText) else {
                return false
        }
        let substringToReplace = textFieldText[rangeOfTextToReplace]
        let count = textFieldText.count - substringToReplace.count + string.count
		
        return count <= 30
    }
}


extension UITextField {
	
    @IBInspectable var placeHolderColor: UIColor? {
        get {
            return self.placeHolderColor
        }
        set {
			self.attributedPlaceholder = NSAttributedString(string:self.placeholder != nil ? self.placeholder! : "", attributes:[NSAttributedString.Key.foregroundColor: newValue!])
        }
    }
}
