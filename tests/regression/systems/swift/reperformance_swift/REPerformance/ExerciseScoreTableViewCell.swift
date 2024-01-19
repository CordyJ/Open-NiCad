//
//  ExerciseScoreTableViewCell.swift
//  REPerformance
//
//  Created by Francis Chary on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


fileprivate let ExerciseScoreCellInvalidEntry = " - "


class ExerciseScoreTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var exerciseSubCategoryLabel: UILabel?
	@IBOutlet fileprivate var dateDisplayLabel: UILabel?
	@IBOutlet fileprivate var scoreDisplayLabel: UILabel?
	
	
	override func prepareForReuse() {
		self.exerciseSubCategoryLabel?.text = ExerciseScoreCellInvalidEntry
		self.dateDisplayLabel?.text = ExerciseScoreCellInvalidEntry
		self.scoreDisplayLabel?.text = ExerciseScoreCellInvalidEntry
		
		super.prepareForReuse()
	}
}


struct ExerciseScorePersonalCellViewModel {
	let exerciseSubCategoryName: String?
	let dateDisplay: String?
	let scoreDisplay: String?
	let videoStatusImage: UIImage?
}


class ExerciseScorePersonalTableViewCell: ExerciseScoreTableViewCell {
	
	@IBOutlet fileprivate var videoStatusImageView: UIImageView?
	@IBOutlet fileprivate var noVideoStatusLabel: UILabel?
	
	
	override func prepareForReuse() {
		self.videoStatusImageView?.image = nil
		
		super.prepareForReuse()
	}
	
	
	func configure(with score: ExerciseScorePersonalCellViewModel) {
		self.exerciseSubCategoryLabel?.text = score.exerciseSubCategoryName ?? ExerciseScoreCellInvalidEntry
		self.scoreDisplayLabel?.text = score.scoreDisplay ?? ExerciseScoreCellInvalidEntry
		self.dateDisplayLabel?.text = score.dateDisplay ?? ExerciseScoreCellInvalidEntry
		
		if let videoStatusImage = score.videoStatusImage {
			self.videoStatusImageView?.image = videoStatusImage
			self.videoStatusImageView?.isHidden = false
			self.noVideoStatusLabel?.isHidden = true
		}
		else {
			self.videoStatusImageView?.image = nil
			self.videoStatusImageView?.isHidden = true
			self.noVideoStatusLabel?.isHidden = false
		}
	}
}


struct ExerciseScoreAthleteCellViewModel {
	let exerciseSubCategoryName: String?
	let dateDisplay: String?
	let scoreDisplay: String?
	let weight: Double?
	let volume: Double?
}


class ExerciseScoreAthleteTableViewCell: ExerciseScoreTableViewCell {
	
	@IBOutlet fileprivate var weightLabel: UILabel?
	@IBOutlet fileprivate var volumeLabel: UILabel?
	
	
	override func prepareForReuse() {
		self.volumeLabel?.text = ExerciseScoreCellInvalidEntry
		
		super.prepareForReuse()
	}
	
	
	func configure(with score: ExerciseScoreAthleteCellViewModel) {
		self.exerciseSubCategoryLabel?.text = score.exerciseSubCategoryName ?? ExerciseScoreCellInvalidEntry
		self.scoreDisplayLabel?.text = score.scoreDisplay ?? ExerciseScoreCellInvalidEntry
		self.dateDisplayLabel?.text = score.dateDisplay ?? ExerciseScoreCellInvalidEntry
		
		if let weight = score.weight, weight > 0 {
			self.weightLabel?.text = "\(Int(weight)) lbs"
		}
		else {
			self.weightLabel?.text = ExerciseScoreCellInvalidEntry
		}
		
		if let volume = score.volume, volume > 0 {
			self.volumeLabel?.text = "\(Int(volume)) lbs"
		}
		else {
			self.volumeLabel?.text = ExerciseScoreCellInvalidEntry
		}
	}
}
