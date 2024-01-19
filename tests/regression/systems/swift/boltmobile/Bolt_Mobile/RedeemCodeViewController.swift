//
//  RedeemCodeViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class RedeemCodeViewController: UIViewController {
    
    @IBOutlet private var codeLabel:UILabel?
    var code:String?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.leftBarButtonItem = UIBarButtonItem(image: Asset.xIcon.image, style: .plain, target: self, action: #selector(dismissButtonTapped(_:)))
        navigationController?.navigationBar.barStyle = .black
    }
    
    override func viewWillAppear(_ animated: Bool) {
        if let code = code {
            codeLabel?.text = code
        } else {
            codeLabel?.text = L10n.referralRedeemErrorGettingCode
        }
    }
    
    @IBAction private func dismissButtonTapped(_ sender:UIButton?){
        self.dismiss(animated: true, completion: nil)
    }

}
