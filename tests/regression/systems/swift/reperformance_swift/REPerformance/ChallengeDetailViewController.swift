//
//  ChallengeDetailViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2018-05-29.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ChallengeDetailViewController: UIViewController {
	
	@IBOutlet fileprivate var dateLabel: UILabel?
	@IBOutlet fileprivate var exerciseLabel: UILabel?
	@IBOutlet fileprivate var categoryLabel: UILabel?
	@IBOutlet fileprivate var descriptionLabel: UILabel?
	
	var challenge: Challenge? {
		didSet {
			if let startEndDateText = self.challenge?.startToEndDateExtendedDisplay() {
				self.dateLabel?.text = startEndDateText
			}
			else {
				self.dateLabel?.isHidden = true
			}
			
			if let category = self.challenge?.exercise {
				self.exerciseLabel?.text = "Exercise: \(category.readable)"
			}
			else {
				self.exerciseLabel?.isHidden = true
			}
			
			if let format = self.challenge?.format.capitalized {
				self.categoryLabel?.text = "Category: \(format)"
			}
			else {
				self.categoryLabel?.isHidden = true
			}
			
			if let description = self.challenge?.description {
				self.descriptionLabel?.text = description
			}
			else {
				self.descriptionLabel?.isHidden = true
			}
		}
	}
	
	
	override func viewDidAppear(_ animated: Bool) {
		super.viewDidAppear(animated)
		
		REPAnalytics.trackScreenWithName(screenName: ScreenName.Challenges.Details(self.challenge!.name), className: String(describing: self))
	}
}


extension Challenge {
	
	func startToEndDateDisplay() -> String? {
		guard let start = startDate, let end = endDate else {
			return nil
		}
		
		let formatter = DateFormatter()
		formatter.dateFormat = "MMM d"
		formatter.timeZone = TimeZone.current
		let dateToReturn = formatter.string(from: start)
		
		let startMonth = Calendar.current.component( .month, from: start)
		let endMonth = Calendar.current.component( .month, from: end)
		
		if startMonth == endMonth {
			let endDay = Calendar.current.component(.day, from: end)
			return dateToReturn + " to \(endDay)"
		} else {
			return dateToReturn + " to " + formatter.string(from: end)
		}
	}
	
	func startToEndDateExtendedDisplay() -> String? {
		guard let start = self.startDate, let end = self.endDate else {
			return nil
		}
		
		let formatter = DateFormatter()
		formatter.dateFormat = "MMMM d' at 'h:mm a"
		formatter.timeZone = TimeZone.current
		
		let dateToReturn = formatter.string(from: start)
		
		return dateToReturn + " to " + formatter.string(from: end)
	}
}
