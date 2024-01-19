//
//  GymLeaderboardViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-10-10.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView


class GymLeaderboardViewController: UIViewController {
	
	@IBOutlet private var tableView: UITableView?
	@IBOutlet private var outOfLabel: UILabel?
	@IBOutlet private var subtitleLabel: UILabel?
	@IBOutlet private var nameLabel: UILabel?
	@IBOutlet private var regionLabel: UILabel?
	
	var errorableLeaderboardViewModel: ErrorableLeaderboardViewModel?
	
	var selectedAthlete: ((Athlete)->())?
	
	
	override func viewDidLoad() {
		super.viewDidLoad()
		
		self.tableView?.estimatedRowHeight = 55
		self.tableView?.rowHeight = UITableView.automaticDimension
		
		self.setUpViewComponents()
	}
	
	
	func showLoadingIndicator(_ show: Bool) {
		if show == true {
			NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		}
		else {
			NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
		}
	}
	
	func setUpViewComponents() {
		self.subtitleLabel?.textColor = UIColor.white
		self.nameLabel?.textColor = UIColor(named: .rePerformanceYellow)
		self.regionLabel?.textColor = UIColor(named: .rePerformanceYellow)
		self.outOfLabel?.textColor = UIColor.white
	}
	
	func setUpView() {
		guard let errorableLeaderboardViewModel = self.errorableLeaderboardViewModel, case let .leaderboard(leaderboardViewModel) = errorableLeaderboardViewModel else {
			return
		}
		
		self.title = leaderboardViewModel.title
		self.subtitleLabel?.text = leaderboardViewModel.subtitle
		self.nameLabel?.text = leaderboardViewModel.leaderboard.gym?.name
		self.outOfLabel?.text = "out of \(leaderboardViewModel.leaderboard.total)"
		self.tableView?.setContentOffset(CGPoint.zero, animated: true)
	}
	
	func reloadView() {
		self.setUpView()
		self.tableView?.reloadData()
	}
	
	func reloadRow(row: Int, section: Int) {
		let indexPathToReload = IndexPath(row: row, section: section)
		self.tableView?.reloadRows(at: [indexPathToReload], with: .automatic)
	}
}


extension GymLeaderboardViewController: UITableViewDataSource, UITableViewDelegate {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		guard let errorableLeaderboardViewModel = self.errorableLeaderboardViewModel, case let .leaderboard(leaderboardViewModel) = errorableLeaderboardViewModel else {
			return 0
		}
		
		if leaderboardViewModel.leaderboard.isRankingEmpty {
			return 1
		}
		else {
			return ((leaderboardViewModel.leaderboard.groupedRankings.count * 2) - 1)
		}
	}
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		guard let errorableLeaderboardViewModel = self.errorableLeaderboardViewModel, case let .leaderboard(leaderboardViewModel) = errorableLeaderboardViewModel else {
			return 0
		}
		
		if leaderboardViewModel.leaderboard.isRankingEmpty {
			return 1
		}
		else {
			if (section % 2 == 0) {
				let groupedRankingSection = Int(floor(Double(section) / 2))
				
				return leaderboardViewModel.leaderboard.groupedRankings[groupedRankingSection].count
			}
			else {
				return 1				// Show the divider cell between each grouped ranking.
			}
		}
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		guard let errorableLeaderboardViewModel = self.errorableLeaderboardViewModel else {
			fatalError()
		}
		
		switch errorableLeaderboardViewModel {
		case .leaderboard(let leaderboardViewModel):
			if (indexPath.section % 2 == 0) {
				let leaderboardPositionTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.ReportCard.LeaderboardPositionCellIdentifier, for: indexPath) as! LeaderboardPositionTableViewCell
				let groupedRankingSection = Int(floor(Double(indexPath.section) / 2))
				let athlete = leaderboardViewModel.leaderboard.groupedRankings[groupedRankingSection][indexPath.row]
				
				let score: String?
				if leaderboardViewModel.globalLeaderboard == true {
					score = athlete.lifestyleCategory
				}
				else if let athleteScore = athlete.score {
					if leaderboardViewModel.exerciseCategory == .MileRun, let localScore = FormatMillisecondsForDisplay.convertScoreForDisplayMileRun(score: "\(athleteScore)") {
						score = localScore
					}
					else if leaderboardViewModel.exerciseCategory == .FortyYardDash, let localScore = FormatMillisecondsForDisplay.convertScoreForDisplayFortyYardDash(score: "\(athleteScore)") {
						score = localScore
					}
					else {
						score = "\(athleteScore)"
					}
				}
				else {
					score = nil
				}
				
				var athleteRank = ""
				if let rank = athlete.rank {
					athleteRank = "\(rank)"
				}
				
				leaderboardPositionTableViewCell.configureCell(rankText: athleteRank, nameText: athlete.name, isPublic: (athlete.isPublic ?? false), rightSideText: score ?? "", medalVisible: athlete.isVerified ?? false, personFacebookID: athlete.facebookIdentifier, profileURL: athlete.imageURL)
				
				return leaderboardPositionTableViewCell
			}
			else {
				return tableView.dequeueReusableCell(withIdentifier: Constants.ReportCard.LeaderboardDividerCellIdentifier, for: indexPath) as! LeaderboardDividerTableViewCell
			}
		case .error(let message):
			let leaderboardErrorTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.ReportCard.LeaderboardErrorCellIdentifier, for: indexPath) as! LeaderboardErrorTableViewCell
			leaderboardErrorTableViewCell.configureCell(errorMessage: message)
			
			return leaderboardErrorTableViewCell
		}
	}
	
	func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
		tableView.deselectRow(at: indexPath, animated: true)
		
		guard let errorableLeaderboardViewModel = self.errorableLeaderboardViewModel, case let .leaderboard(leaderboardViewModel) = errorableLeaderboardViewModel else {
			return
		}
		
		guard indexPath.section % 2 == 0 else {
			return
		}
		
		let groupedRankingSection = Int(floor(Double(indexPath.section) / 2))
		let athlete = leaderboardViewModel.leaderboard.groupedRankings[groupedRankingSection][indexPath.row]
		
		self.selectedAthlete?(athlete)
	}
}
