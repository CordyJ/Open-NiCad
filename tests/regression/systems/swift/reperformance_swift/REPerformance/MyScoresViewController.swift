//
//  MyScoresViewController.swift
//  REPerformance
//
//  Created by Francis Chary on 2017-05-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


struct ExerciseInfo {
	let image: Image
	let title: String
	let isWeightLifting: Bool
}


protocol MyScoresProviding {
	var isPersonal: Bool { get }
	
	func numberOfSections() -> Int
	func numberOfRows(for section: Int) -> Int
	func exercise(for: Int) -> ExerciseInfo
	func score(for: IndexPath) -> ExerciseScorePersonalCellViewModel
}


class MyScoresViewController: UIViewController {
	
	@IBOutlet var scoresTableView: UITableView?
	@IBOutlet var videoStatusLegendView: UIView?
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}
	
	var viewData: MyScoresProviding?
	
	var showVideoStatusLegend: Bool = false
	
	
	override func viewWillAppear(_ animated: Bool) {
		super.viewWillAppear(animated)
		
		self.videoStatusLegendView?.isHidden = self.showVideoStatusLegend == false
	}
	
	override func viewDidAppear(_ animated: Bool) {
		super.viewDidAppear(animated)
		
		REPAnalytics.trackScreenWithName(screenName: ScreenName.MyScores, className: String(describing: self))
	}
}


extension MyScoresViewController: UITableViewDataSource, UITableViewDelegate {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		guard let viewModel = self.viewData else {
			return 0
		}
		
		return viewModel.numberOfSections() + 1
	}
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		guard let viewModel = self.viewData else {
			return 0
		}
		
		if section == 0 {
			return (self.showVideoStatusLegend == true ? 1 : 0)
		}
		else {
			let adjustedSection = section - 1
			return viewModel.numberOfRows(for: adjustedSection)
		}
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		if indexPath.section == 0 {
			return tableView.dequeueReusableCell(withIdentifier: "Video Status Legend Cell Identifier", for: indexPath)
		}
		
		var adjustedIndexPath = indexPath
		adjustedIndexPath.section -= 1
		let viewData = self.viewData!
		let score = viewData.score(for: adjustedIndexPath)
		let cell = tableView.dequeueReusableCell(withIdentifier: "Score Cell Identifier", for: indexPath) as! ExerciseScorePersonalTableViewCell
		
		cell.configure(with: score)
		
		return cell
	}
	
	func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
		if section == 0 {
			return nil
		}
		
		let adjustedSection = section - 1
		let viewData = self.viewData!
		let exercise = viewData.exercise(for: adjustedSection)
		let header = tableView.dequeueReusableCell(withIdentifier: "Score Section Header") as! MyScoreSectionHeaderTableViewCell
		
		header.configure(with: exercise)
		
		return header
	}
	
	func tableView(_ tableView: UITableView, heightForHeaderInSection section: Int) -> CGFloat {
		if section == 0 {
			return 0
		}
		
		return 111
	}
}
