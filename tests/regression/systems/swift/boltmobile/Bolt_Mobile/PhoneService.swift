//
//  PhoneService.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-25.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class PhoneService {
    
    class func makeCall(fromViewController:UIViewController, phoneNumber:String) {
        if let supportNumberURL = URL(string: "tel://\(phoneNumber)"), UIApplication.shared.canOpenURL(supportNumberURL) {
            UIApplication.shared.open(supportNumberURL, options: [:], completionHandler: nil)
        } else {
            UIAlertController.showAlert(title: nil, message: L10n.callFailureMessage, inViewController: fromViewController)
        }
    }
}
