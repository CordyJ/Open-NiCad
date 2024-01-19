//
//  AskLocationViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-23.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class AskLocationViewController: UIViewController {
    
    var emailLocation:(()->())?
    var phoneLocation:(()->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.leftBarButtonItem = UIBarButtonItem(image: Asset.xIcon.image, style: .plain, target: self, action: #selector(dismissButtonTapped(_:)))
    }
    
    @IBAction private func dismissButtonTapped(_ sender:UIButton?){
        self.dismiss(animated: true, completion: nil)
    }
    
    @IBAction private func emailTapped(_ sender:UIButton?){
        emailLocation?()
    }
    
    @IBAction private func phoneTapped(_ sender:UIButton?){
        phoneLocation?()
    }
}
