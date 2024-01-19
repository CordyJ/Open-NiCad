//
//  LeaderboardInitialViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class LeaderboardInitialViewController: UIViewController {
    
    var compareToOthers:(()->())?
    var compareWithYourGym:(()->())?

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    
    @IBAction private func compareToOthersTapped(_ sender:UIButton?){
        self.compareToOthers?()
    }
    
    @IBAction private func compareWithYourGymTapped(_ sender:UIButton?){
        self.compareWithYourGym?()
    }

}
