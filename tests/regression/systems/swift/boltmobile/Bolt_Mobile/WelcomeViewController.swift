//
//  WelcomeViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-15.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class WelcomeViewController: UIViewController {
    
    var getStarted:(()->())?
    
    override var prefersStatusBarHidden: Bool {
        return true
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        navigationController?.setNavigationBarHidden(true, animated: false)
    }
    
    @IBAction private func getStartedTapped() {
        getStarted?()
    }

}
