//
//  ReferralsContactViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import IQKeyboardManagerSwift

enum ReferralsContactViewType {
    case UserInfoPush
    case UserInfoPresent
    case ReferralInfo
}

struct ReferralsContactViewData {
    
    let firstName:String
    let lastName:String
    let email:String
    let phoneNumber:String
}

class ReferralsContactViewController: UIViewController {
    
    var viewType:ReferralsContactViewType?
    var viewData:ReferralsContactViewData?
    
    var returnKeyHandler:IQKeyboardReturnKeyHandler?

    @IBOutlet private var subtitle:UILabel?
    @IBOutlet private var firstNameTextField:UITextField?
    @IBOutlet private var lastNameTextField:UITextField?
    @IBOutlet private var emailTextField:UITextField?
    @IBOutlet private var phoneNumberTextField:UITextField?
    @IBOutlet private var button: UIButton?

    var submitUserInfo:((_ firstName:String, _ lastName:String, _ email:String, _ phoneNumber:String)->())?
    var submitReferralInfo:((_ firstName:String, _ lastName:String, _ email:String?, _ phoneNumber:String)->())?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        phoneNumberTextField?.keyboardType = .numberPad
        returnKeyHandler = IQKeyboardReturnKeyHandler(controller: self)
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        setUpView()
    }
    
    deinit {
        returnKeyHandler = nil
    }
    
    @IBAction private func dismissButtonTapped(_ sender:UIButton?){
        self.dismiss(animated: true, completion: nil)
    }
    
    func setUpView() {
        guard let viewType = viewType else {
            return
        }
        switch viewType {
        case .UserInfoPresent:
            navigationItem.leftBarButtonItem = UIBarButtonItem(image: Asset.xIcon.image, style: .plain, target: self, action: #selector(dismissButtonTapped(_:)))
            setUpUserInfo()
        case .UserInfoPush:
            setUpUserInfo()
        case .ReferralInfo:
            setUpReferralsInfo()
        }
    }
    
    func setUpUserInfo(){
        subtitle?.text = L10n.yourUserInformationSubtitle
        
        firstNameTextField?.placeholder = L10n.yourFirstNamePlaceholder
        lastNameTextField?.placeholder = L10n.yourLastNamePlaceholder
        emailTextField?.placeholder = L10n.yourEmailPlaceholder
        phoneNumberTextField?.placeholder = L10n.yourPhoneNumberPlaceholder
        
        firstNameTextField?.text = viewData?.firstName ?? ""
        lastNameTextField?.text = viewData?.lastName ?? ""
        emailTextField?.text = viewData?.email ?? ""
        phoneNumberTextField?.text = viewData?.phoneNumber ?? ""
        
        button?.setTitle(L10n.yourButtonTitle, for: .normal)
    }
    
    func setUpReferralsInfo(){
        subtitle?.text = L10n.referralsSubtitle

        firstNameTextField?.placeholder = L10n.referralFirstNamePlaceholder
        lastNameTextField?.placeholder = L10n.referralLastNamePlaceholder
        emailTextField?.placeholder = L10n.referralEmailPlaceholder
        phoneNumberTextField?.placeholder = L10n.referralPhoneNumberPlaceholder
        
        firstNameTextField?.text = ""
        lastNameTextField?.text = ""
        emailTextField?.text = ""
        phoneNumberTextField?.text = ""
        
        button?.setTitle(L10n.referralButtonTitle, for: .normal)
    }
    
    @IBAction private func submitTapped(_ sender:UIButton?){
        guard let viewType = viewType else {
            return
        }
        switch viewType {
            case .UserInfoPush, .UserInfoPresent:
                validateAndSubmitUserInfo()
            case .ReferralInfo:
                validateAndSubmitReferralInfo()
        }
    }
    
    
    private func validateAndSubmitUserInfo() {
        
        guard let firstName = firstNameTextField?.text?.trimmingCharacters(in: .whitespaces), firstName.count > 0 else {
            UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidFirstName, inViewController: self)
            return
        }
        
        guard let lastName = lastNameTextField?.text?.trimmingCharacters(in: .whitespaces), lastName.count > 0 else {
            UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidLastName, inViewController: self)
            return
        }

        guard let email = emailTextField?.text?.trimmingCharacters(in: .whitespaces), email.isValidEmail() else {
            UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidEmail, inViewController: self)
            return
        }
        
        guard let phoneNumber = phoneNumberTextField?.text?.trimmingCharacters(in: .whitespaces), phoneNumber.isValidPhoneNumber() else {
            UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidPhoneNumber, inViewController: self)
            return
        }
        
        submitUserInfo?(firstName, lastName, email, phoneNumber)
    }

    private func validateAndSubmitReferralInfo() {
        
        guard let firstName = firstNameTextField?.text?.trimmingCharacters(in: .whitespaces), firstName.count > 0 else {
            UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidFirstName, inViewController: self)
            return
        }
        
        guard let lastName = lastNameTextField?.text?.trimmingCharacters(in: .whitespaces), lastName.count > 0 else {
            UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidLastName, inViewController: self)
            return
        }
        
        guard let phoneNumber = phoneNumberTextField?.text?.trimmingCharacters(in: .whitespaces), phoneNumber.isValidPhoneNumber() else {
            UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidPhoneNumber, inViewController: self)
            return
        }
        
        if let email = emailTextField?.text?.trimmingCharacters(in: .whitespaces), email.count > 0 {
            if email.isValidEmail() {
                submitReferralInfo?(firstName, lastName, email, phoneNumber)
                return
            } else {
                UIAlertController.showAlert(title: L10n.invalidEntryTitle, message: L10n.invalidEmail, inViewController: self)
                return
            }
        } else {
            submitReferralInfo?(firstName, lastName, nil, phoneNumber)
            return
        }
    }

}
