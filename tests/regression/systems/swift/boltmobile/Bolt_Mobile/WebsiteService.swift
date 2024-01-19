//
//  WebsiteService.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-25.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class WebsiteService {
    
    class func openWebsite(fromViewController:UIViewController, urlString:String){
        if let websiteURL = URL(string: urlString), UIApplication.shared.canOpenURL(websiteURL) {
            UIApplication.shared.open(websiteURL, options: [:], completionHandler: nil)
        } else {
            UIAlertController.showAlert(title: nil, message: L10n.unableToOpenWebsite, inViewController: fromViewController)
        }
    }
}
