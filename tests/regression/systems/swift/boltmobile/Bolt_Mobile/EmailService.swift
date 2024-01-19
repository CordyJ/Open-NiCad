//
//  EmailService.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-25.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import MessageUI

class EmailService:NSObject {
    
    let navigationController:UINavigationController
    
    init(navController:UINavigationController) {
        navigationController = navController
    }
    
    func sendEmail(toAddress:String, subject:String, messageBody:String, presentVC:UIViewController, failureMessage:String) {
        if MFMailComposeViewController.canSendMail() {
            let composeVC = MFMailComposeViewController()
            composeVC.mailComposeDelegate = self
            composeVC.setToRecipients([toAddress])
            composeVC.setSubject(subject)
            composeVC.setMessageBody(messageBody, isHTML: false)
            presentVC.present(composeVC, animated: true, completion: nil)
        } else {
            UIAlertController.showAlert(title: nil, message: failureMessage, inViewController: presentVC)
        }
    }
}

extension EmailService:MFMailComposeViewControllerDelegate {
    func mailComposeController(_ controller: MFMailComposeViewController, didFinishWith result: MFMailComposeResult, error: Error?) {
        if let topViewController = navigationController.topViewController {
            controller.dismiss(animated: true, completion: {
                switch result{
                case .sent:
                    UIAlertController.showAlert(title: nil, message: L10n.emailSentMessage, inViewController: topViewController)
                default:
                    UIAlertController.showAlert(title: nil, message: L10n.emailNotSendMessage, inViewController: topViewController)
                }
            })
        } else {
            controller.dismiss(animated: true, completion: nil)
        }
    }
}


