//
//  EndorsementsTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-23.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class EndorsementsTableViewCell: UITableViewCell {
    
    @IBOutlet private var titleLabel:UILabel?
    @IBOutlet private var disclosureIndicator:UIImageView?

    override func awakeFromNib() {
        super.awakeFromNib()
        titleLabel?.textColor = UIColor.white
        disclosureIndicator?.image = #imageLiteral(resourceName: "OrangeDisclosureIndicatorRight")
    }
    
    func setTitleLabelWithText(_ text:String){
        titleLabel?.text = text
    }

}
