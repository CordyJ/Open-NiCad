//
//  ChallengesCoordinator.swift
//  REPerformance
//
//  Created by Alan Yeung on 2018-05-25.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import Foundation
import UIKit
import NVActivityIndicatorView


class ChallengesCoordinator {
	
	let challengesViewController: ChallengesViewController
	let challengeDataProvider = ChallengeDataProvider()
	
	
	init() {
		self.challengesViewController = StoryboardScene.Challenges.challengesVC.instantiate()
		self.challengesViewController.title = L10n.challengeTitle
		self.challengesViewController.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
		self.challengesViewController.selectedChallenge = { [unowned self] (challenge) in
			self.moveToChallengeGyms(challenge)
		}
		
		self.challengesViewController.challengesWillAppear = { [unowned self] in
			NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
			self.challengeDataProvider.retreiveChallenges() { (retreiveChallengesResult) in
				NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
				
				switch retreiveChallengesResult {
				case .success(let challenges):
					self.challengesViewController.challenges = challenges
				case .failure(_):
					self.challengesViewController.challenges = []
				}
			}
		}
	}
	
	
	func rootViewController() -> UIViewController {
		return self.challengesViewController
	}
	
	private func moveToChallengeGyms(_ challenge: Challenge) {
		let challengeGymsViewController = StoryboardScene.Challenges.challengeGymsVC.instantiate()
		challengeGymsViewController.title = challenge.type == .gym ? L10n.challengeGymLeaderboardTitle : L10n.challengeLeaderboardTitle
		challengeGymsViewController.navigationItem.backBarButtonItem = UIBarButtonItem(title: "", style: .plain, target: nil, action: nil)
		challengeGymsViewController.challenge = challenge
		challengeGymsViewController.challengeAction = { [unowned self] in
			guard let challengeToChange = challengeGymsViewController.challenge else {
				return
			}
			
			let changeChallengeState = {
				NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
				self.challengeDataProvider.submitChallengeAction(challenge: challengeToChange, completion: { (submitChallengeActionResult) in
					NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
					
					if case .success(_) = submitChallengeActionResult {
						var newChallenge = challengeToChange
						newChallenge.hasJoined = !challengeToChange.hasJoined
						challengeGymsViewController.challenge = newChallenge
						challengeGymsViewController.showChallengeJoinedAlert(challenge: newChallenge)
						REPAnalytics.trackEvent(name: EventAnalytics.Challenges.ChallengeType(newChallenge), parameters: ["Action" : EventAnalytics.Challenges.Join(newChallenge), "Label" : newChallenge.name])
					}
				})
			}
			
			if challengeToChange.hasJoined {
				let promptAlertController = UIAlertController(title: nil, message: L10n.challengeLeavePromptMessage, preferredStyle: .alert)
				promptAlertController.addAction(UIAlertAction(title: L10n.cancel, style: .default, handler: nil))
				promptAlertController.addAction(UIAlertAction(title: L10n.confirm, style: .default, handler: { (_) in
					changeChallengeState()
				}))
				challengeGymsViewController.present(promptAlertController, animated: true, completion: nil)
			}
			else {
				changeChallengeState()
			}
		}
		challengeGymsViewController.challengeInfo = { [unowned self] in
			self.moveToChallengeDetails(challenge)
		}
		challengeGymsViewController.viewLeaderboard = { [unowned self] (gym) in
			self.moveToGymLeaderboard(challenge, gym: gym)
		}
		challengeGymsViewController.changeGym = {
			let leaderboardCoordinator = LeaderboardCoordinator()
			leaderboardCoordinator.presentChooseAGym(from: challengeGymsViewController)
		}
		challengeGymsViewController.selectedAthlete = { (athlete) in
			guard let isPublic = athlete.isPublic, isPublic == true else {
				return
			}
			
			let coordinator = ReportCardCoordinator(athlete: athlete)
			let reportCardViewController = coordinator.reportCardViewController
			let navigationController = UINavigationController.init(rootViewController: reportCardViewController)
			reportCardViewController.navigationItem.leftBarButtonItem = BlockBarButtonItem(barButtonSystemItem: .done) {
				challengeGymsViewController.dismiss(animated: true)
			}
			challengeGymsViewController.present(navigationController, animated: true)
		}
		
		self.challengesViewController.navigationController?.pushViewController(challengeGymsViewController, animated: true)
		
		if challenge.type == .personal {
			self.challengeDataProvider.retreiveLeaderboard(challenge: challenge) { (retreiveLeaderboardResult) in
				switch retreiveLeaderboardResult {
				case .success(let athletes):
					challengeGymsViewController.athletes = athletes
				case .failure(_):
					challengeGymsViewController.athletes = []
				}
			}
		}
	}
	
	private func moveToChallengeDetails(_ challenge: Challenge) {
		let challengeDetailViewController = StoryboardScene.Challenges.challengeDetailVC.instantiate()
		challengeDetailViewController.title = "Details"
		challengeDetailViewController.challenge = challenge
		
		self.challengesViewController.navigationController?.pushViewController(challengeDetailViewController, animated: true)
	}
	
	private func moveToGymLeaderboard(_ challenge: Challenge, gym: Gym) {
		let challengeGymLeaderboardViewController = StoryboardScene.Challenges.challengeGymLeaderboardViewController.instantiate()
		challengeGymLeaderboardViewController.navigationItem.title = gym.name
		challengeGymLeaderboardViewController.challenge = challenge
        challengeGymLeaderboardViewController.selectedAthlete = { (athlete) in
            guard let isPublic = athlete.isPublic, isPublic == true else {
                return
            }
            
            let coordinator = ReportCardCoordinator(athlete: athlete)
            let reportCardViewController = coordinator.reportCardViewController
            let navigationController = UINavigationController.init(rootViewController: reportCardViewController)
            reportCardViewController.navigationItem.leftBarButtonItem = BlockBarButtonItem(barButtonSystemItem: .done) {
                challengeGymLeaderboardViewController.dismiss(animated: true)
            }
            challengeGymLeaderboardViewController.present(navigationController, animated: true)
        }
		
		self.challengesViewController.navigationController?.pushViewController(challengeGymLeaderboardViewController, animated: true)
		
		NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		self.challengeDataProvider.retreiveLeaderboard(challenge: challenge, gym: gym) { (retreiveLeaderboardResult) in
			NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
			
			switch retreiveLeaderboardResult {
			case .success(let athletes):
				challengeGymLeaderboardViewController.athletes = athletes
			case .failure(_):
				challengeGymLeaderboardViewController.athletes = []
			}
		}
	}
}
