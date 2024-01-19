//
//  ChallengeGymsViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2018-06-05.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AlamofireImage


class ChallengeGymsViewController: UIViewController {
	
	@IBOutlet fileprivate var tableView: UITableView?
	@IBOutlet fileprivate var bannerImageView: UIImageView?
	@IBOutlet fileprivate var titleLabel: UILabel?
	@IBOutlet fileprivate var subtitleLabel: UILabel?
	@IBOutlet fileprivate var challengeDateRangeLabel: UILabel?
	@IBOutlet fileprivate var remainingLabel: UILabel?
	@IBOutlet fileprivate var joinedTotalLabel: UILabel?
	@IBOutlet fileprivate var actionButton: UIButton?
	
	var challengeAction: (()->())?
	var challengeInfo: (()->())?
	var viewLeaderboard: ((Gym)->())?
	var changeGym: (()->())?
	var selectedAthlete: ((Athlete)->())?
	
	var challenge: Challenge? {
		didSet {
			guard let challenge = self.challenge else {
				return
			}
			
			self.titleLabel?.text = challenge.name
			self.subtitleLabel?.text = challenge.subtitle
			self.challengeDateRangeLabel?.text = challenge.startToEndDateDisplay()
			self.joinedTotalLabel?.text = L10n.challengeTotalJoined("\(challenge.joinedTotal)")
			self.remainingLabel?.text = challenge.timeRemaining()
			self.actionButton?.setTitle(challenge.actionTitle(), for: .normal)
			self.actionButton?.isHidden = !challenge.shouldShowActionButton()
			
			if let bannerImageURL = challenge.imageURL {
				self.bannerImageView?.af_setImage(withURL: bannerImageURL)
			} else {
				self.bannerImageView?.image = UIImage(asset: Asset.Assets.torontoSkylineDELETE)
			}
		}
	}
	
	var athletes: [Athlete]? {
		didSet {
			self.tableView?.reloadData()
		}
	}
	
	
	override func viewDidAppear(_ animated: Bool) {
		super.viewDidAppear(animated)
		
		REPAnalytics.trackScreenWithName(screenName: ScreenName.Challenges.Gyms(self.challenge!.name), className: String(describing: self))
	}
	
	
	@IBAction private func actionTapped(_ sender: UIButton) {
		guard let challenge = self.challenge else {
			return
		}
		
		switch challenge.type {
		case .personal:
			self.challengeAction?()
		case .gym:
				self.challengeAction?()
		}
	}
	
	@IBAction private func infoTapped(_ sender: UIButton) {
		self.challengeInfo?()
	}
	
	func showChallengeJoinedAlert(challenge: Challenge) {
		guard challenge.hasJoined == true else {
			return
		}
		
		guard let exercise = challenge.exercise?.readable else {
			return
		}
		
		let message = L10n.challengeJoinedMessage(exercise, challenge.format.capitalized)
		UIAlertController.showAlert("Challenge Joined", message: message, inViewController: self)
	}
}


extension ChallengeGymsViewController: UITableViewDataSource, UITableViewDelegate {
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		guard let challenge = self.challenge else {
			return 0
		}
		
		switch challenge.type {
		case .personal:
			return self.athletes?.count ?? 0
		case .gym:
            return challenge.gyms?.count ?? 0
		}
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		guard let challenge = self.challenge else {
			fatalError()
		}
		
		switch challenge.type {
		case .personal:
			let cell = tableView.dequeueReusableCell(withIdentifier: "Challenge Gym Leaderboard Ranking Cell Identifier", for: indexPath) as! ChallengeGymLeaderboardTableViewCell
			let athlete = self.athletes![indexPath.row]
			
			cell.rank = athlete.rank
			cell.name = athlete.name
			cell.score = athlete.score
            cell.profileImageURL = (athlete.imageURL != nil) ? athlete.imageURL : FacebookImage.imageURLWithFacebookID(athlete.facebookIdentifier)
			cell.isPublic = athlete.isPublic
			
			return cell
		case .gym:
			let cell = tableView.dequeueReusableCell(withIdentifier: Constants.Challenges.ChallengeGymCellIdentifier, for: indexPath) as! ChallengeGymTableViewCell
            if let gym = challenge.gyms?[indexPath.row] {
                cell.configure(gym: gym, postAt: indexPath.row)
            }
			
			return cell
		}
	}
	
	func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
		tableView.deselectRow(at: indexPath, animated: true)
		
		guard let challenge = self.challenge else {
			return
		}
		
		if challenge.type == .gym {
            if let gym = challenge.gyms?[indexPath.row] {
                self.viewLeaderboard?(gym)
            }
		}
		else if challenge.type == .personal {
			let athlete = self.athletes![indexPath.row]
			self.selectedAthlete?(athlete)
		}
	}
}


fileprivate extension Challenge {
	
	func actionTitle() -> String {
		return self.hasJoined ? L10n.challengeLeave : L10n.challengeJoin
	}
	
	func timeRemaining() -> String {
		/*
		Note: We must use the local time (user's current timezone) to compute the ordinality of days, otherwise it is computed relative to UTC.
		*/
		
		guard let startDate = self.startDate?.toLocalTime(), let endDate = self.endDate?.toLocalTime() else {
			return ""
		}
		
		let now = Date().toLocalTime()
		
		// 1. Challenge has ended.
		guard endDate.compare(now) != .orderedAscending else {
			return L10n.challengeEnded
		}
		
		// 2. Challenge hasn't started yet.
		if startDate.compare(now) == .orderedDescending {
			var daysRemaining = 0
			if let nowDay = Calendar.current.ordinality(of: .day, in: .era, for: now), let startDay = Calendar.current.ordinality(of: .day, in: .era, for: startDate) {
				daysRemaining = startDay - nowDay
			}
			
			if daysRemaining > 0 {
				let challengeStartsInDaysFormatLocalizedString = NSLocalizedString("challenge_starts_in_days", comment: "")
				let challengeStartsInDaysLocalizedString = String.localizedStringWithFormat(challengeStartsInDaysFormatLocalizedString, daysRemaining)
				return challengeStartsInDaysLocalizedString
			}
			else {
				let secondsRemaining = startDate.timeIntervalSince(now)
				let hoursRemaining = Int(floor(secondsRemaining / Constants.secondsInOneHour))
				
				if hoursRemaining > 0 {
					let challengeStartsInHoursFormatLocalizedString = NSLocalizedString("challenge_starts_in_hours", comment: "")
					let challengeStartsInHoursLocalizedString = String.localizedStringWithFormat(challengeStartsInHoursFormatLocalizedString, hoursRemaining)
					return challengeStartsInHoursLocalizedString
				}
				else {
					return L10n.challengeStartsInLessThanAnHour
				}
			}
		}
		// 3. Challenge is currently happening.
		else {
			var daysRemaining = 0
			if let nowDay = Calendar.current.ordinality(of: .day, in: .era, for: now), let endDay = Calendar.current.ordinality(of: .day, in: .era, for: endDate) {
				daysRemaining = endDay - nowDay
			}
			
			if daysRemaining > 0 {
				let challengeStartsInDaysFormatLocalizedString = NSLocalizedString("challenge_days_remaining", comment: "")
				let challengeStartsInDaysLocalizedString = String.localizedStringWithFormat(challengeStartsInDaysFormatLocalizedString, daysRemaining)
				return challengeStartsInDaysLocalizedString
			}
			else {
				let secondsRemaining = endDate.timeIntervalSince(now)
				let hoursRemaining = Int(floor(secondsRemaining / Constants.secondsInOneHour))
				
				if hoursRemaining > 0 {
					let challengeHoursRemainingFormatLocalizedString = NSLocalizedString("challenge_hours_remaining", comment: "")
					let challengeHoursRemainingLocalizedString = String.localizedStringWithFormat(challengeHoursRemainingFormatLocalizedString, hoursRemaining)
					return challengeHoursRemainingLocalizedString
				}
				else {
					return L10n.challengeLessThenHour
				}
			}
		}
	}
	
	func shouldShowActionButton() -> Bool {
		guard let endDate = self.endDate else {
			return true								// Indicates that the challenge is goal-oriented (rather than by a deadline) which we wish to show.
		}
		
		// Only show the button to join/leave a challenge if it has not ended yet.
		let shouldShow = Calendar.current.compare(Date(), to: endDate, toGranularity: .second) == .orderedAscending
		
		return shouldShow
	}
	
	func userBelongInGyms() -> Bool {
		guard let currentGymPlaceID = UserDefaults.standard.currentGymPlaceID, currentGymPlaceID.isEmpty == false else {
			return false
		}
		
        return self.gyms?.filter({$0.placeIdentifier == currentGymPlaceID}).count ?? 0 > 0
	}
}
