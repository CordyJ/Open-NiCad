//
//  ReportCardTotalRepsVolumeTableViewCell.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-12.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ReportCardTotalRepsVolumeTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var totalRepsLabel: UILabel!
	@IBOutlet fileprivate var totalVolumeLabel: UILabel!
	
	
	var totalReps: Int? {
		didSet {
			if let totalReps = self.totalReps {
				self.totalRepsLabel?.text = "Total Reps: \(totalReps)"
			}
			else {
				self.totalRepsLabel?.text = nil
			}
		}
	}
	
	var totalVolume: Int? {
		didSet {
			if let totalVolume = self.totalVolume {
				self.totalVolumeLabel?.text = "Total Volume: \(totalVolume) lbs"
			}
			else {
				self.totalVolumeLabel?.text = nil
			}
		}
	}
	
	
	override func prepareForReuse() {
		self.totalReps = nil
		self.totalVolume = nil
		
		super.prepareForReuse()
	}
}
