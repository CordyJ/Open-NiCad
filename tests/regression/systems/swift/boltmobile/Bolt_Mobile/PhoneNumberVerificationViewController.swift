//
//  PhoneNumberVerificationViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-12-12.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class PhoneNumberVerificationViewController: UIViewController {
    
    @IBOutlet private var codeTextField:UITextField?
    
    var submitCode:((String)->())?
    var resendCode:(()->())?

    override func viewDidLoad() {
        super.viewDidLoad()
    }
    
    @IBAction private func submitTapped(_ sender:UIButton?){
        if let code = codeTextField?.text {
            submitCode?(code)
        } else {
            UIAlertController.showAlert(title: nil, message: L10n.verificationInvalidCodeMessage, inViewController: self)
        }
    }
    
    @IBAction private func resendCodeTapped(_ sender:UIButton?){
        resendCode?()
    }

}
