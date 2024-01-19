//
//  UIAlertController+BoltMobile.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-15.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

extension UIAlertController {
    
    class func showAlert(title: String?, message: String?, inViewController: UIViewController) {
        let alertController = UIAlertController(title: title, message: message, preferredStyle: .alert)
        let ok = UIAlertAction(title: L10n.alertActionOkButtonTitle, style: .cancel, handler: nil)
        alertController.addAction(ok)
        inViewController.present(alertController, animated: true, completion: nil)
    }
}

