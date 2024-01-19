//
//  DisplayAlert.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

extension UIAlertController{
    
    class func showAlert(_ title: String?, message: String?, inViewController: UIViewController) {
        let alertController = UIAlertController(title: title, message: message, preferredStyle: .alert)
        let ok = UIAlertAction(title: "OK", style: .default, handler: nil)
        alertController.addAction(ok)
        inViewController.present(alertController, animated: true, completion: nil)
    }
}

