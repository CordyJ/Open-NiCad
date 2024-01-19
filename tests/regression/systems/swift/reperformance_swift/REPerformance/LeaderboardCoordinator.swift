//
//  LeaderboardCoordinator.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-31.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView
import GoogleMaps


enum LeaderboardPresentationStyle: Int {
	case push
	case present
}


class LeaderboardCoordinator: NSObject {
	
	let navigationController: UINavigationController = UINavigationController()
	let leaderboardDataProvider: LeaderboardDataProvider = LeaderboardDataProvider()
	var leaderboardInitialViewController: LeaderboardInitialViewController
	
	
	override init() {
		self.leaderboardInitialViewController = StoryboardScene.Leaderboard.leaderboardInitialVC.instantiate()
		self.leaderboardInitialViewController.tabBarItem = UITabBarItem(title: L10n.leaderboardTabBarItemTitle, image: #imageLiteral(resourceName: "TabBar_Leaderboard"), tag: 0)
		self.navigationController.setViewControllers([self.leaderboardInitialViewController], animated: true)
		
		super.init()
		
		self.start()
	}
	
	func tabBarViewController() -> UIViewController{
		return self.navigationController
	}
	
	func start() {
		self.moveToLeaderboardInitialVC()
	}
	
	func moveToLeaderboardInitialVC() {
		self.leaderboardInitialViewController.compareToOthers = {
			self.startGlobal(presentingViewController: self.navigationController)
		}
		
		self.leaderboardInitialViewController.compareWithYourGym = { [unowned self] in
			self.startGym()
		}
	}
	
	public func startGlobal(presentingViewController viewController: UIViewController) {
		if SubscriptionService.shared.isActive {
			self.moveToLeaderboard(presentingViewController: viewController)
		}
		else {
			SubscriptionService.checkIsInConferenceMode(completion: { (isConferenceMode) in
				if isConferenceMode {
					self.moveToLeaderboard(presentingViewController: viewController)
				}
				else {
					self.moveToLearnAboutPro(presentingViewController: viewController)
				}
			})
		}
	}
	
	fileprivate func moveToLearnAboutPro(presentingViewController viewController: UIViewController) {
		let learnAboutProViewController = StoryboardScene.Leaderboard.learnAboutProVC.instantiate()
		learnAboutProViewController.title = "Upgrade to Pro"
		learnAboutProViewController.navigationItem.leftBarButtonItem = UIBarButtonItem(title: L10n.doneBarItemTitle, style: .plain, target: self, action: #selector(dismissLearnAboutPro))
		learnAboutProViewController.dismissWithSuccessfulPurchase = {
			self.dismissLearnAboutPro()
			self.startGlobal(presentingViewController: viewController)
		}
		
		let enclosingNav = UINavigationController(rootViewController: learnAboutProViewController)
		viewController.present(enclosingNav, animated: true, completion: nil)
	}
	
	fileprivate func moveToLeaderboard(presentingViewController viewController: UIViewController) {
		let leaderboardViewController  = StoryboardScene.Leaderboard.leaderboardVC.instantiate()
		let enclosingNav = UINavigationController(rootViewController: leaderboardViewController)
		
		leaderboardViewController.dismiss = {
			leaderboardViewController.dismiss(animated: true, completion: nil)
		}
		
		leaderboardViewController.willAppear = {
			if let neverSeen = UserDefaults.standard.leaderboardNeverSeen, neverSeen == true {
				UIAlertController.showAlert(nil, message: L10n.leaderboardFirstTimeView, inViewController: leaderboardViewController)
				UserDefaults.standard.leaderboardNeverSeen = false
			}
		}
		
		var leaderboardGroup: LeaderboardGroup = .Everyone
		var exerciseCategory: ExerciseCategory?
		var exerciseTestFormat: ExerciseTestFormat?
		var filterAge: Bool = false
		let refreshLeaderboardContent = { (completion: (()->())?) in
			leaderboardViewController.showLoadingIndicator(true)
			self.leaderboardDataProvider.retreiveLeaderboard(group: leaderboardGroup, filterAge: filterAge, exercise: exerciseCategory, testFormat: exerciseTestFormat) { (leaderboard, errorMessage) in
				leaderboardViewController.showLoadingIndicator(false)
				
				let errorableLeaderboardViewModel: ErrorableLeaderboardViewModel
				if let leaderboard = leaderboard {
					let leaderboardViewModel = LeaderboardViewModel(leaderboard: leaderboard, globalLeaderboard: false, exerciseCategory: exerciseCategory, exerciseTestFormat: exerciseTestFormat, filteredByAge: filterAge)
					errorableLeaderboardViewModel = .leaderboard(viewModel: leaderboardViewModel)
				}
				else {
					errorableLeaderboardViewModel = .error(message: errorMessage ?? L10n.leaderboardDefaultErrorMessage)
				}
				leaderboardViewController.errorableLeaderboardViewModel = errorableLeaderboardViewModel
				leaderboardViewController.setUpView()
				leaderboardViewController.reloadView()
				
				leaderboardViewController.selectedAthlete = { (athlete) in
					guard athlete.isPublic == true else {
						return
					}
					
					self.showAthleteReportCard(viewController: leaderboardViewController, athlete: athlete)
				}
			}
			
			completion?()
		}
		
		leaderboardViewController.segmentChanged = { (group) in
			leaderboardGroup = group
			refreshLeaderboardContent() { }
		}
		
		leaderboardViewController.byTest = {
			self.moveToFilterByTest(presentingViewController: leaderboardViewController, selection: { (category, testFormat) in
				exerciseCategory = category
				exerciseTestFormat = testFormat
				refreshLeaderboardContent() { }
			})
		}
		
		leaderboardViewController.byAge = {
			filterAge.toggle()
			refreshLeaderboardContent() { }
		}
		
		
		refreshLeaderboardContent() {
			viewController.present(enclosingNav, animated: true, completion: nil)
		}
	}
	
	fileprivate func moveToFilterByTest(presentingViewController: UIViewController, selection: @escaping (ExerciseCategory, ExerciseTestFormat)->()) {
		let leaderboardSelectionViewController = StoryboardScene.Leaderboard.leaderboardSelectionVC.instantiate()
		leaderboardSelectionViewController.setUpView()
		leaderboardSelectionViewController.cancel = {
			leaderboardSelectionViewController.dismiss(animated: true, completion: nil)
		}
		leaderboardSelectionViewController.selectionMade = { (exerciseCategory, exerciseTestFormat) in
			if let exerciseCategory = exerciseCategory, let exerciseTestFormat = exerciseTestFormat {
				selection(exerciseCategory, exerciseTestFormat)
			}
			
			leaderboardSelectionViewController.dismiss(animated: true, completion: nil)
		}
		
		let enclosingNav = UINavigationController(rootViewController: leaderboardSelectionViewController)
		presentingViewController.present(enclosingNav, animated: true, completion: nil)
	}
	
	
	@IBAction func dismissLearnAboutPro() {
		navigationController.dismiss(animated: true, completion: nil)
	}
	
	
	//Gym Leaderboards
	
	private func startGym() {
		self.startGymLeaderboard()
	}
	
	private func moveToChooseAGym() {
		self.presentChooseAGym(from: self.navigationController)
	}
	
	func presentChooseAGym(from viewController: UIViewController) {
		let chooseAGymVC = StoryboardScene.Leaderboard.chooseAGymVC.instantiate()
		if let currentGymPlaceID = UserDefaults.standard.currentGymPlaceID, currentGymPlaceID != "" {
			chooseAGymVC.title = L10n.chooseAGymTitleChange
		}
		else {
			chooseAGymVC.title = L10n.chooseAGymTitleFind
		}
		
		chooseAGymVC.didLoad = {
			NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		}
		
		let googleDataProvider = GoogleDataProvider()
		chooseAGymVC.findNearbyGyms = { (userLocation, pageToken) in
			googleDataProvider.findNearbyGyms(location: userLocation, pageToken: pageToken, completion: { (REPPlaces, nextPageToken, attributions, error) in
				if let error = error {
					print("Error searching: \(error)")
					NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
				}
				else {
					if let repPlaces = REPPlaces {
						var placesToAdd:[(REPPlace, GMSMarker?)] = []
						for place in repPlaces {
							let placeToAdd:(REPPlace, GMSMarker?) = (place, nil)
							placesToAdd.append(placeToAdd)
						}
						
						chooseAGymVC.nearbyGyms = chooseAGymVC.nearbyGyms + placesToAdd
						chooseAGymVC.showGyms()
					}
					
					if let attributions = attributions, attributions.count > 0 {
						if chooseAGymVC.attributions == nil || chooseAGymVC.attributions?.count == 0 {
							chooseAGymVC.attributions = attributions
						}
						else {
							chooseAGymVC.attributions = chooseAGymVC.attributions! + attributions
						}
					}
					
					chooseAGymVC.loadAttributions()
					
					if let nextPageToken = nextPageToken, nextPageToken != "" {
						//Google states in the API document that it takes a few seconds for the page token to become valid so need to delay here to avoid having an invalid request.
						//https://developers.google.com/places/web-service/search
						DispatchQueue.main.asyncAfter(deadline: .now() + 3.0, execute: {
							chooseAGymVC.searchForNearbyGyms(pageToken: nextPageToken)
						})
					}
					else {
						NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
					}
				}
			})
		}
		
		chooseAGymVC.selectGym = { [unowned self] (repPlace) in
			NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
			self.leaderboardDataProvider.submitGym(placeID: repPlace.placeID, name: repPlace.name, region: repPlace.vicinity, completion: { (isSuccess, errorMessage) in
				NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
				
				if isSuccess == true {
					UserDefaults.standard.currentGymPlaceID = repPlace.placeID
					chooseAGymVC.dismiss(animated: true, completion: nil)
				}
				else {
					UIAlertController.showAlert(nil, message: errorMessage, inViewController: chooseAGymVC)
				}
			})
		}
		
		let enclosingNav = UINavigationController(rootViewController: chooseAGymVC)
		enclosingNav.navigationBar.setHalfLeaderboardGradientBackground()
		
		viewController.present(enclosingNav, animated: true, completion: nil)
	}
	
	private func startGymLeaderboard() {
		let leaderboardSelectionViewController = StoryboardScene.Leaderboard.leaderboardSelectionVC.instantiate()
		leaderboardSelectionViewController.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
		leaderboardSelectionViewController.isGymType = true
		leaderboardSelectionViewController.setUpView()
		
		leaderboardSelectionViewController.selectionMade = { [weak navigationController, weak leaderboardDataProvider] (exerciseCategory, exerciseTestFormat) in
			guard let exerciseCategory = exerciseCategory, let exerciseTestFormat = exerciseTestFormat else {
				return
			}
			
			let gymLeaderboardViewController = StoryboardScene.Leaderboard.gymLeaderboardVC.instantiate()
			gymLeaderboardViewController.showLoadingIndicator(true)
			
			leaderboardDataProvider?.retreiveGymLeaderboard(exercise: exerciseCategory, testFormat: exerciseTestFormat, completion: { (leaderboard, errorMessage) in
				gymLeaderboardViewController.showLoadingIndicator(false)
				
				let errorableLeaderboardViewModel: ErrorableLeaderboardViewModel
				if let leaderboard = leaderboard {
					let leaderboardViewModel = LeaderboardViewModel(leaderboard: leaderboard, globalLeaderboard: false, exerciseCategory: exerciseCategory, exerciseTestFormat: exerciseTestFormat, filteredByAge: false)
					errorableLeaderboardViewModel = .leaderboard(viewModel: leaderboardViewModel)
				}
				else {
					errorableLeaderboardViewModel = .error(message: errorMessage ?? L10n.leaderboardDefaultErrorMessage)
				}
				gymLeaderboardViewController.errorableLeaderboardViewModel = errorableLeaderboardViewModel
				gymLeaderboardViewController.reloadView()
				
				gymLeaderboardViewController.selectedAthlete = { (athlete) in
					guard athlete.isPublic == true else {
						return
					}
					
					self.showAthleteReportCard(viewController: gymLeaderboardViewController, athlete: athlete)
				}
				
				navigationController?.pushViewController(gymLeaderboardViewController, animated: true)
			})
		}
		
		leaderboardSelectionViewController.changeGym = {
			self.moveToChooseAGym()
		}
		
		if UserDefaults.standard.currentGymPlaceID == nil || UserDefaults.standard.currentGymPlaceID == "" {
			self.moveToChooseAGym()
		}
		
		self.navigationController.pushViewController(leaderboardSelectionViewController, animated: true)
	}
	
	fileprivate func showAthleteReportCard(viewController presentingViewController: UIViewController, athlete: Athlete) {
		assert(athlete.isPublic == true)
		
		let coordinator = ReportCardCoordinator(athlete: athlete)
		let reportCardViewController = coordinator.reportCardViewController
		let navigationController = UINavigationController.init(rootViewController: reportCardViewController)
		reportCardViewController.navigationItem.leftBarButtonItem = BlockBarButtonItem(barButtonSystemItem: .done) {
			presentingViewController.dismiss(animated: true)
		}
		presentingViewController.present(navigationController, animated: true)
	}
}
