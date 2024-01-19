//
//  YourDealViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-09.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView

struct YourDealViewData{
    let singleRewardViewData:SingleRewardViewData
    let informationLabelText:String
}

class YourDealViewController: UIViewController {
    
    @IBOutlet private var informationLabel:UILabel?
    
    @IBOutlet private var logoImageView:UIImageView?
    @IBOutlet private var itemImageView:UIImageView?
    
    @IBOutlet private var discountDescriptionLabel:UILabel?
    @IBOutlet private var productDescriptionlabel:UILabel?
    @IBOutlet private var nonProCreditsLabel:UILabel?
    @IBOutlet private var proCreditsLabel:UILabel?
    
    @IBOutlet private var redeemButton:UIButton?
    
    var redeem:((SingleRewardViewData)->())?
    
    var viewData:YourDealViewData?
    
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
        REPAnalytics.trackScreenWithName(screenName: ScreenName.ViewRewards, className: String(describing: self))
    }

    func setUpView(){
        redeemButton?.setUpOrangeREPerformanceButton()
        informationLabel?.textColor = UIColor.white
        itemImageView?.backgroundColor = UIColor(named: .rePerformanceRewardsBlue)
    }
    
    func configureView(){
        if let viewData = viewData {
            informationLabel?.text = viewData.informationLabelText
            logoImageView?.image = viewData.singleRewardViewData.companyLogoImage
            itemImageView?.image = viewData.singleRewardViewData.itemImage
            discountDescriptionLabel?.text = viewData.singleRewardViewData.discountDescription
            productDescriptionlabel?.text = viewData.singleRewardViewData.productDescription
            nonProCreditsLabel?.text = viewData.singleRewardViewData.costNonMembers
            proCreditsLabel?.text = viewData.singleRewardViewData.costProMembers
        } else {
            informationLabel?.text = L10n.rewardsRedeemInformation
            logoImageView?.image = nil
            itemImageView?.image = nil
            discountDescriptionLabel?.text = "Error"
            productDescriptionlabel?.text = ""
            nonProCreditsLabel?.text = ""
            proCreditsLabel?.text = ""
        }
    }
    
    @IBAction private func redeemTapped(_ sender:UIButton){
        if let viewData = viewData {
            redeem?(viewData.singleRewardViewData)
        }
    }
    
    func showActivity(_ show:Bool){
        if show{
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
        } else {
            NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
        }
    }

}
