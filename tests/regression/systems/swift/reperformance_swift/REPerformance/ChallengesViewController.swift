//
//  ChallengesListViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2018-05-25.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ChallengesViewController: UIViewController {
	
	@IBOutlet private var tableView: UITableView? {
		didSet {
			self.tableView?.estimatedRowHeight = 85
			self.tableView?.rowHeight = UITableView.automaticDimension
			self.tableView?.backgroundColor = UIColor.clear
			self.tableView?.tableFooterView = UIView()
		}
	}
	
	var challenges: [Challenge]? {
		didSet {
			self.tableView?.reloadData()
		}
	}
	
	var challengesWillAppear: (()->())?
	var selectedChallenge: ((Challenge)->())?
	
	
	override func viewWillAppear(_ animated: Bool) {
		super.viewWillAppear(animated)
		
		self.challengesWillAppear?()
	}
}

extension ChallengesViewController: UITableViewDataSource, UITableViewDelegate {
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		return challenges?.count ?? 0
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		guard let cell = tableView.dequeueReusableCell(withIdentifier: Constants.Challenges.ChallengesCellIdentifier, for: indexPath) as? ChallengesTableViewCell, let challenge = self.challenges?[indexPath.row] else {
			fatalError()
		}
		
		cell.configure(challenge: challenge)
		
		return cell
	}
	
	func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
		tableView.deselectRow(at: indexPath, animated: true)
		
		guard let challenge = self.challenges?[indexPath.row] else {
			return
		}
		
		self.selectedChallenge?(challenge)
	}
}
