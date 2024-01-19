//
//  CouponTableViewCell.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-22.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class CouponTableViewCell: UITableViewCell {
    
    @IBOutlet private var couponImageView:UIImageView?
    @IBOutlet private var activityIndicator:UIActivityIndicatorView?
    @IBOutlet private var errorLabel:UILabel?
    
    var getCoupon:(()->())?
    
    func configureCell(couponImage:UIImage?){
        if let couponImage = couponImage {
            couponImageView?.image = couponImage
            activityIndicator?.stopAnimating()
            errorLabel?.isHidden = true
        } else {
            activityIndicator?.stopAnimating()
            errorLabel?.isHidden = false
            couponImageView?.image = nil
        }
    }
    
    func clearCell(){
        couponImageView?.image = nil
        activityIndicator?.startAnimating()
        errorLabel?.isHidden = true
    }
    
    @IBAction private func getThisCouponTapped(_ sender:UIButton?){
        getCoupon?()
    }
}
