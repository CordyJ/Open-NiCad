//
//  ReportCardScoreOptionsTableViewCell.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-08.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ReportCardScoreOptionsTableViewCell: UITableViewCell {
	
	@IBAction private func tappedMyScoresButton(_ sender: Any) {
		self.viewLatestScores?()
	}
	
	@IBAction private func tappedBestScoresButton(_ sender: Any?) {
		self.viewBestScores?()
	}
	
	@IBAction private func tappedChallengesButton(_ sender: Any) {
		self.viewChallenges?()
	}
	
	
	var viewLatestScores: (()->())?
	var viewBestScores: (()->())?
	var viewChallenges: (()->())?
}
