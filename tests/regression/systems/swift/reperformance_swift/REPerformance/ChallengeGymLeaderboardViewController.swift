//
//  ChallengeGymLeaderboardViewController.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2018-06-11.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ChallengeGymLeaderboardViewController: UIViewController {
	
	@IBOutlet fileprivate weak var leaderboardTableView: UITableView! {
		didSet {
			self.leaderboardTableView.backgroundColor = UIColor.clear
		}
	}
	
	var challenge: Challenge?
	var selectedAthlete: ((Athlete)->())?
	var athletes: [Athlete]? {
		didSet {
			self.leaderboardTableView.reloadData()
		}
	}
	
	
	override func viewDidAppear(_ animated: Bool) {
		super.viewDidAppear(animated)
		
		REPAnalytics.trackScreenWithName(screenName: ScreenName.Challenges.Leaderboard(self.challenge!.name), className: String(describing: self))
	}
}


extension ChallengeGymLeaderboardViewController: UITableViewDataSource, UITableViewDelegate {
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		return self.athletes?.count ?? 0
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		let cell = tableView.dequeueReusableCell(withIdentifier: "Challenge Gym Leaderboard Ranking Cell Identifier", for: indexPath) as! ChallengeGymLeaderboardTableViewCell
		let challengeLeaderboard = self.athletes![indexPath.row]
		
		cell.rank = challengeLeaderboard.rank
		cell.name = challengeLeaderboard.name
		cell.score = challengeLeaderboard.score
        cell.profileImageURL = FacebookImage.imageURLWithFacebookID(challengeLeaderboard.facebookIdentifier)
		cell.isPublic = challengeLeaderboard.isPublic
        
		return cell
	}
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        
        let athlete = self.athletes![indexPath.row]
        self.selectedAthlete?(athlete)
        
    }
}
