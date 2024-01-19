//
//  AskExpertViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

enum Location:String {
    case circle
    case eightStreet
    case attridge
    case rosewood
}

class AskExpertViewController: UIViewController {
    
    var loctionSelected:((Location)->())?

    override func viewDidLoad() {
        super.viewDidLoad()
    }
    
    @IBAction private func circleTapped(_ sender:UIButton?){
        loctionSelected?(.circle)
    }
    @IBAction private func eightStreetTapped(_ sender:UIButton?){
        loctionSelected?(.eightStreet)
    }
    @IBAction private func attridgeTapped(_ sender:UIButton?){
        loctionSelected?(.attridge)
    }
    @IBAction private func rosewoodTapped(_ sender:UIButton?){
        loctionSelected?(.rosewood)
    }

}
