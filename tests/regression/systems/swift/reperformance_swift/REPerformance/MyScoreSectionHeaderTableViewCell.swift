//
//  MyScoreSectionHeaderTableViewCell.swift
//  REPerformance
//
//  Created by Francis Chary on 2017-05-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


class MyScoreSectionHeaderTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var headerImageView: UIImageView!
	@IBOutlet fileprivate var headerTitleLabel: UILabel!
	@IBOutlet fileprivate var scoreRepLabel: UILabel!
	
	
	func configure(with exerciseInfo: ExerciseInfo) {
		self.headerImageView.image = exerciseInfo.image
		self.headerTitleLabel.text = exerciseInfo.title
		self.scoreRepLabel.text = exerciseInfo.isWeightLifting ? "Reps" : "Score"
	}
}
