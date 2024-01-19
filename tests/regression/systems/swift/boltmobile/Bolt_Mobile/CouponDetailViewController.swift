//
//  CouponDetailViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-10-24.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class CouponDetailViewController: UIViewController {
    
    @IBOutlet private var couponImageView:UIImageView?
    @IBOutlet private var errorLabel:UILabel?
    
    var redeemCoupon:(()->())?
    
    var coupon:Coupon?
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        setUpView()
    }
    
    func setUpView(){
        if let coupon = coupon {
            couponImageView?.image = coupon.couponImage
            errorLabel?.isHidden = true
        } else {
            errorLabel?.isHidden = false
        }
    }
    
    @IBAction private func redeemCouponTapped(_ sender:UIButton?){
        redeemCoupon?()
    }

}
