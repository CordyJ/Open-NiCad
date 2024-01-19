//
//  RewardsTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-07.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class RewardsTableViewCell: UITableViewCell {
    
    @IBOutlet private var logoImageView:UIImageView?
    @IBOutlet private var discountDescriptionLabel:UILabel?
    @IBOutlet private var productDescriptionLabel:UILabel?
    @IBOutlet private var savePercentNonMembersLabel:UILabel?
    @IBOutlet private var savePercentProMembersLabel:UILabel?
    @IBOutlet private var saveDollarNonMembersLabel:UILabel?
    @IBOutlet private var saveDollarProMembersLabel:UILabel?
    
    @IBOutlet private var itemImageView:UIImageView?
    
    @IBOutlet private var getItNowView:UIView?
    @IBOutlet private var getItNowLabel:UILabel?
    

    override func awakeFromNib() {
        super.awakeFromNib()
        itemImageView?.backgroundColor = UIColor(named: .rePerformanceRewardsBlue)
        getItNowLabel?.textColor = UIColor.white
    }
    
    func configureCell(logoImage:UIImage?, discountDescription:String, productDescription:String, percentNonMembers:Int, percentProMembers:Int, dollarNonMembers:String, dollarProMembers:String, itemImage:UIImage?, rightLabelText:String, rightViewColor:UIColor){
        logoImageView?.image = logoImage
        discountDescriptionLabel?.text = discountDescription
        productDescriptionLabel?.text = productDescription
        savePercentNonMembersLabel?.text = String(format: "%d%% Off!", percentNonMembers)
        savePercentProMembersLabel?.text = String(format: "%d%% Off!", percentProMembers)
        saveDollarNonMembersLabel?.text = dollarNonMembers
        saveDollarProMembersLabel?.text = dollarProMembers
        itemImageView?.image = itemImage
        getItNowView?.backgroundColor = rightViewColor
        getItNowLabel?.text = rightLabelText
    }
}
