//
//  HomeViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-18.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class HomeViewController: UIViewController {
    
    var myReferrals:(()->())?
    var coupons:(()->())?
    var contactReview:(()->())?
    var askExpert:(()->())?
    var deviceUpgrade:(()->())?
    var bookAppointment:(()->())?
    
    override var preferredStatusBarStyle: UIStatusBarStyle {
        return .lightContent
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        navigationController?.setNavigationBarHidden(true, animated: true)
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        navigationController?.setNavigationBarHidden(false, animated: false)
    }
    
    @IBAction private func myReferralsTapped(_ sender:UIButton?){
        myReferrals?()
    }
    
    @IBAction private func couponsTapped(_ sender:UIButton?){
        coupons?()
    }
    
    @IBAction private func contactReviewTapped(_ sender:UIButton?){
        contactReview?()
    }
    
    @IBAction private func askExpertTapped(_ sender:UIButton?){
        askExpert?()
    }
    
    @IBAction private func deviceUpgradeTapped(_ sender:UIButton?){
        deviceUpgrade?()
    }
    
    @IBAction private func bookAppointmentTapped(_ sender:UIButton?){
        bookAppointment?()
    }

}
