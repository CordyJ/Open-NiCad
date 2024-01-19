//
//  ChallengeGymTableViewCell.swift
//  REPerformance
//
//  Created by Alan Yeung on 2018-06-05.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ChallengeGymTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var positionLabel: UILabel?
	@IBOutlet fileprivate var titleLabel: UILabel?
	@IBOutlet fileprivate var totalRepsLabel: UILabel?
	
	
	override func prepareForReuse() {
		super.prepareForReuse()
		
		self.positionLabel?.text = nil
		self.titleLabel?.text = nil
		self.totalRepsLabel?.text = nil
	}
	
	
	func configure(gym: Gym, postAt pos: Int) {
		self.positionLabel?.text = "\(pos + 1)"
		self.titleLabel?.text = gym.name
		
		if let totalReps = gym.totalReps {
			let formatLocalizedString = NSLocalizedString("challenge_total_rep", comment: "")
			let challengeTotalRepsInLocalizedString = String.localizedStringWithFormat(formatLocalizedString, totalReps)
			self.totalRepsLabel?.text = challengeTotalRepsInLocalizedString
		}
		else {
			self.totalRepsLabel?.text = nil
		}
	}
}
