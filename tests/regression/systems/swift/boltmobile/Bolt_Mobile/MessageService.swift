//
//  MessageService.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-25.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit
import MessageUI

enum TextType {
    case upgrade
    case referral
}

class MessageService:NSObject {

    let navigationController:UINavigationController
    let textType: TextType
    
    init(navController:UINavigationController, type: TextType) {
        navigationController = navController
        textType = type
    }
    
    func sendMessage(toPhoneNumberString:String, messageBody:String, presentVC:UIViewController){
        if MFMessageComposeViewController.canSendText() {
            let composeVC = MFMessageComposeViewController()
            composeVC.body = messageBody
            composeVC.recipients = [toPhoneNumberString]
            composeVC.messageComposeDelegate = self
            presentVC.present(composeVC, animated: true, completion: nil)
        } else {
            UIAlertController.showAlert(title: nil, message: L10n.textFailureMessage, inViewController: presentVC)
        }
    }
}

extension MessageService:MFMessageComposeViewControllerDelegate {
    func messageComposeViewController(_ controller: MFMessageComposeViewController, didFinishWith result: MessageComposeResult) {
        if let topViewController = navigationController.topViewController {
            controller.dismiss(animated: true, completion: {
                switch result {
                case .sent:
                    if self.textType == .upgrade {
                        UIAlertController.showAlert(title: nil, message: L10n.textSentMessage, inViewController: topViewController)
                    }
                default:
                    UIAlertController.showAlert(title: nil, message: L10n.textNotSentMessage, inViewController: topViewController)
                }
            })
        } else {
            controller.dismiss(animated: true, completion: nil)
        }
    }
}
