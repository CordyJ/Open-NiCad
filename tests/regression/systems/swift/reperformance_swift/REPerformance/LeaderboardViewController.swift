//
//  LeaderboardViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-26.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView


struct LeaderboardViewModel {
	
	let leaderboard: Leaderboard
	let globalLeaderboard: Bool
	let exerciseCategory: ExerciseCategory?
	let exerciseTestFormat: ExerciseTestFormat?
	let filteredByAge: Bool
	
	var leaderboardLocation: String {
		get {
			return (UserDefaults.standard.userCurrentLocation ?? "")
		}
	}
	
	var title: String {
		get {
			if let exerciseCategory = self.exerciseCategory {
				return LeaderboardSelectionHeaderData.titleForExerciseCategory(exerciseCategory: exerciseCategory) + " Leaderboard"
			}
			
			return "Leaderboard"
		}
	}
	
	var subtitle: String {
		get {
			if let exerciseTestFormat = self.exerciseTestFormat {
				return LeaderboardSelectionCellData.textForExerciseFormat(exerciseTestFormat)
			}
			
			return ""
		}
	}
}


enum ErrorableLeaderboardViewModel {
	case leaderboard(viewModel: LeaderboardViewModel)
	case error(message: String)
}


class LeaderboardViewController: UIViewController {
	
	@IBOutlet private var tableView: UITableView?
	@IBOutlet private var segmentedControl: UISegmentedControl?
	@IBOutlet private var outOfLabel: UILabel?
	@IBOutlet private var medalImageView: UIImageView?
	@IBOutlet private var accountVerifiedLabel: UILabel?
	@IBOutlet private var compareLabel: UILabel?
	@IBOutlet private var byTestButton: UIButton?
	@IBOutlet private var byAgeGroupButton: UIButton?
	@IBOutlet private var subtitleLabel: UILabel?
	@IBOutlet private var locationLabel: UILabel?
	
	let friendsIndex: Int = 0
	let everyoneIndex: Int = 1
	let nearbyIndex: Int = 2
	
	var errorableLeaderboardViewModel: ErrorableLeaderboardViewModel?
	
	var currentSegment: LeaderboardGroup = .Everyone
	
	var dismiss: (()->())?
	var byTest: (()->())?
	var byAge: (()->())?
	var segmentChanged: ((LeaderboardGroup)->())?
	var willAppear: (()->())?
	var selectedAthlete: ((Athlete)->())?
	
	
	override func viewDidLoad() {
		super.viewDidLoad()
		
		self.tableView?.estimatedRowHeight = 55
		self.tableView?.rowHeight = UITableView.automaticDimension
		self.navigationItem.leftBarButtonItem = UIBarButtonItem(barButtonSystemItem: .done, target: self, action: #selector(dismissTapped(_:)))
		
		self.setUpSegmentedControl()
		self.setUpViewComponents()
	}
	
	override func viewWillAppear(_ animated: Bool) {
		super.viewWillAppear(animated)
		
		self.willAppear?()
	}
	
	override func viewDidAppear(_ animated: Bool) {
		super.viewDidAppear(animated)
		
		guard let errorableLeaderboardViewModel = self.errorableLeaderboardViewModel, case let .leaderboard(leaderboardViewModel) = errorableLeaderboardViewModel else {
			return
		}
		
		if leaderboardViewModel.globalLeaderboard {
			REPAnalytics.trackScreenWithName(screenName: ScreenName.LeaderBoard.Global, className: String(describing: self))
		}
		
		guard let exerciseCategory = leaderboardViewModel.exerciseCategory else {
			return
		}
		
		switch exerciseCategory {
		case .MileRun:
			REPAnalytics.trackScreenWithName(screenName: ScreenName.LeaderBoard.MileRun, className: String(describing: self))
		case .FortyYardDash:
			REPAnalytics.trackScreenWithName(screenName: ScreenName.LeaderBoard.FortyYardDash, className: String(describing: self))
		case .BenchPress:
			REPAnalytics.trackScreenWithName(screenName: ScreenName.LeaderBoard.BenchPress, className: String(describing: self))
		case .DeadLift:
			REPAnalytics.trackScreenWithName(screenName: ScreenName.LeaderBoard.Deadlift, className: String(describing: self))
		case .Squat:
			REPAnalytics.trackScreenWithName(screenName: ScreenName.LeaderBoard.Squat, className: String(describing: self))
		case .MilitaryPress:
			REPAnalytics.trackScreenWithName(screenName: ScreenName.LeaderBoard.MilitaryPress, className: String(describing: self))
		}
	}
	
	func setUpSegmentedControl() {
		self.segmentedControl?.tintColor = UIColor(named: .rePerformanceOrange)
		self.segmentedControl?.setTitleTextAttributes([NSAttributedString.Key.foregroundColor: UIColor.white], for: .normal)
		self.segmentedControl?.setTitleTextAttributes([NSAttributedString.Key.foregroundColor: UIColor.white], for: .selected)
		self.segmentedControl?.backgroundColor = UIColor.clear
		self.segmentedControl?.selectedSegmentIndex = everyoneIndex
	}
	
	func setUpViewComponents() {
		self.subtitleLabel?.textColor = UIColor.white
		self.locationLabel?.textColor = UIColor.white
		self.outOfLabel?.textColor = UIColor.white
		self.accountVerifiedLabel?.textColor = UIColor(named: .rePerformanceOrange)
		self.compareLabel?.textColor = UIColor.white
		self.byTestButton?.setUpWhiteREPerformanceButton()
		self.byAgeGroupButton?.setUpWhiteREPerformanceButton()
	}
	
	func setUpView() {
		if let errorableLeaderboardViewModel = self.errorableLeaderboardViewModel, case let .leaderboard(leaderboardViewModel) = errorableLeaderboardViewModel {
			if leaderboardViewModel.leaderboard.isRankingEmpty {
				self.outOfLabel?.text = ""
			}
			else {
				self.outOfLabel?.text = "out of \(leaderboardViewModel.leaderboard.total)"
			}
			
			if leaderboardViewModel.leaderboard.isRankingEmpty {
				self.setAccountVerifiedVisible(false)
			}
			else {
				self.setAccountVerifiedVisible(true)
			}
			
			if leaderboardViewModel.filteredByAge {
				self.byAgeGroupButton?.setTitle(L10n.leaderboardAllAgeGroupButtonTitle, for: .normal)
			}
			else {
				self.byAgeGroupButton?.setTitle(L10n.leaderboardYourAgeGroupButtonTitle, for: .normal)
			}
			
			self.title = leaderboardViewModel.title
			self.subtitleLabel?.text = leaderboardViewModel.subtitle
			
			if self.currentSegment == .Nearby {
				self.locationLabel?.text = leaderboardViewModel.leaderboardLocation
			}
			else {
				self.locationLabel?.text = nil
			}
		}
		else {
			self.outOfLabel?.text = ""
			self.setAccountVerifiedVisible(false)
			self.byAgeGroupButton?.setTitle(L10n.leaderboardYourAgeGroupButtonTitle, for: .normal)
			
			self.title = "Leaderboard"
			self.subtitleLabel?.text = nil
			self.locationLabel?.text = nil
		}
		
		self.tableView?.setContentOffset(CGPoint.zero, animated: true)
	}
	
	func setAccountVerifiedVisible(_ visible: Bool) {
		self.medalImageView?.isHidden = !visible
		self.accountVerifiedLabel?.isHidden = !visible
	}
	
	@IBAction func dismissTapped(_ sender: UIButton) {
		self.dismiss?()
	}
	
	@IBAction func byTestTapped(_ sender: UIButton) {
		self.byTest?()
	}
	
	@IBAction func byAgeGroupTapped(_ sender: UIButton) {
		self.byAge?()
	}
	
	@IBAction func segmentChanged(_ sender: UISegmentedControl) {
		switch sender.selectedSegmentIndex {
		case 0:
			self.currentSegment = .Friends
			self.segmentChanged?(.Friends)
		case 1:
			self.currentSegment = .Everyone
			self.segmentChanged?(.Everyone)
		case 2:
			self.currentSegment = .Nearby
			self.segmentChanged?(.Nearby)
		default:
			self.currentSegment = .Everyone
			self.segmentChanged?(.Everyone)
		}
	}
	
	func reloadView() {
		self.setUpView()
		self.tableView?.reloadData()
	}
	
	func showLoadingIndicator(_ show: Bool) {
		if show {
			NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		}
		else {
			NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
		}
	}
	
	func reloadRow(row: Int, section: Int) {
		let indexPathToReload = IndexPath(row: row, section: section)
		self.tableView?.reloadRows(at: [indexPathToReload], with: .automatic)
	}
}


extension LeaderboardViewController: UITableViewDataSource, UITableViewDelegate {
	
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
