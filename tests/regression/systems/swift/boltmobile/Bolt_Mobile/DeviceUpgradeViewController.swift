//
//  DeviceUpgradeViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-19.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class DeviceUpgradeViewController: UIViewController {
    
    var checkForUpgrade:(()->())?
    var browsePhones:(()->())?
    var shopAccessories:(()->())?
    
    @IBAction private func checkForUpgradeTapped(){
        checkForUpgrade?()
    }
    
    @IBAction private func browsePhonesTapped(){
        browsePhones?()
    }
    
    @IBAction private func shopAccessoriesTapped(){
        shopAccessories?()
    }

}
