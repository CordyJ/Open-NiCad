//
//  RedeemViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-09.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

struct RedeemViewData{
    var logoImage:UIImage?
    let couponCode:String
    let discountDescription:String
    let productDescription:String
}

class RedeemViewController: UIViewController {
    
    @IBOutlet private var logoImageView:UIImageView?
    @IBOutlet private var couponCodeLabel:UILabel?
    
    @IBOutlet private var discountDescriptionLabel:UILabel?
    @IBOutlet private var productDescriptionLabel:UILabel?
    
    @IBOutlet private var doneButton:UIButton?
    
    var viewData:RedeemViewData?
    
    var done:(()->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        setUpView()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        configureView()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.RedeemReward, className: String(describing: self))
    }
    
    func setUpView(){
        doneButton?.setUpOrangeREPerformanceButton()
    }
    
    func configureView(){
        if let viewData = viewData {
            logoImageView?.image = viewData.logoImage
            couponCodeLabel?.text = viewData.couponCode
            discountDescriptionLabel?.text = viewData.discountDescription
            productDescriptionLabel?.text = viewData.productDescription
        } else {
            logoImageView?.image = nil
            couponCodeLabel?.text = "Error"
            discountDescriptionLabel?.text = "Error"
            productDescriptionLabel?.text = nil
        }
    }
    
    @IBAction private func doneTapped(_ sender:UIButton){
        done?()
    }
    
}
