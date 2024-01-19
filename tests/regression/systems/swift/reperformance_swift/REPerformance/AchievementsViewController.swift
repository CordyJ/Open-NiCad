//
//  AchievementsViewController.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2017-05-24.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView


class AchievementTypeTableViewCell: UITableViewCell {
	
	//MARK: - Properties
	
	@IBOutlet private var typeTitleLabel: UILabel!
	@IBOutlet private var typeImageView: UIImageView!
	@IBOutlet private var dropDownIconImageView: UIImageView!
	
	var title: String? {
		didSet {
			self.typeTitleLabel.text = title
		}
	}
	
	var typeImage: UIImage? {
		didSet {
			self.typeImageView.image = typeImage
		}
	}
	
	
	//MARK: - UITableViewCell Methods
	
	override func prepareForReuse() {
		super.prepareForReuse()
		
		self.title = nil
		self.typeImage = nil
	}
	
	override func setSelected(_ selected: Bool, animated: Bool) {
		super.setSelected(selected, animated: animated)
		
		let degrees:CGFloat = selected ? 0 : 180
		let radians:CGFloat = degrees * .pi/180
		UIView.animate(withDuration: 0.4) {
			self.dropDownIconImageView.transform = CGAffineTransform(rotationAngle: radians)
		}
	}
}


class AchievementItemTableViewCell: UITableViewCell {
	
	//MARK: - Properties
	
	@IBOutlet private var achievementTitleLabel: UILabel!
	@IBOutlet private var creditsWorthLabel: UILabel!
	@IBOutlet private var pointsLabel: UILabel!
	
	var achievementTitle: String? {
		didSet {
			self.achievementTitleLabel.text = achievementTitle
		}
	}
	
	var creditsWorth: Int? {
		didSet {
			if let creditsWorth = creditsWorth {
				self.creditsWorthLabel.text = "worth \(creditsWorth) credits"
			}
			else {
				self.creditsWorthLabel.text = nil
			}
		}
	}
	
	var points: Int? {
		didSet {
			if let points = points {
				self.pointsLabel.text = "\(points)"
			}
			else {
				self.pointsLabel.text = nil
			}
		}
	}
	
	
	//MARK: - UITableViewCell Methods
	
	override func prepareForReuse() {
		super.prepareForReuse()
		
		self.achievementTitle = nil
		self.creditsWorth = nil
		self.points = nil
	}
}


class AchievementsViewController: UIViewController {
	
	//MARK: - Properties
	
	@IBOutlet fileprivate var achievementsTableView: UITableView!
	
	fileprivate var achievement: Achievements? {
		didSet {
			self.achievementsTableView.reloadData()
		}
	}
	
	fileprivate var selectedIndexPath: IndexPath? {
		didSet {
			// Only allow the first row to be 'selected' for drop-down purposes.
			if selectedIndexPath?.row != 0 {
				selectedIndexPath = oldValue
				return
			}
			
			self.achievementsTableView.beginUpdates()
			
			if let oldValue = oldValue, oldValue != selectedIndexPath {
				// Remove cells from the old index path.
                var indexPathsToRemove: [IndexPath] = []
                for indexPathRowIterator in 1...(self.achievementsTableView.numberOfRows(inSection: oldValue.section) - 1) {
                    let indexPathToRemove = IndexPath(row: indexPathRowIterator, section: oldValue.section)
                    indexPathsToRemove.append(indexPathToRemove)
                }

                self.achievementsTableView.deleteRows(at: indexPathsToRemove, with: .automatic)
			}
			
			if let selectedIndexPath = selectedIndexPath, oldValue != selectedIndexPath {
				// Add cells to the new index path.
				var indexPathsToAdd: [IndexPath] = []
                var upperRange = 3
                if selectedIndexPath.section == 6 {
                    upperRange = 2
                }
                else if selectedIndexPath.section == 7 {
                    upperRange = 1
                }
				for indexPathRowIterator in 1...upperRange  {
					let indexPathToAdd = IndexPath(row: indexPathRowIterator, section: selectedIndexPath.section)
					indexPathsToAdd.append(indexPathToAdd)
				}
				
				self.achievementsTableView.insertRows(at: indexPathsToAdd, with: .automatic)
			}
			
			self.achievementsTableView.endUpdates()
		}
	}
	
	
	//MARK: - UIViewController Methods
	
	override func viewDidLoad() {
		super.viewDidLoad()
		
		self.achievementsTableView?.rowHeight = UITableView.automaticDimension
		self.achievementsTableView?.estimatedRowHeight = 44
	}
	
	override func viewWillAppear(_ animated: Bool) {
		super.viewWillAppear(animated)
		
		self.retrieveAchievements()
	}
	
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.Achievements, className: String(describing: self))
    }
	
	//MARK: - AchievementsViewController Methods
	
	private func retrieveAchievements() {
		NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		
		let achievementsDataProvider = AchievementsDataProvider()
		achievementsDataProvider.retrieveAchievements { [weak self] (achievements, _) in
			NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
			self?.achievement = achievements
		}
	}
}


extension AchievementsViewController: UITableViewDataSource {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		guard let _ = self.achievement else {
			return 0
		}
		
		return 8
	}
    
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        if self.selectedIndexPath?.section == section && self.selectedIndexPath?.section == 6 {
            return 3
        }
        else if self.selectedIndexPath?.section == section && self.selectedIndexPath?.section == 7 {
            return 2
        }
        else if self.selectedIndexPath?.section == section {
            return 4
        }
		
		return 1
	}
    
	
	func tableView(_ tableView: UITableView, willSelectRowAt indexPath: IndexPath) -> IndexPath? {
		if indexPath.row != 0 {
			return nil
		}
		
		return indexPath
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		var cell: UITableViewCell!
		
		if indexPath.row == 0 {
			let achievementTypeTableViewCell = tableView.dequeueReusableCell(withIdentifier: "Achievement Type Cell Identifier", for: indexPath) as! AchievementTypeTableViewCell
			
			switch indexPath.section {
			case 0:
				achievementTypeTableViewCell.title = "Mile run"
				achievementTypeTableViewCell.typeImage = Asset.ReportCard.scoreHeaderMileRun.image
			case 1:
				achievementTypeTableViewCell.title = "40 Yard Dash"
				achievementTypeTableViewCell.typeImage = Asset.ReportCard.scoreHeaderFortyYardDash.image
			case 2:
				achievementTypeTableViewCell.title = "Bench Press"
				achievementTypeTableViewCell.typeImage = Asset.ReportCard.scoreHeaderBenchPress.image
			case 3:
				achievementTypeTableViewCell.title = "Deadlift"
				achievementTypeTableViewCell.typeImage = Asset.ReportCard.scoreHeaderDeadlift.image
			case 4:
				achievementTypeTableViewCell.title = "Squat"
				achievementTypeTableViewCell.typeImage = Asset.ReportCard.scoreHeaderSquat.image
			case 5:
				achievementTypeTableViewCell.title = "Military Press"
				achievementTypeTableViewCell.typeImage = Asset.ReportCard.scoreHeaderMilitaryPress.image
            case 6:
                achievementTypeTableViewCell.title = "Challenges"
                achievementTypeTableViewCell.typeImage = Asset.Assets.Profile.challengeIcon.image
            case 7:
                achievementTypeTableViewCell.title = "Loyalty"
                achievementTypeTableViewCell.typeImage = Asset.Assets.Profile.loyaltyIcon.image
			default:
				break
			}
			
			cell = achievementTypeTableViewCell
		}
		else {
			let achievementItemTableViewCell = tableView.dequeueReusableCell(withIdentifier: "Achievement Item Cell Identifier", for: indexPath) as! AchievementItemTableViewCell
			
			var currentAchievement: Achievement?
            var challengeAchievement: Achievement_Challenge?
            var loyaltyAchievement: Achievement_Loyalty?
			switch indexPath.section {
			case 0:
				currentAchievement = self.achievement?.mileRun
			case 1:
				currentAchievement = self.achievement?.fourtyYardDash
			case 2:
				currentAchievement = self.achievement?.benchPress
			case 3:
				currentAchievement = self.achievement?.deadlift
			case 4:
				currentAchievement = self.achievement?.squat
			case 5:
				currentAchievement = self.achievement?.militaryPress
            case 6:
                challengeAchievement = self.achievement?.challenge
            case 7:
                loyaltyAchievement = self.achievement?.loyalty
			default:
				break
			}
            
            if challengeAchievement != nil {
                switch indexPath.row {
                case 1:
                    achievementItemTableViewCell.achievementTitle = "Join Challenge"
                    if let challengeAchievement = challengeAchievement {
                        achievementItemTableViewCell.points = challengeAchievement.joinChallengeCount
                        achievementItemTableViewCell.creditsWorth = challengeAchievement.joinChallengeCreditWorth
                    }
                case 2:
                    achievementItemTableViewCell.achievementTitle = "Join Challenge Streak"
                    if let challengeAchievement = challengeAchievement {
                        achievementItemTableViewCell.points = challengeAchievement.challengeStreakCount
                        achievementItemTableViewCell.creditsWorth = challengeAchievement.challgeneStreakCreditWorth
                    }
                default:
                    break
                }
            }
            else if loyaltyAchievement != nil {
                switch indexPath.row {
                case 1:
                    achievementItemTableViewCell.achievementTitle = "Daily Visit"
                    if let loyaltyAchievement = loyaltyAchievement {
                        achievementItemTableViewCell.points = loyaltyAchievement.dailyVisitCount
                        achievementItemTableViewCell.creditsWorth = loyaltyAchievement.dailyVisitCreditWorth
                    }
                default:
                    break
                }
            }
			
            else if currentAchievement != nil {
                switch indexPath.row {
                case 1:
                    achievementItemTableViewCell.achievementTitle = "Personal Best"
                    if let currentAchievement = currentAchievement {
                        achievementItemTableViewCell.points = currentAchievement.personalBestCount
                        achievementItemTableViewCell.creditsWorth = currentAchievement.personalBestCreditWorth
                    }
                case 2:
                    achievementItemTableViewCell.achievementTitle = "Video Approval"
                    if let currentAchievement = currentAchievement {
                        achievementItemTableViewCell.points = currentAchievement.videoCount
                        achievementItemTableViewCell.creditsWorth = currentAchievement.videoCreditWorth
                    }
                case 3:
                    achievementItemTableViewCell.achievementTitle = "Submission"
                    if let currentAchievement = currentAchievement {
                        achievementItemTableViewCell.points = currentAchievement.submissionCount
                        achievementItemTableViewCell.creditsWorth = currentAchievement.submissionCreditWorth
                    }
                default:
                    break
                }
            }
			
			cell = achievementItemTableViewCell
		}
		
		return cell
	}
}


extension AchievementsViewController: UITableViewDelegate {
	
	func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
		self.selectedIndexPath = indexPath
	}
}

