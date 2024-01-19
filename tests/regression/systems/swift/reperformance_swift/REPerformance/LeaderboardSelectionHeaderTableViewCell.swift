//
//  LeaderboardSelectionSectionTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-29.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class LeaderboardSelectionHeaderTableViewCell: UITableViewCell {
    
    @IBOutlet private var exerciseCategoryLabel:UILabel?
    @IBOutlet private var exerciseCategoryImageView:UIImageView?

    override func awakeFromNib() {
        super.awakeFromNib()
        exerciseCategoryLabel?.textColor = UIColor.white
    }
    
    func configureCell(exerciseCategoryText:String, exerciseCategoryImage:UIImage){
        exerciseCategoryLabel?.text = exerciseCategoryText
        exerciseCategoryImageView?.image = exerciseCategoryImage
    }

}
