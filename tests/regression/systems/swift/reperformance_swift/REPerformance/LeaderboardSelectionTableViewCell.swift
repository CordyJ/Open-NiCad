//
//  LeaderboardSelectionTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-29.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class LeaderboardSelectionTableViewCell: UITableViewCell {
    
    @IBOutlet private var exerciseTestTypeLabel:UILabel?

    override func awakeFromNib() {
        super.awakeFromNib()
        exerciseTestTypeLabel?.textColor = UIColor.white
        selectionStyle = .none
    }
    
    func setExerciseTestTypeLabelWithText(_ text:String){
        exerciseTestTypeLabel?.text = text
    }

}
