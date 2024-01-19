//
//  LeaderboardErrorTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-09-29.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class LeaderboardErrorTableViewCell: UITableViewCell {
    
    @IBOutlet private var errorLabel:UILabel?

    override func awakeFromNib() {
        super.awakeFromNib()
        errorLabel?.textColor = UIColor.white
        selectionStyle = .none
    }
    
    func configureCell(errorMessage:String){
        errorLabel?.text = errorMessage
    }

}
