//
//  ReportCardCoordinator.swift
//  REPerformance
//
//  Created by Francis Chary on 2017-05-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import Social
import Alamofire
import AlamofireImage
import NVActivityIndicatorView
import FBSDKCoreKit


class ReportCardCoordinator {
	
	let reportCardDataProvider = ReportCardDataProvider()
	let challengesCoordinator = ChallengesCoordinator()
	let chatCoordinator = ChatCoordinator()
	let athlete: Athlete?
	
	var reportCardViewController: ReportCardViewController
	var leaderboardCoordinator: LeaderboardCoordinator?
	var updateReportCardRequired: Bool = true
	var lastUpdate: Date = Date()
	
	static var canShareReport: Bool {
		get {
			if SLComposeViewController.isAvailable(forServiceType: SLServiceTypeFacebook) {
				return true
			}
			
			return false
		}
	}
	
	
	init(athlete: Athlete? = nil) {
		self.athlete = athlete
		self.reportCardViewController = StoryboardScene.ReportCard.reportCardVC.instantiate()
		self.setupReportCardViewController()
	}
	
	
	func setupReportCardViewController() {
		self.reportCardViewController.tabBarController?.navigationItem.title = L10n.reportCardTitle
		self.reportCardViewController.tabBarItem = UITabBarItem(title: L10n.reportCardTabBarItemTitle, image: #imageLiteral(resourceName: "TabBar_ReportCard"), tag: 0)
		
		if let athlete = athlete {
			self.setupReportCardForAthleteViewController(athlete)
		}
		else {
			self.setupReportCardForUserViewController()
		}
	}
	
	func setupReportCardForUserViewController() {
		self.reportCardViewController.chat = {
			self.chatCoordinator.start(presenting: self.reportCardViewController)
		}
		
		self.reportCardViewController.shareReport = { [weak self] (reportCard) in
			self?.shareReportCardOnFacebook(reportCardImage: reportCard)
		}
		
		self.reportCardViewController.reportCardWillAppear = {
			self.reportCardViewController.age = UserDefaults.standard.userAge
			self.reportCardViewController.weight = UserDefaults.standard.userWeight
			self.reportCardViewController.isPersonalReportCard = true
			self.reportCardViewController.isMale = (UserDefaults.standard.userGender == Constants.UserData.Male)
			self.reportCardViewController.isPublic = (UserDefaults.standard.isProfilePrivate == false)
			self.reportCardViewController.lifestyleCategoryName = UserDefaults.standard.lifestyleType
			
			if let firstName = UserDefaults.standard.userFirstName, let lastName = UserDefaults.standard.userLastName {
				self.reportCardViewController.name = "\(firstName) \(lastName)"
			} else {
				self.reportCardViewController.name = ""
			}
			
			let elapsedTimeSinceLastRetrieval = Date().timeIntervalSince(self.lastUpdate)
			if self.updateReportCardRequired || (elapsedTimeSinceLastRetrieval > Constants.ReportCard.RefreshTimeInterval) {
				self.retrieveReportCard()
				self.updateReportCardRequired = false
				self.lastUpdate = Date()
				
                self.setUserProfileImage(userFacebookID: UserDefaults.standard.userFacebookID, lifestyle: UserDefaults.standard.lifestyleType)
			}
			
			if let reportCardNeverSeen = UserDefaults.standard.reportCardNeverSeen {
				if reportCardNeverSeen {
					UIAlertController.showAlert(nil, message: L10n.reportCardFirstViewAlert, inViewController: self.reportCardViewController)
					UserDefaults.standard.reportCardNeverSeen = false
				}
			}
			
			self.refreshChatUnreadMessagesStatus()
		}
		
		self.reportCardViewController.changeProfileVisibility = { (isPublic) in
			let currentProfileVisibilityIsPrivate = UserDefaults.standard.isProfilePrivate
			self.reportCardDataProvider.updateProfileVisibility(isPrivate: !isPublic) { (errorMessage) in
				if let _ = errorMessage {
					UserDefaults.standard.isProfilePrivate = currentProfileVisibilityIsPrivate
				}
				else {
					UserDefaults.standard.isProfilePrivate = (isPublic == false)
				}
				
				self.reportCardViewController.isPublic = (UserDefaults.standard.isProfilePrivate == false)
			}
		}
        
        self.reportCardViewController.updateProfileImage = { (profileImage) in
            _ = UIImage.saveProfileImage(image: profileImage)
            self.reportCardDataProvider.updateProfileImage() {
                (errorMessage) in
                if let _ = errorMessage {
                    print(errorMessage?.description ?? "error setting profile image")
                }
            }
        }
		
		self.reportCardViewController.onMyLatestScoresPressed = {
			self.showScores()
		}
		
		self.reportCardViewController.onMyBestScoresPressed = {
			self.showBestScores()
		}
		
		self.reportCardViewController.onChallengesPressed = {
			self.moveToChallenges()
		}
	}
	
	func setupReportCardForAthleteViewController(_ athlete: Athlete) {
		self.reportCardViewController.chat = {
			self.chatCoordinator.start(presenting: self.reportCardViewController, athlete: athlete)
		}
		
		self.reportCardViewController.reportCardWillAppear = {
			self.reportCardViewController.name = athlete.name
			self.reportCardViewController.age = athlete.age
			self.reportCardViewController.weight = athlete.weight
			self.reportCardViewController.isMale = (athlete.gender ?? "male").lowercased() == "male"
			self.reportCardViewController.lifestyleCategoryName = athlete.lifestyleCategory
			self.reportCardViewController.isPersonalReportCard = false
			
			self.retrieveAthleteReportCard(identifier: "\(athlete.userIdentifier)")
			
            self.setAthleteProfileImage(userFacebookID: athlete.facebookIdentifier, lifestyle: athlete.lifestyleCategory, athleteID: athlete.userIdentifier)
		}
		
		self.reportCardDataProvider.retrieveAthleteScores(identifier: "\(athlete.userIdentifier)") { (allExercisesResult: ReportCardExerciseScores?, errorMessage: String?) in
			DispatchQueue.main.async {
				self.reportCardViewController.exerciseScores = allExercisesResult
			}
		}
	}
	
	func recreateReportCard() {
		self.reportCardViewController = StoryboardScene.ReportCard.reportCardVC.instantiate()
		self.setupReportCardViewController()
	}
	
	func retrieveReportCard() {
		self.reportCardDataProvider.retrievePersonalReportCard() { (reportCard, _) in
			self.reportCardViewController.reportCard = reportCard
		}
	}
	
	func retrieveAthleteReportCard(identifier: String) {
		self.reportCardDataProvider.retrieveAthleteReportCard(identifier: identifier) { (reportCard, _) in
			self.reportCardViewController.reportCard = reportCard
		}
	}
	
    func setUserProfileImage(userFacebookID: String?, lifestyle: String?) {
        if let profileImage = UIImage.getSavedProfileImage() {
            self.reportCardViewController.profileImage = profileImage
        }
        else {
            self.setProfileImageFromFacebook(userFacebookID: userFacebookID, lifestyle: lifestyle)
        }
    }
        
    func setAthleteProfileImage(userFacebookID: String?, lifestyle: String?, athleteID: Int) {
        self.reportCardDataProvider.getProfileImage(athleteID: athleteID) { (profileURL) in
            if let profileURL = profileURL  {
                
                UIImage.userProfileImage(url: profileURL, completion: { (image) in
                        self.reportCardViewController.profileImage = image
                    })
            }
            else {
                self.setProfileImageFromFacebook(userFacebookID: userFacebookID, lifestyle: lifestyle)
            }
            
        }
	}
    
    func setProfileImageFromFacebook(userFacebookID: String?, lifestyle: String?) {
        if let userFacebookID = userFacebookID, userFacebookID.isEmpty == false {
            let imageSize = UIScreen.main.bounds.width
            if let imageURL = FacebookImage.imageURLWithFacebookID(userFacebookID, size: CGSize(width: imageSize, height: imageSize)) {
                
                UIImage.userProfileImage(url: imageURL, completion: { (image) in
                    if let profileImage = image {
                        self.reportCardViewController.profileImage = profileImage
                    }
                    else {
                        self.setDefaultImage(lifestyleType: lifestyle)
                    }
                })
            }
            else {
                self.setDefaultImage(lifestyleType: lifestyle)
            }
        }
        else {
            self.setDefaultImage(lifestyleType: lifestyle)
        }
    }
	
	func setDefaultImage(lifestyleType: String?) {
		let profileImage: UIImage
		switch (lifestyleType ?? "").lowercased() {
		case "fit":
			profileImage = Asset.Assets.Profile.fitProfile.image
		case "action":
			profileImage = Asset.Assets.Profile.actionProfile.image
		case "athlete":
			profileImage = Asset.Assets.Profile.athleteProfile.image
		case "elite":
			profileImage = Asset.Assets.Profile.eliteProfile.image
		default:
			profileImage = Asset.Assets.Profile.fitProfile.image
		}
		
		self.reportCardViewController.profileImage = profileImage
	}
	
	func tabBarViewController() -> UIViewController {
		return self.reportCardViewController
	}
	
	func refreshChatUnreadMessagesStatus(completion: (()->())? = nil) {
		ChatCoordinator.getUnreadMessageCount() { (getUnreadMessageCountResult) in
			if case .success(let count) = getUnreadMessageCountResult {
				let hasUnreadMessages = count > 0
				self.reportCardViewController.hasUnreadMessages = hasUnreadMessages
				self.reportCardViewController.tabBarItem.badgeValue = hasUnreadMessages ? "" : nil		// Assign an empty string to see a circle notification or nil to remove it.
				UIApplication.shared.applicationIconBadgeNumber = count
			}
			
			completion?()
		}
	}
	
	func showScores() {
		let myScoresViewController = StoryboardScene.ReportCard.myScoresViewController.instantiate()
		myScoresViewController.title = L10n.myLatestScoresTitle
		myScoresViewController.navigationItem.leftBarButtonItem = UIBarButtonItem(title: L10n.doneBarItemTitle, style: .plain, target: self, action: #selector(self.closeButtonTapped(sender:)))
		myScoresViewController.showVideoStatusLegend = (athlete == nil)
		
		let navigationController = UINavigationController()
		navigationController.viewControllers = [myScoresViewController]
		navigationController.view.backgroundColor = UIColor.clear
		
		self.reportCardDataProvider.retrieveScores() { (allExercisesResult: ReportCardExerciseScores?, errorMessage: String?) in
			DispatchQueue.main.async {
				let scores: MyScores?
				if let allExercisesResult = allExercisesResult {
					scores = MyScores(isPersonal: true, myScoresAllExerciseResult: allExercisesResult)
				}
				else {
					scores = nil
				}
				myScoresViewController.viewData = scores
				myScoresViewController.scoresTableView?.reloadData()
			}
		}
		
		self.reportCardViewController.present(navigationController, animated: true, completion: nil)
	}
	
	func showBestScores() {
		guard let userID = UserDefaults.standard.userID else {
			return
		}
		
		let myBestScoresViewController = StoryboardScene.ReportCard.myBestScoresViewControllerStoryboardIdentifier.instantiate()
		myBestScoresViewController.title = L10n.myBestScoresTitle
		myBestScoresViewController.navigationItem.leftBarButtonItem = BlockBarButtonItem(title: L10n.doneBarItemTitle, style: .plain) {
			self.reportCardViewController.dismiss(animated: true)
		}
		
		let navigationController = UINavigationController()
		navigationController.viewControllers = [myBestScoresViewController]
		navigationController.view.backgroundColor = UIColor.clear
		
		self.reportCardViewController.present(navigationController, animated: true, completion: nil)
		
		self.reportCardDataProvider.retrieveAthleteScores(identifier: "\(userID)") { (allExercisesResult: ReportCardExerciseScores?, errorMessage: String?) in
			DispatchQueue.main.async {
				myBestScoresViewController.exerciseScores = allExercisesResult
			}
		}
	}
	
	func moveToChallenges() {
		let vc = self.challengesCoordinator.rootViewController()
		vc.navigationItem.leftBarButtonItem = UIBarButtonItem(image: Asset.Assets.xIcon.image, style: .plain, target: self, action: #selector(self.closeButtonTapped(sender:)))
		let navigationController = UINavigationController(rootViewController: vc)
		self.reportCardViewController.present(navigationController, animated: true, completion: nil)
	}
	
	private func shareReportCardOnFacebook(reportCardImage: Image) {
		let shareReportCardActivityViewController = UIActivityViewController(activityItems: [reportCardImage], applicationActivities: nil)
		self.reportCardViewController.present(shareReportCardActivityViewController, animated: true, completion: nil)
	}
	
	
	@IBAction func closeButtonTapped(sender: Any) {
		self.reportCardViewController.dismiss(animated: true, completion: nil)
	}
}


struct MyScores: MyScoresProviding {
	
	var isPersonal: Bool
	
	let myScoresAllExerciseResult: ReportCardExerciseScores
	private let weightScores: [ReportCardExerciseWeightScores]		// This exists solely to reduce duplicated code when generating 'ScoreViewData'.
	
	
	init(isPersonal: Bool, myScoresAllExerciseResult: ReportCardExerciseScores) {
		self.isPersonal = isPersonal
		self.myScoresAllExerciseResult = myScoresAllExerciseResult
		self.weightScores = [myScoresAllExerciseResult.benchPress, myScoresAllExerciseResult.deadlift, myScoresAllExerciseResult.squat, myScoresAllExerciseResult.militaryPress]
	}
	
	
	func numberOfSections() -> Int {
		return 6
	}
	
	func numberOfRows(for section: Int) -> Int {
		switch section {
		case 0, 1, 2, 3:
			return 4
		case 4:
			return 3
		case 5:
			return 2
		default:
			return 0
		}
	}
	
	
	func exercise(for section: Int) -> ExerciseInfo {
		switch section {
		case 0:
			return ExerciseInfo(image: Asset.ReportCard.scoreHeaderBenchPress.image, title: "Bench Press", isWeightLifting: true)
		case 1:
			return ExerciseInfo(image: Asset.ReportCard.scoreHeaderDeadlift.image, title: "Deadlift", isWeightLifting: true)
		case 2:
			return ExerciseInfo(image: Asset.ReportCard.scoreHeaderSquat.image, title: "Squat", isWeightLifting: true)
		case 3:
			return ExerciseInfo(image: Asset.ReportCard.scoreHeaderMilitaryPress.image, title: "Military Press", isWeightLifting: true)
		case 4:
			return ExerciseInfo(image: Asset.ReportCard.scoreHeaderMileRun.image, title: "Mile Run", isWeightLifting: false)
		case 5:
			return ExerciseInfo(image: Asset.ReportCard.scoreHeaderFortyYardDash.image, title: "40 Yard Dash", isWeightLifting: false)
		default:
			fatalError()
		}
	}
	
	func score(for indexPath: IndexPath) -> ExerciseScorePersonalCellViewModel {
		let dateFormatter = DateFormatter.displayScoreResultsDateFormatter()
		
		switch indexPath.section {
		case 0, 1, 2, 3:
			switch indexPath.row {
			case 0:
				if let staminaDate = self.weightScores[indexPath.section].stamina.date, let staminaScore = self.weightScores[indexPath.section].stamina.score {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Stamina", dateDisplay: dateFormatter.string(from: staminaDate), scoreDisplay: "\(staminaScore)", videoStatusImage: self.weightScores[indexPath.section].stamina.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Stamina", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			case 1:
				if let enduranceDate = self.weightScores[indexPath.section].endurance.date, let enduranceScore = self.weightScores[indexPath.section].endurance.score {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Endurance", dateDisplay: dateFormatter.string(from: enduranceDate), scoreDisplay: "\(enduranceScore)", videoStatusImage: self.weightScores[indexPath.section].endurance.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Endurance", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			case 2:
				if let strengthDate = self.weightScores[indexPath.section].strength.date, let strengthScore = self.weightScores[indexPath.section].strength.score {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Strength", dateDisplay: dateFormatter.string(from: strengthDate), scoreDisplay: "\(strengthScore)", videoStatusImage: self.weightScores[indexPath.section].strength.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Strength", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			case 3:
				if let powerDate = self.weightScores[indexPath.section].power.date, let powerScore = self.weightScores[indexPath.section].power.score {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Power", dateDisplay: dateFormatter.string(from: powerDate), scoreDisplay: "\(powerScore)", videoStatusImage: self.weightScores[indexPath.section].power.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Power", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			default:
				fatalError()
			}
		case 4:
			switch indexPath.row {
			case 0:
				if let trackDate = self.myScoresAllExerciseResult.mileRun.trackRunning.date, let score = self.myScoresAllExerciseResult.mileRun.trackRunning.score, let trackScore = FormatMillisecondsForDisplay.convertScoreForDisplayMileRun(score: "\(score)") {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Track Running", dateDisplay: dateFormatter.string(from: trackDate), scoreDisplay: "\(trackScore)", videoStatusImage: self.myScoresAllExerciseResult.mileRun.trackRunning.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Track Running", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			case 1:
				if let outdoorDate = self.myScoresAllExerciseResult.mileRun.outdoor.date, let score = self.myScoresAllExerciseResult.mileRun.outdoor.score, let outdoorScore = FormatMillisecondsForDisplay.convertScoreForDisplayMileRun(score: "\(score)") {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Outdoor", dateDisplay: dateFormatter.string(from: outdoorDate), scoreDisplay: "\(outdoorScore)", videoStatusImage: self.myScoresAllExerciseResult.mileRun.outdoor.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Outdoor", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			case 2:
				if let treadmillDate = self.myScoresAllExerciseResult.mileRun.treadmill.date, let score = self.myScoresAllExerciseResult.mileRun.treadmill.score, let treadmillScore = FormatMillisecondsForDisplay.convertScoreForDisplayMileRun(score: "\(score)") {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Treadmill", dateDisplay: dateFormatter.string(from: treadmillDate), scoreDisplay: "\(treadmillScore)", videoStatusImage: self.myScoresAllExerciseResult.mileRun.treadmill.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Treadmill", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			default:
				fatalError()
			}
		case 5:
			switch indexPath.row {
			case 0:
				if let selfTimedDate = self.myScoresAllExerciseResult.fortyYardDash.selfTimed.date, let score = self.myScoresAllExerciseResult.fortyYardDash.selfTimed.score, let selfTimedScore = FormatMillisecondsForDisplay.convertScoreForDisplayFortyYardDash(score: "\(score)") {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Self Timed", dateDisplay: dateFormatter.string(from: selfTimedDate), scoreDisplay: "\(selfTimedScore)", videoStatusImage: self.myScoresAllExerciseResult.fortyYardDash.selfTimed.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Self Timed", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			case 1:
				if let cuedTimeDate = self.myScoresAllExerciseResult.fortyYardDash.cuedTime.date, let score = self.myScoresAllExerciseResult.fortyYardDash.cuedTime.score, let cuedTimeScore = FormatMillisecondsForDisplay.convertScoreForDisplayFortyYardDash(score: "\(score)") {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Cued Time", dateDisplay: dateFormatter.string(from: cuedTimeDate), scoreDisplay: "\(cuedTimeScore)", videoStatusImage: self.myScoresAllExerciseResult.fortyYardDash.cuedTime.video.statusImage)
				} else {
					return ExerciseScorePersonalCellViewModel(exerciseSubCategoryName: "Cued Time", dateDisplay: nil, scoreDisplay: nil, videoStatusImage: nil)
				}
			default:
				fatalError()
			}
		default:
			fatalError()
		}
	}
}


extension VideoStatus {
	
	var statusImage: UIImage {
		get {
			switch self {
			case .Reviewing:
				return Asset.Assets.VideoStatus.reviewingIcon.image
			case .Approved:
				return Asset.Assets.VideoStatus.approveIcon.image
			case .Declined:
				return Asset.Assets.VideoStatus.declinedIcon.image
			case .NoVideo:
				return Asset.Assets.VideoStatus.novideoIcon.image
			}
		}
	}
}


struct MileRunResult {
	let trackDate: Date?
	let trackScore: String?
	let trackVideoStatus: VideoStatus?
	let outdoorDate: Date?
	let outdoorScore: String?
	let outdoorVideoStatus: VideoStatus?
	let treadmillDate: Date?
	let treadmillScore: String?
	let treadmillVideoStatus: VideoStatus?
}


struct FortyYardDashResult {
	let selfTimedDate: Date?
	let selfTimedScore: String?
	let selfTimedVideoStatus: VideoStatus?
	let cuedTimeDate: Date?
	let cuedTimeScore: String?
	let cuedTimeVideoStatus: VideoStatus?
}


struct WeightLiftingResult {
	let staminaDate: Date?
	let staminaScore: String?
	let staminaVideoStatus: VideoStatus?
	let enduranceDate: Date?
	let enduranceScore: String?
	let enduranceVideoStatus: VideoStatus?
	let strengthDate: Date?
	let strengthScore: String?
	let strengthVideoStatus: VideoStatus?
	let powerDate: Date?
	let powerScore: String?
	let powerVideoStatus: VideoStatus?
}

